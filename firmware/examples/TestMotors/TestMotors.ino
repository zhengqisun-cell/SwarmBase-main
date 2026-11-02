#define LED_BLUE Dy 
#define LED_RED Dx
#define SERVO_L D9
#define SERVO_R D10
#define THRUST_L D0
#define THRUST_R D1


#include <ESP32Servo.h>

Servo servo1;
Servo servo2;
Servo thrust1;
Servo thrust2;
int SERVO_LOCK = 0; // Lock the servo at 90 degree for arm installation

void setup() {
  // pinMode(LED_BLUE, OUTPUT); // Initialize the LED_BUILTIN pin as an output
  // pinMode(LED_RED, OUTPUT); // Initialize the LED_BUILTIN pin as an output
  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
  servo1.setPeriodHertz(50);// Standard 50hz servo
  servo2.setPeriodHertz(50);// Standard 50hz servo

  thrust1.setPeriodHertz(51);// Standard 50hz servo
  thrust2.setPeriodHertz(51);// Standard 50hz servo

  servo1.attach(SERVO_L, 650, 2500); // 0043 Servos
  servo2.attach(SERVO_R, 650, 2500); // 0043 Servos

  thrust1.attach(THRUST_L, 1000, 2000);
  thrust2.attach(THRUST_R, 1000, 2000);

  // ESC arm
  escarm();

}

// The loop function runs over and over again forever
void loop() {
    // Sweep servos from 0 to 180 degrees and increase thrust from 1100 to 2000
    for (int posVal = 0; posVal <= 180; posVal++) {
        int thrustVal = map(posVal, 0, 180, 1100, 2000); // Map servo angle to thrust value
        
        servo1.write(posVal);
        servo2.write(posVal);
        thrust1.writeMicroseconds(thrustVal);
        thrust2.writeMicroseconds(thrustVal);
        
        delay(20);
    }

    delay(1000);

    // Sweep servos from 180 to 0 degrees and decrease thrust from 2000 to 1100
    for (int posVal = 180; posVal >= 0; posVal--) {
        int thrustVal = map(posVal, 0, 180, 1100, 2000); // Map servo angle to thrust value
        
        servo1.write(posVal);
        servo2.write(posVal);
        thrust1.writeMicroseconds(thrustVal);
        thrust2.writeMicroseconds(thrustVal);
        
        delay(20);
    }
    delay(2000);

    while(SERVO_LOCK){
        servo1.write(90);
        servo2.write(90);
    }
}


//Enter arming sequence for ESC
void escarm(){
  servo1.write(180);
  servo2.write(180);
  Serial.println("Arming");
  // ESC arming sequence for BLHeli S
  thrust1.writeMicroseconds(1000);
  delay(10);
  thrust2.writeMicroseconds(1000);
  delay(10);

  // Sweep up
  for(int i=1100; i<1500; i++) {
    thrust1.writeMicroseconds(i);
    delay(5);
    thrust2.writeMicroseconds(i);
    delay(5);
  }
  // Sweep down
  for(int i=1500; i<1100; i--) {
    thrust1.writeMicroseconds(i);
    delay(5);
    thrust2.writeMicroseconds(i);
    delay(5);
  }
  // Back to minimum value
  thrust1.writeMicroseconds(1100);
  delay(200);
  thrust2.writeMicroseconds(1100);
  delay(200);
}
