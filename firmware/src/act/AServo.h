/**
 * @file AServo.h
 * @author David Saldana
 * @brief Actuation of servo motors for a XIAO ESP32S3
 * @version 0.1
 * @date 2024-02-09
 * 
 * @copyright Copyright (c) 2024
 * 
 */

#ifndef BLIMPSWARM_ASERVO_H
#define BLIMPSWARM_ASERVO_H

#include "Actuator.h"
#include <stdint.h>
#include <ESP32Servo.h> // Primary library used for the actuation of servos for all esp32 chips

class AServo : public Actuator{
public:
    /**
     * @brief Construct a new AServo object
     * 
     * @param minVal Minimum value that can be used to actuate
     * @param maxVal Maximum value that can be used to actuate
     * @param offsetVal Offset value for correction of error
     * @param pinVal Pin used for the component
     * @param periodHertz The frequency at which the component is actuated
     */
    AServo(int minVal, int maxVal, int offsetVal, int pinVal, int periodHertz);

    AServo(int pinVal);

    /**
     * @brief Actuates the value given to the servo motor
     * 
     * @param value The value to actuate
     */
    void act(float value);

    // Diagnostic accessors: commanded angle and library state, not shaft feedback.
    int lastRequestedAngle() const { return last_requested_angle; }
    int readPulseMicroseconds() { return servo.readMicroseconds(); }
    int pulseResolutionBits() { return servo.readTimerWidth(); }
    int lastDutyTicks() const { return last_duty_ticks; }
    uint64_t totalDutyTicks() const { return duty_tick_sum; }
    uint64_t totalRequestedPulseUs() const { return pulse_us_sum; }
    // Existing log accessor names retained; counts now describe fixed PWM writes.
    unsigned long compensationUpdates() const { return compensation_updates; }
    unsigned long compensationLateFrames() const { return compensation_late_frames; }

private:
    Servo servo;
    int last_requested_angle = 0;
    int period_hertz = 50;
    // 50Hz / 14 bits gives 1.22us ticks, supported by the ESP32-S3.
    static constexpr int PWM_BITS = 14;
    uint32_t last_pwm_update_us = 0;
    unsigned long compensation_updates = 0;
    unsigned long compensation_late_frames = 0;
    int last_duty_ticks = 0;
    uint64_t duty_tick_sum = 0, pulse_us_sum = 0;
    bool pwm_initialized = false;
};


#endif //BLIMPSWARM_ASERVO_H
