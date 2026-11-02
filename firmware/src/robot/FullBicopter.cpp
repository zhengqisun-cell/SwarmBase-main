/**
 * @file FullBicopter.cpp
 * @author Edward Jeff
 * @brief Implementation of FullBicopter.h
 * @version 0.1
 * @date 2024-03-01
 * 
 * @copyright Copyright (c) 2024
 * 
 */


#include "FullBicopter.h"


FullBicopter::FullBicopter(){
    
}

void FullBicopter::startup() {
    RawBicopter::startup(); // Initializes the servos and motors
    sensorsuite.startup(); // Initializes the Nicla and the other sensors
    float senses[MAX_SENSORS];
    FullBicopter::sense(senses);
}


int FullBicopter::sense(float sensors[MAX_SENSORS]) {
    sensorsuite.update();
    int numSenses = 0;
    //(temperature, altitude, velocityAltitude, roll, pitch, yaw, rollrate, pitchrate, yawrate, batteryVoltage)

    float* sensorsValues = sensorsuite.readValues(numSenses);
    for (int i = 0; i < numSenses; i++) {
        sensors[i] = sensorsValues[i];
    }
    return numSenses; 
}

// Controls [Ready, Fx, height/Fz, Tz, Tx]
// Heading rate. The IMU is mounted ~88 deg rolled, so gyro z (sensors[8]) is the lateral
// swing rate, not the heading rate (log 2026-10-29: correlation -0.06 with the heading).
// The yaw-angle rate from the ZYX Euler kinematics, psi_dot = (gy sin(roll) + gz cos(roll))
// / cos(pitch), reduces to gz for an upright IMU and gives the heading rate for any mount.
// Computed every loop, Off included, so telemetry and a bench check can see it.
void FullBicopter::updateYawRate(float sensors[MAX_SENSORS]) {
    int axis = PDterms.yawRateAxis;
    if (axis < 6 || axis > 8) axis = 8;
    float yaw_rate = sensors[axis] * PDterms.yawRateSign;
    if (PDterms.yawRateEuler) {
        float cp = cos(sensors[4]);
        if (fabsf(cp) < 0.2f) cp = copysignf(0.2f, cp == 0.f ? 1.f : cp);
        yaw_rate = (sensors[7] * sin(sensors[3]) + sensors[8] * cos(sensors[3])) / cp;
    }
    last_yaw_rate = yaw_rate;
}

void FullBicopter::control(float sensors[MAX_SENSORS], float controls[], int size) {
    float outputs[5];
    trackPitchZero(sensors, controls[0] == 0);
    updateYawRate(sensors);

    // IMU stale (no change in the pitch sample for 0.7 s: the BNO stream has stopped or the robot
    // was reset without a power cycle): behave as Off rather than fly on frozen attitude.
    imu_stale = millis() - last_pitch_change_ms > 700;

    // When control[0] == 0, the robot stops its motors and sets servos to facing vertically upward
    if (controls[0] == 0 || (imu_stale && PDterms.imuGuard)) {
        outputs[0] = 0;
        outputs[1] = 0;
        // Checking for full rotations and adjusting t1 and t2
        float t1 = adjustAngle(PI/2);
        float t2 = adjustAngle(PI/2);

        // Converting values to a more stable form
        // float servoBottom = 90.0f - PDterms.servoRange/2.0f; // bottom limit of servo in degrees
        // float servoTop = 90.0f + PDterms.servoRange/2.0f; // top limit of servo in degrees
        outputs[2] = clamp((t1 ) * 180.0f / PI  + PDterms.servoBeta , 0.0f,  PDterms.servoRange ) * 180.0f / PDterms.servoRange;
        outputs[3] = 180.0f -clamp((t2) * 180.0f / PI  + PDterms.servoBeta, 0.0f,  PDterms.servoRange ) * 180.0f / PDterms.servoRange;
        outputs[4] = 0;
        servo_old1 = outputs[2];
        servo_old2 = outputs[3];
        servo_history_valid = true;
        resetVerticalMode(); // servos are pointed up again

        return FullBicopter::actuate(outputs, size);
    }
    
    float feedbackControls[5];
    FullBicopter::addFeedback(sensors, controls, feedbackControls);
    
    outputs[4] = 1;
    FullBicopter::getOutputs(sensors, feedbackControls,  outputs);
    RawBicopter::actuate(outputs, size);
}

void FullBicopter::getPreferences() {
    //calls the getPreferences of the superclass object to reduce the number of getPreferences calls
    RawBicopter::getPreferences();
    sensorsuite.getPreferences();
    // Implementation for reading values from non-volatile storage (NVS)
    // must manually enter keys and default values for every variable.
    Preferences preferences; //initialize the preferences 
    preferences.begin("params", true); //true means read-only

    //value = preferences.getInt("value", default_value); //(value is an int) (default_value is manually set)
    
    // enables feedback on each vector
    PDterms.zEn = preferences.getBool("zEn", false);
    PDterms.yawEn = preferences.getBool("yawEn", false);
    PDterms.rollEn = preferences.getBool("rollEn", false);
    PDterms.rotateEn = preferences.getBool("rotateEn", false);
    PDterms.pitchEn = preferences.getBool("pitchEn", false);

    // PID terms
    PDterms.kpyaw = preferences.getFloat("kpyaw", 0.1);
    PDterms.kppyaw = preferences.getFloat("kppyaw", 0.1);
    PDterms.kdyaw = preferences.getFloat("kdyaw", 0.1);// same thing as if I said kpyawrate
    PDterms.kddyaw = preferences.getFloat("kddyaw", 0.1);
    PDterms.kiyaw = preferences.getFloat("kiyaw", 0);
    PDterms.kiyawrate = preferences.getFloat("kiyawrate", 0);

    PDterms.kpz = preferences.getFloat("kpz", 0.5);
    PDterms.kdz = preferences.getFloat("kdz", 0.5);
    PDterms.kiz = preferences.getFloat("kiz", 0);

    PDterms.kproll = preferences.getFloat("kproll", 0);
    PDterms.kdroll = preferences.getFloat("kdroll", 0);
    PDterms.kppitch = preferences.getFloat("kppitch", 0);
    PDterms.kdpitch = preferences.getFloat("kdpitch", 0);

    // Range terms for the integrals
    PDterms.z_int_low = preferences.getFloat("z_int_low", 0);
    PDterms.z_int_high = preferences.getFloat("z_int_high", 0);
    PDterms.yawRateIntRange = preferences.getFloat("yawRateIntRange", 0);

    // radius of the blimp
    PDterms.lx = preferences.getFloat("lx", .15);

    // Off by default: the stock yaw loop uses raw gyro z. Set true for the current robot, whose IMU
    // is mounted ~88 deg rolled (2026-10-30, verified in simulation; see ~/Desktop/BlimpSim).
    PDterms.yawRateEuler = preferences.getBool("yawRateEuler", false);
    // Fixed-axis alternative that does not depend on the IMU's attitude reference (which is lost
    // after a reboot without a power cycle): on this robot the IMU is mounted ~90 deg rolled and
    // gyro y (sensors[7]) is the heading rate, bench-verified 2026-10-30.
    PDterms.yawRateAxis = preferences.getInt("yawRateAxis", 8);
    PDterms.yawRateSign = preferences.getFloat("yawRateSign", 1.0f);
    // Yaw authority grows with the total thrust command (thrust is ~quadratic in command), so the
    // yaw output is scaled down above this level; 0 disables. Sim-verified 2026-10-30.
    PDterms.yawAuthRef = preferences.getFloat("yawAuthRef", 0);
    // Flight 2026-10-30 13:42: the IMU stream died in flight and the loop kept flying on frozen
    // values (a corrupt -16 rad/s yaw rate). With the guard the robot stops instead.
    // true: stop (as Off) while stale. false: keep flying degraded - rates are zeroed by the IMU
    // watchdog, the heading error is then just the stick input, pitch compensation is off.
    // Default false: ParamManager only writes a bool when it differs from getBool(key, 0), so a
    // "false" for a key that was never stored would be dropped and a true default could not be
    // switched off over the radio.
    PDterms.imuGuard = preferences.getBool("imuGuard", false);
    // Downward thrust (botZlim < 0): flipping the thrust from up to down swings both servos ~180 deg
    // through forward/backward, which turned every height wobble around Fz = 0 into a forward or
    // yaw kick (2026-10-29). The flip now needs a sustained condition (see verticalForce()), and
    // a large swing is made with the motors off: zCoastMs spin-down, then zSwingMs servo travel.
    PDterms.zDownErr = preferences.getFloat("zDownErr", 0.8f);
    PDterms.zDownOn = preferences.getFloat("zDownOn", 0.1f);
    PDterms.zDownMs = preferences.getFloat("zDownMs", 300);
    PDterms.zCoastMs = preferences.getFloat("zCoastMs", 150);
    PDterms.zSwingMs = preferences.getFloat("zSwingMs", 350);

    preferences.end();
}

void FullBicopter::addFeedback(float sensors[MAX_SENSORS], float controls[], float feedbackControls[]) {
    
    float fx = controls[1]; // Fx; the original negated this, which made forward commands fly backward (flight test 2026-10-29)
    float fz = controls[2]; // Fz/height
    float tx = controls[3]; // tx
    float tz = controls[4]; // tz
    
    int dt = 4000;
    
    // Z feedback
    z_err_valid = PDterms.zEn;
    if (PDterms.zEn) {
        z_err = controls[2] - sensors[1]; // for the up/down thrust switch in verticalForce()
        // Integral in Z
        z_integral += (controls[2] - (sensors[1])) * ((float)dt)/1000000.0f * PDterms.kiz;
        z_integral = clamp(z_integral, PDterms.z_int_low, PDterms.z_int_high);
        // Serial.println("z feedback");
        // PID in z
        fz = (controls[2] - (sensors[1]))*PDterms.kpz 
                      - (sensors[2])*PDterms.kdz + (z_integral); 
    }

    float yaw_rate = last_yaw_rate; // computed in updateYawRate() every loop, Off included

    // Yaw feedback (Cascading control format) 
    //      this means that there is a separate PID for both absolute yaw and yawrate which are combined
    //      what this basically means is that the D term for the absolute yaw is replaced with the yawrate PI
    //          the D term in yaw is equivalent to the P term in yawrate
    if (PDterms.yawEn) {
        // Serial.print("yaw feedback: ");
        // initial absolute error for the yaw
        float e_yaw = controls[4] - sensors[5]; // Tz - Yaw
        e_yaw = atan2(sin(e_yaw), cos(e_yaw));
        e_yaw = clamp(e_yaw, -PI/5, PI/5);

        // integral term for the absolute yaw
        yaw_integral += e_yaw * ((float)dt)/1000000.0f * PDterms.kiyaw;
        yaw_integral = clamp(yaw_integral, -PI/4, PI/4);
        
        // finding desired yaw rate from the absolute yaw feedback
        float yaw_desired_rate = (e_yaw  + yaw_integral);

        // getting the error in the yawrate
        float e_yawrate = yaw_desired_rate * PDterms.kpyaw - yaw_rate; // YawRate

        // integral term for the yawrate
        yawrate_integral += e_yawrate * ((float)dt)/1000000.0f * PDterms.kiyawrate;
        yawrate_integral = clamp(yawrate_integral, - PDterms.yawRateIntRange, PDterms.yawRateIntRange);

        // final result of the cascading PID controller in yaw
        tz = yaw_desired_rate * PDterms.kppyaw  + e_yawrate*PDterms.kdyaw - yaw_rate * PDterms.kddyaw  + yawrate_integral;
        
        // Serial.println(tz);
    }

    // Pitch feedback
    if (PDterms.pitchEn) { 
        // Serial.println("roll feedback");
        fx = fx - pitchTilt(sensors)*PDterms.kppitch - sensors[6] * PDterms.kdpitch; // Pitch - PitchRate
    }
    // Roll feedback
    if (PDterms.rollEn) { 
        // Serial.println("roll feedback");
        tx = tx - constrain(sensors[4]*PDterms.kproll - sensors[7] * PDterms.kdroll, -fz*PDterms.lx*.9, fz*PDterms.lx*.9); // Roll - RollRate
    }
    // Roll and pitch rotation state feedback
    if (PDterms.rotateEn) {
        // Serial.println("rotate feedback");
        float cosp = cos(sensors[4]); // Pitch
        float sinp = sin(sensors[4]); // Pitch
        float cosr = cos(sensors[3]); // Roll
        float ifx = controls[1]; // Fx
        fx = ifx*cosp + fz*sinp;
        fz = (-1*ifx*sinp + fz* cosp)/cosr;
    }
    feedbackControls[0] = fx;
    feedbackControls[1] = fz;
    feedbackControls[2] = tx;
    feedbackControls[3] = tz;
    feedbackControls[4] = 1;
    
    
}

// While Off, keep a ~1 s average of the IMU pitch; on leaving Off it becomes the zero. If the
// IMU did not change for a second (frozen after a reset), the zero is not trusted and pitch
// compensation stays off for that flight.
void FullBicopter::trackPitchZero(float sensors[MAX_SENSORS], bool off) {
    unsigned long now = millis();
    float pitch = sensors[3];
    if (pitch != last_pitch_sample) {
        last_pitch_sample = pitch;
        last_pitch_change_ms = now;
    }
    if (off) {
        if (!pitch_avg_started) {
            pitch_avg = pitch;
            pitch_avg_started = true;
        }
        float diff = atan2f(sinf(pitch - pitch_avg), cosf(pitch - pitch_avg));
        pitch_avg += diff * 0.004f; // 4 ms loop -> ~1 s time constant
        was_off = true;
    } else if (was_off) {
        was_off = false;
        pitch_zero = pitch_avg;
        pitch_zero_valid = pitch_avg_started && now - last_pitch_change_ms < 1000;
    }
}

float FullBicopter::pitchTilt(float sensors[MAX_SENSORS]) const {
    float d = sensors[3] - pitch_zero;
    return atan2f(sinf(d), cosf(d));
}

// Vertical force for the mixer. With botZlim < 0 the thrust can point down, but the servos only
// change side after the switch condition has held for zDownMs; meanwhile the force on the current
// side is clipped to zero, so height wobbles no longer swing the servos through forward/backward.
// getOutputs() makes the swing itself with the motors off.
// With the height loop on, the condition is the height error: down when the target is more than
// zDownErr below, back up within zDownErr/2. Fz itself is no use for this: its D term on the baro
// rate swings it across zero every second or two, and every flip then cost 0.5 s of thrust (sim
// 2026-11-02, height scenario: 10-12 flips per run for zDownOn 0.1-0.4; with zDownErr 0.8 none in
// hands-off hover, the remaining ones only on the sim's ~1 m climb overshoots).
float FullBicopter::verticalForce(float fz) {
    if (PDterms.botZlim >= 0) {
        resetVerticalMode();
        return clamp(fz, PDterms.botZlim, 2);
    }
    unsigned long now = millis();
    bool other_side;
    if (z_err_valid)
        other_side = z_down ? z_err > -PDterms.zDownErr / 2 : (z_err < -PDterms.zDownErr && fz < 0);
    else
        other_side = z_down ? fz > PDterms.zDownOn : fz < -PDterms.zDownOn;
    if (!other_side) {
        z_switch_armed = false;
    } else if (!z_switch_armed) {
        z_switch_armed = true;
        z_switch_ms = now;
    } else if (now - z_switch_ms >= PDterms.zDownMs) {
        z_down = !z_down;
        z_switch_armed = false;
        z_flip_active = true;
        z_flip_checked = false;
        z_flip_ms = now;
    }
    return z_down ? clamp(fz, PDterms.botZlim, 0) : clamp(fz, 0, 2);
}

void FullBicopter::resetVerticalMode() {
    z_down = false;
    z_switch_armed = false;
    z_flip_active = false;
}

void FullBicopter::getOutputs(float sensors[MAX_SENSORS], float controls[], float out[]) {
    // Assuming PDterms, kf1, kf2, servo1offset, servo2offset, and feedbackPD.pitch are defined elsewhere

    float l = PDterms.lx;

    float fx = clamp(controls[0], -1, 1);
    float fz = verticalForce(controls[1]); // >= 0 in up mode, <= 0 in down mode
    float taux = clamp(controls[2], -l + 0.01f, l - 0.01f);
    float tauz = clamp(controls[3], -.1, .1);

    // Pitch correction (applied to the angles below). The tilt is relative to the zero captured
    // while Off (pitchOffset is a small trim in degrees) and is limited so a wrong zero or axis can
    // never turn the thrust flat (flight 2026-10-29 18:50).
    // With a stale IMU (stream stopped) the pitch reading is frozen at whatever it was, so no
    // compensation: the robot then flies as a plain manual craft (baro height hold, stick yaw).
    float pitch_comp = 0.0f;
    if (PDterms.pitchEn && pitch_zero_valid && !imu_stale) {
        constexpr float MAX_PITCH_COMP = 25.0f * PI / 180.0f;
        pitch_comp = clamp(pitchTilt(sensors) * PDterms.pitchInvert + PDterms.pitchOffset/180 * PI,
                           -MAX_PITCH_COMP, MAX_PITCH_COMP);
    }

    // Yaw torque tilts the two thrusts in opposite directions away from the force direction.
    // With little lift that tilt reaches horizontal and one servo hits its end stop, leaving net
    // forward thrust (bench log 2026-10-29). Keep the yaw tilt within MAX_YAW_TILT of the force;
    // With a = l*fx, b = l*fz the motors point along (a +- tauz, b); keeping both within the
    // tilt of (a, b) gives |tauz| <= tan(tilt) * (a^2 + b^2) / (b + tan(tilt) * |a|).
    // 55 deg gives usable heading hold at low lift; yaw tilt plus pitch correction stays within
    // 65 deg so neither servo gets near its end stop.
    constexpr float MAX_YAW_TILT = 55.0f * PI / 180.0f;
    constexpr float MAX_TOTAL_TILT = 65.0f * PI / 180.0f;
    const float yaw_tilt = clamp(MAX_TOTAL_TILT - fabsf(pitch_comp), 20.0f * PI / 180.0f, MAX_YAW_TILT);
    const float tan_tilt = tanf(yaw_tilt);
    const float a = l * fx, b = l * fabsf(fz); // the bound is symmetric for downward thrust
    const float denom = b + tan_tilt * fabsf(a);
    const float yaw_cap = denom > 1e-9f ? tan_tilt * (a * a + b * b) / denom : 0.0f;
    // The yaw torque a given tauz produces grows with the total thrust command (brushless thrust
    // rises ~quadratically with command, so the differential (f1^2 - f2^2) ~ tauz * |F|). The yaw
    // gains were tuned near hover; scale the command down above that level so a forward push at
    // full thrust does not turn a small heading error into a spin (flights 2026-10-30).
    if (PDterms.yawAuthRef > 0.0f) {
        const float level = hypot(fx, fabsf(fz));
        if (level > PDterms.yawAuthRef) tauz *= PDterms.yawAuthRef / level;
    }
    tauz = clamp(tauz, -yaw_cap, yaw_cap);

    // Inverse A-Matrix calculations
    // Each motor's thrust is the length of the same vector that sets its angle. The original
    // code paired them crosswise, which reversed yaw torque once |fx| outweighed fz.
    float term3 = hypot(l * fx + tauz, l * fz - taux); // motor 1, same vector as t1
    float term4 = hypot(l * fx - tauz, l * fz + taux); // motor 2, same vector as t2
    float f1 = term3 / (2 * l);
    float f2 = term4 / (2 * l);
    // Normalized thrust below this value has no useful direction.
    constexpr float direction_epsilon = 1e-5f;
    bool direction1_valid = f1 > direction_epsilon;
    bool direction2_valid = f2 > direction_epsilon;
    float t1 = PI / 2;
    float t2 = PI / 2;
    // Keep each direction in the half the thrust mode allows (upper in up mode, lower in down
    // mode) and stop it at the backward end instead of wrapping past +-pi. A zero vertical
    // component comes out of atan2 as +pi or -pi depending on the sign of the zero, and a wrap
    // sends the servo to the other end of its travel: full-turn servo swings while flying
    // backward (SwarmBase log 20261102-143346, t = 157-162 s).
    auto keepHalf = [this](float t) {
        if (z_down) return t > 0 ? (t > PI / 2 ? -PI : 0.0f) : t;
        return t < 0 ? (t < -PI / 2 ? PI : 0.0f) : t;
    };
    auto stopAtBack = [this](float t) { return z_down ? fmaxf(t, -PI) : fminf(t, PI); };
    if (direction1_valid) t1 = keepHalf(atan2(l * fz - taux, l * fx + tauz));
    if (direction2_valid) t2 = keepHalf(atan2(l * fz + taux, l * fx - tauz));

    // Apply pitch once to a newly computed direction, never to a held angle.
    if (direction1_valid) t1 = stopAtBack(t1 + pitch_comp);
    if (direction2_valid) t2 = stopAtBack(t2 + pitch_comp);

    // Checking for full rotations and adjusting t1 and t2
    t1 = adjustAngle(t1);
    t2 = adjustAngle(t2);

    // Converting values to a more stable form
    // float servoBottom = 90.0f - PDterms.servoRange/2.0f; // bottom limit of servo in degrees
    // float servoTop = 90.0f + PDterms.servoRange/2.0f; // top limit of servo in degrees
    out[2] = clamp((t1 ) * 180.0f / PI  + PDterms.servoBeta , 0.0f,  PDterms.servoRange ) * 180.0f / PDterms.servoRange;
    out[3] = 180.0f -clamp((t2) * 180.0f / PI  + PDterms.servoBeta, 0.0f,  PDterms.servoRange ) * 180.0f / PDterms.servoRange;
    out[0] = clamp(f1, 0, 1);
    out[1] = clamp(f2, 0, 1);

    // Up/down flip (verticalForce): when the servos have far to go, the props first spin down
    // with the servos held, then the servos swing with the motors still off. Near-horizontal
    // thrust (forward flight) flips with a small servo move and needs no cut.
    if (z_flip_active) {
        if (!z_flip_checked && direction1_valid && direction2_valid) {
            constexpr float SMALL_SWING_DEG = 40.0f; // servo shaft degrees
            const float small = SMALL_SWING_DEG * 180.0f / PDterms.servoRange;
            z_flip_checked = true;
            if (!servo_history_valid || fmaxf(fabsf(out[2] - servo_old1), fabsf(out[3] - servo_old2)) < small)
                z_flip_active = false;
        }
        if (z_flip_active) {
            unsigned long elapsed = millis() - z_flip_ms;
            out[0] = out[1] = 0;
            if (elapsed < PDterms.zCoastMs) {
                out[2] = servo_old1;
                out[3] = servo_old2;
            } else if (elapsed >= PDterms.zCoastMs + PDterms.zSwingMs) {
                z_flip_active = false;
            }
        }
    }

    if (servo_history_valid && (!direction1_valid || abs(out[2] - servo_old1) < PDterms.servo_move_min)) {
        out[2] = servo_old1;
    } else {
        servo_old1 = out[2];
    }
    
    if (servo_history_valid && (!direction2_valid || abs(out[3] - servo_old2) < PDterms.servo_move_min)) {
        out[3] = servo_old2;
    } else {
        servo_old2 = out[3];
    }
    servo_history_valid = true;
    // // Adjust servo positions if motor speeds are too low
    // if (out[0] < 0.02f) {
    //     out[2] = 90;
    // }
    // if (out[1] < 0.02f) {
    //     out[3] = 90;
    // }
}