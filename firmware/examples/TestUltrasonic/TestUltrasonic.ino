#include <Arduino.h>
#include "BlimpSwarm.h"
#include "sense/GY_US42V2.h"

GY_US42V2 ultrasonic;


void setup(){
  delay(250);
  Serial.begin(115200);
//   Serial.println("Start Sensortest");
  // GY_US42V2 ultrasonic;
//   SVerial.println("setup done");
}

void loop(){
//   sensors.update();
  
  

  uint8_t test;
  test= ultrasonic.readDistance();
  // float* sensorValue = test;

  
  // Serial.print(-10);
  // Serial.print(",");
  // Serial.print(10);
  // Serial.print(",");
//   for (int i = 0; i < test-1; i++){
//     Serial.print(sensorValues[i]);
//     Serial.print(",");
//   }

  Serial.println(test);
  delay(10);

}