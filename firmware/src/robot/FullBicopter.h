/**
 * @file FullBicopter.h
 * @author Edward Jeff
 * @brief Robot class that includes all aspect of robot including motors, servos, IMU, and Nicla Vision
 * @version 0.1
 * @date 2024-03-01
 * 
 * @copyright Copyright (c) 2024
 * 
 */

#ifndef BLIMPSWARM_FULLBICOPTER_H
#define BLIMPSWARM_FULLBICOPTER_H



#include "RawBicopter.h"
#include "sense/NiclaSuite.h"
#include <Arduino.h>




class FullBicopter : public RawBicopter {
public:
    /**
     * @brief Construct a new Full Bicopter object.
     * Initializes the actuator, sensors, and the Nicla Vision.
     * 
     */
    FullBicopter();

    /**
     * @copydoc RawBicopter::sense()
     * 
     * @brief Reads all the values from the sensors on the main board. Includes the BNO and BMP.
     */
    int sense(float sensors[MAX_SENSORS]) override;

    /**
     * @copydoc RawBicopter::control()
     * 
     * @brief Takes the raw commands, adds feedback to those commands,
     * and then calculates the values to actuate.
     */
    void control(float sensors[MAX_SENSORS], float controls[], int size) override;

    /**
     * @copydoc RawBicopter::getPreferences()
     * 
     */
    void getPreferences() override;

    /**
     * @copydoc RawBicopter::startup()
     * 
     */
    void startup() override;
    
    // Sensor interface
    NiclaSuite sensorsuite;

    // List of the variables that need persistant storage
    float z_integral = 0;
    float yaw_integral = 0;
    float yawrate_integral = 0;
    float servo_old1 = 0;
    float servo_old2 = 0;

    // Pitch zero captured while Off; compensation uses the tilt relative to it.
    float pitchZero() const { return pitch_zero; }
    bool pitchZeroValid() const { return pitch_zero_valid; }
    // Heading rate the yaw loop used in the last control() call (raw gyro z or the Euler rate).
    float lastYawRate() const { return last_yaw_rate; }
    bool imuStale() const { return imu_stale; }
    // Thrust vectors below horizontal (downward force allowed); flips only with botZlim < 0.
    bool zDown() const { return z_down; }


private:
    bool servo_history_valid = false;

    float pitch_avg = 0;            // 1 s average of the IMU pitch while Off
    bool pitch_avg_started = false;
    float last_pitch_sample = 0;
    unsigned long last_pitch_change_ms = 0;
    bool was_off = true;
    float pitch_zero = 0;
    bool pitch_zero_valid = false;
    float last_yaw_rate = 0;
    bool imu_stale = false;

    bool z_down = false;
    float z_err = 0;                // height target - height, when the height loop is on
    bool z_err_valid = false;
    bool z_switch_armed = false;    // Fz is past the threshold on the other side, since z_switch_ms
    unsigned long z_switch_ms = 0;
    bool z_flip_active = false;     // motors held off while the servos swing, since z_flip_ms
    bool z_flip_checked = false;
    unsigned long z_flip_ms = 0;

    float verticalForce(float fz);
    void resetVerticalMode();

    void trackPitchZero(float sensors[MAX_SENSORS], bool off);
    void updateYawRate(float sensors[MAX_SENSORS]);
    float pitchTilt(float sensors[MAX_SENSORS]) const;

    /**
     * @brief Applies controllers based on the values retrieved from the sensors.
     * 
     * @param sensors Float array of values received from sensors
     * @param controls Float array of values received from controller input
     * @param feedbackControls The resulting control array after input is added
     */
    void addFeedback(float sensors[MAX_SENSORS], float controls[], float feedbackControls[]);

    /**
     * @brief Controls the outputs after feedback to send them to the actuators
     * 
     * @param sensors Float array of values received from sensors
     * @param controls Float array of values received from controller input
     * @param outputs The resulting control array after controlled
     */
    void getOutputs(float sensors[MAX_SENSORS], float controls[], float outputs[]);
};


#endif //BLIMPSWARM_FULLBICOPTER_H
