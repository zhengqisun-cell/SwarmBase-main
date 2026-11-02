/**
 * @file AServo.cpp
 * @author David Saldana
 * @brief Implementation of Aservo.h
 * @version 0.1
 * @date 2024-02-09
 * 
 * @copyright Copyright (c) 2024
 * 
 */

#include "AServo.h"
#include <math.h>



AServo::AServo(int minVal, int maxVal, int offsetVal, int pinVal, int periodHertz): Actuator(minVal, maxVal, offsetVal, pinVal) {
    // Additional initialization specific to servos
    this->period_hertz = periodHertz;
    pinMode(this->pin, OUTPUT);
    servo.attach(this->pin, this->min, this->max);
    servo.setPeriodHertz(this->period_hertz);
    // This library resets the width in attach(), so configure it afterwards.
    servo.setTimerWidth(PWM_BITS);
}

AServo::AServo(int pinVal): Actuator(550, 2450, 0, pinVal) {
    // Additional initialization specific to servos
    pinMode(this->pin, OUTPUT);
    servo.attach(this->pin, this->min, this->max);
    servo.setPeriodHertz(50); // Standard 50hz servo
    servo.setTimerWidth(PWM_BITS);
}


void AServo::act(float value) {
    // Preserve the library's integer angle -> integer microsecond mapping.
    // Use a fixed nearest 14-bit duty, never alternate pulses at a held angle.
    if (!isfinite(value)) return;
    last_requested_angle = (int)constrain(value, 0, 180);
    const uint32_t now = (uint32_t)micros();
    const uint32_t period_us = 1000000UL / period_hertz;
    if (pwm_initialized && (uint32_t)(now - last_pwm_update_us) < period_us) return;
    if (pwm_initialized) {
        const uint32_t frames = (uint32_t)(now - last_pwm_update_us) / period_us;
        last_pwm_update_us += frames * period_us;
        // Never replay missed writes in a burst. Delayed loop timing is observable.
        if (frames > 1) compensation_late_frames += frames - 1;
    } else { last_pwm_update_us = now; pwm_initialized = true; }
    const int pulse_us = map(last_requested_angle, 0, 180, min, max);
    const double wanted = (double)pulse_us * (1UL << servo.readTimerWidth()) * period_hertz / 1000000.0;
    const int proposed = (int)floor(wanted + 0.5);
    // Respect exactly the existing Servo library limits, including end-stop saturation.
    const double tick_scale = (double)(1UL << servo.readTimerWidth()) * period_hertz / 1000000.0;
    const int low = (int)(min * tick_scale), high = (int)(max * tick_scale);
    last_duty_ticks = constrain(proposed, low, high);
    servo.writeTicks(last_duty_ticks);
    duty_tick_sum += last_duty_ticks; pulse_us_sum += pulse_us;
    ++compensation_updates;
}
