/**
 * @file RawBicopter.cpp
 * @author Edward Jeff
 * @brief Implementation of RawBicopter.h
 * @version 0.1
 * @date 2024-01-20
 * 
 * @copyright Copyright (c) 2024
 * 
 */


#include "RawBicopter.h"
#include <Arduino.h>


#define SERVO1 D0
#define SERVO2 D1
#define THRUST1 D9
#define THRUST2 D10
#define BATT A2

static constexpr int MOTOR_PWM_HZ = 55;
// Cutting thrust on every large servo swing caused repeated ~1 s thrust loss in flight,
// so the flip guard is off; set true to bring back ServoFlipGuard.
static constexpr bool SERVO_FLIP_GUARD = false;


RawBicopter::RawBicopter(){
    
}

void RawBicopter::startup() {
    servo1 = new AServo(SERVO1);
    servo2 = new AServo(SERVO2);
    motor1 = new BLMotor(1100, 2000, 0, THRUST1, MOTOR_PWM_HZ);
    motor2 = new BLMotor(1100, 2000, 0, THRUST2, MOTOR_PWM_HZ);
    led = new LED(LED_BUILTIN);


    ESP32PWM::allocateTimer(0);
    ESP32PWM::allocateTimer(1);
    ESP32PWM::allocateTimer(2);
    ESP32PWM::allocateTimer(3);

    Preferences preferences;
    
    preferences.begin("params", false); //true means read-only
    if (preferences.getBool("calibrate", false)){
        //calibrate brushless motors simultaneously
        calibrate();
        preferences.putBool("calibrate", false);
    } else {
        // Arm brushless motors simulataneously
        arm();
    }
    preferences.end();
}

int RawBicopter::sense(float sensors[MAX_SENSORS]) {
    return 0;
}

void RawBicopter::actuate(const float actuators[], int size) {
    float applied[5];
    if (SERVO_FLIP_GUARD) {
        flip_guard.apply(actuators, PDterms.servoRange, (uint32_t)micros(), applied);
    } else {
        bool finite = true;
        for (int i = 0; i < 5; ++i) {
            applied[i] = actuators[i];
            finite = finite && isfinite(actuators[i]);
        }
        if (!finite) { // never pass NaN/inf thrust to the ESCs; keep the servos where they were
            applied[0] = applied[1] = 0.f;
            applied[2] = last_actuators[2]; applied[3] = last_actuators[3];
        }
    }
    // Cut motor commands before touching either servo on a flip/stop call.
    motor1->act(applied[0]);
    motor2->act(applied[1]);
    servo1->act(applied[2]);
    servo2->act(applied[3]);
    led->act(applied[4]);
    for (int i = 0; i < 5; ++i) {
        requested_actuators[i] = actuators[i]; last_actuators[i] = applied[i];
    }
}

void RawBicopter::printActuatorOutputs() {
    Serial.printf(" flip_phase=%d flip_count=%lu coast_ms=%lu settle_ms=%lu pwm_updates=%lu,%lu pwm_late=%lu,%lu servo_ticks_set=%d,%d servo_tick_sum=%llu,%llu servo_us_sum=%llu,%llu requested=",
        SERVO_FLIP_GUARD ? (int)flip_guard.currentPhase() : -1, flip_guard.flipCount(), // phase -1: guard off
        (unsigned long)(ServoFlipGuard::COAST_US/1000), (unsigned long)(ServoFlipGuard::SETTLE_US/1000),
        servo1->compensationUpdates(), servo2->compensationUpdates(),
        servo1->compensationLateFrames(), servo2->compensationLateFrames(),
        servo1->lastDutyTicks(), servo2->lastDutyTicks(),
        (unsigned long long)servo1->totalDutyTicks(), (unsigned long long)servo2->totalDutyTicks(),
        (unsigned long long)servo1->totalRequestedPulseUs(), (unsigned long long)servo2->totalRequestedPulseUs());
    for (int i=0; i<5; ++i) { if (i) Serial.print(','); Serial.printf("%.9g",requested_actuators[i]); }
    Serial.print(" out=");
    for (int i = 0; i < 5; ++i) {
        if (i) Serial.print(',');
        Serial.printf("%.9g", last_actuators[i]);
    }
    Serial.printf(" motor_us_req=%d,%d motor_us_set=%d,%d servo_deg_cmd=%d,%d servo_us_set=%d,%d",
        motor1->lastRequestedPulseUs(), motor2->lastRequestedPulseUs(),
        motor1->readPulseMicroseconds(), motor2->readPulseMicroseconds(),
        servo1->lastRequestedAngle(), servo2->lastRequestedAngle(),
        servo1->readPulseMicroseconds(), servo2->readPulseMicroseconds());
    const int pins[] = {THRUST1, THRUST2, SERVO1, SERVO2};
    const int bits[] = {motor1->pulseResolutionBits(), motor2->pulseResolutionBits(),
        servo1->pulseResolutionBits(), servo2->pulseResolutionBits()};
    for (int i = 0; i < 4; ++i) {
        ESP32PWM* pwm = pwmFactory(pins[i]);
        int channel = pwm ? pwm->getChannel() : -1;
        Serial.printf(" ledc%d=%d,%d,%d,%lu,%lu", i + 1, pins[i], channel, bits[i],
            channel < 0 ? 0UL : (unsigned long)ledcReadFreq(channel),
            channel < 0 ? 0UL : (unsigned long)ledcRead(channel));
    }
    Serial.println();
}


void RawBicopter::control(float sensors[MAX_SENSORS], float controls[], int size) {
    RawBicopter::actuate(controls, size);
}

void RawBicopter::getPreferences() {
    Preferences preferences;
    preferences.begin("params", true); // Initializes the preferences in read-only mode   

    // A-matrix adjustments for the servo
    PDterms.servoBeta = preferences.getFloat("servoBeta", 90);
    PDterms.servoRange = preferences.getFloat("servoRange", 260);
    PDterms.botZlim = preferences.getFloat("botZlim", 0.001);
    PDterms.pitchOffset = preferences.getFloat("pitchOffset", 0);
    PDterms.pitchInvert = preferences.getFloat("pitchInvert", 1);
    PDterms.servo_move_min = preferences.getFloat("servo_move_min", 2); // degrees

    servoDiff = 2*PI - PDterms.servoRange * PI/180;// calculating the servo dead zone

    preferences.end();
}

void RawBicopter::calibrate(){
    delay(1000);
    Serial.println("Calibrating ESCs....");
    // ESC arming sequence for BLHeli S
    motor1->act(1);
    motor2->act(1);
    delay(8000);

    // Back to minimum value
    motor1->act(0);
    motor2->act(0);
    delay(8000);
    //motor1->act(-1); //FIXME is this necessary? If so, we can have a if (value== -1) then writeMicroseconds(0) in motor
    delay(1000);
    Serial.println("Calibration completed");
}

void RawBicopter::arm(){
    // ESC arming sequence for BLHeli S
    motor1->act(0);
    motor2->act(0);
    delay(10);

    // Sweep up
    for (int i = 1050; i < 1500; i++)
    {
        motor1->act((i-1000)/1000);
        motor2->act((i-1000)/1000);
        delay(6);
    }

    // Back to minimum value
    motor1->act(0);
    motor2->act(0);
    delay(1000);
}

// adjusts the servo deadzone to be in the correct place
float RawBicopter::adjustAngle(float angle) {
  while (angle <  - servoDiff / 2 - PDterms.servoBeta * PI/180.0f ) angle += 2 * PI;
  while (angle > 2 * PI - servoDiff / 2 - PDterms.servoBeta * PI/180.0f ) angle -= 2 * PI;
  return angle;
}

float RawBicopter::clamp(float val, float minVal, float maxVal) {
    return std::max(minVal, std::min(maxVal, val));
}

