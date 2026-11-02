

#include <Arduino.h>
#include "BlimpSwarm.h"
#include "sense/Nicla.h"


Nicla sensors; 
// Barometer sensors;
// BNO85 sensors;
// WeightedBatterySensor sensors;
void setup(){
  delay(250);
  Serial.begin(115200);
  Serial.println("Start Sensortest");
  sensors.startup(0x81);
  Serial.println("setup done");
}

void loop(){
  sensors.update();
  
  

  int test;
  float* sensorValues = sensors.readValues(test);
  
  // Serial.print(-10);
  // Serial.print(",");
  // Serial.print(10);
  // Serial.print(",");
  for (int i = 0; i < test-1; i++){
    Serial.print(sensorValues[i]);
    Serial.print(",");
  }
  Serial.println(sensorValues[test-1]);
  delay(10);

}