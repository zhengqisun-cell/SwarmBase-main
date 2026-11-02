#ifndef BLIMPSWARM_SERVO_FLIP_GUARD_H
#define BLIMPSWARM_SERVO_FLIP_GUARD_H
#include <stdint.h>
#include <math.h>

// No shaft/RPM feedback is available. These waits are conservative scheduling
// assumptions, NOT a measurement that the motor stopped or the servo arrived.
class ServoFlipGuard {
public:
    enum Phase { RUN = 0, COAST = 1, SETTLE = 2 };
    // 650ms exceeds eight nominal 80ms motor time constants. Servo settling
    // is provisionally 350ms. Neither value has been identified on this robot.
    static constexpr uint32_t COAST_US = 650000;
    static constexpr uint32_t SETTLE_US = 350000;
    static constexpr float TRIGGER_DEG = 100.f;

    void apply(const float request[5], float servo_range, uint32_t now, float out[5]) {
        bool valid = isfinite(servo_range) && servo_range > 0.f;
        for (int i=0; i<5; ++i) valid = valid && isfinite(request[i]);
        if (!valid) {
            // Invalid input can never restore thrust. Fresh settling is required.
            phase = SETTLE; since = now;
            for (int i=0; i<5; ++i) out[i]=0.f;
            out[2]=held[0]; out[3]=held[1];
            initialized = true;
            return;
        }
        for (int i=0; i<5; ++i) out[i]=request[i];
        float target[2];
        for (int i=0; i<2; ++i) target[i]=fmaxf(0.f, fminf(180.f, request[i+2]));
        if (!initialized) {
            initialized=true;phase=SETTLE;since=now;
            for (int i=0; i<2; ++i) held[i]=target[i];
        } else if (phase == RUN && distance(target, held, servo_range) > TRIGGER_DEG) {
            phase=COAST;since=now;++flips;
        }
        if (phase == COAST && (uint32_t)(now-since) >= COAST_US) {
            phase=SETTLE;since=now;
            for (int i=0; i<2; ++i) held[i]=target[i];
        }
        if (phase == SETTLE) {
            // Hold one commanded angle for the whole wait. Incoming feedback
            // noise must not move the servo and restart this timer indefinitely.
            if ((uint32_t)(now-since) >= SETTLE_US) {
                if (distance(target, held, servo_range) > TRIGGER_DEG) {
                    // Still no thrust: a new large reversal gets its own wait.
                    // COAST is unnecessary here; motors have already been cut.
                    for (int i=0; i<2; ++i) held[i]=target[i];
                    since=now;++flips;
                } else {
                    phase=RUN;
                    // Keep the settled angle on this call; the next RUN call
                    // evaluates the latest request with the normal flip check.
                }
            }
        } else if (phase == RUN) {
            for (int i=0; i<2; ++i) held[i]=target[i];
        }
        out[2]=held[0];out[3]=held[1];
        if (phase != RUN) out[0]=out[1]=0.f;
    }
    Phase currentPhase() const { return phase; }
    unsigned long flipCount() const { return flips; }
private:
    static float distance(const float a[2], const float b[2], float range) {
        return fmaxf(fabsf(a[0]-b[0]), fabsf(a[1]-b[1])) * range / 180.f;
    }
    bool initialized=false;
    Phase phase=SETTLE;
    uint32_t since=0;
    float held[2]={135.f,45.f};
    unsigned long flips=0;
};
#endif
