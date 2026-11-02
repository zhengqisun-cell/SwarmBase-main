/**
 * @file RawBicopter.h
 * @author David Saldana
 * @brief Robot Class that converts high-level commands directly to actuation values
 * @version 0.1
 * @date 2024-01-20
 * 
 * @copyright Copyright (c) 2024
 * 
 */
#ifndef BLIMPSWARM_RAWBICOPTER_H
#define BLIMPSWARM_RAWBICOPTER_H


#include "Robot.h"
#include "act/BLMotor.h"
#include "act/AServo.h"
#include "act/LED.h"
#include "act/ServoFlipGuard.h"
#include <Preferences.h>
#include "util/DataTypes.h"

class RawBicopter : public Robot {
public:
    /**
     * @brief Construct a new Raw Bicopter object
     * 
     */
    RawBicopter();

    /**
     * @copydoc Robot::startup()
     * 
     */
    void startup() override;
    
    /**
     * @copydoc Robot::sense()
     * 
     * @brief RawBicopter does not include any sensors
     * 
     */
    int sense(float sensors[MAX_SENSORS]) override;
    
    /**
     * @copydoc Robot::actuate()
     * 
     */
    void actuate(const float actuators[], int size) override;

    // Print the last completed output call and the PWM library's current state.
    void printActuatorOutputs();

    // Last applied output: 0,1 motors (0..1), 2,3 servo angles (deg), 4 LED.
    float lastActuator(int i) const { return last_actuators[i]; }

    /**
     * @copydoc Robot::control()
     * 
     * @brief Directly converts array of higher-level control commands into actuation
     * 
     */
    void control(float sensors[MAX_SENSORS], float controls[], int size ) override;

    /**
     * @copydoc Robot::calibrate
     * 
     */
    void calibrate() override;

    /**
     * @copydoc Robot::arm()
     * 
     */
    void arm() override;

    /**
     * @copydoc Robot::getPreferences()
     * 
     */
    void getPreferences() override;

    /**
     * @brief Adjusts the servo deadzone to be in the correct place.
     * 
     * @param angle The current angle of the motor
     * @return float The angle value after adjustment is made
     */
    float adjustAngle(float angle);
    
    /**
     * @brief Clamps a value between a minimum and maximum.
     * 
     * @param val Value to be clamped.
     * @param minVal Minimum value that val can be.
     * @param maxVal Maximum value that val can be.
     * @return float Returns the val if within range, otherwise returns min or max.
     */
    float clamp(float val, float minVal, float maxVal);

    feedback_t PDterms;

private:
    float servoDiff = 0;
    float last_actuators[5] = {};
    float requested_actuators[5] = {};
    ServoFlipGuard flip_guard;
    BLMotor* motor1;
    BLMotor* motor2;
    AServo* servo1;
    AServo* servo2;
    LED* led;
};


#endif //BLIMPSWARM_RAWBICOPTER_H
