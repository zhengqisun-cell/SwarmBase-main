/**
 * BICOPTER with altitude control
 * This code runs a bicopter with altitude control using the feedback from a barometer.
 * For this example, your robot needs a barometer sensor.
 */

#include "BlimpSwarm.h"
#include "robot/RobotFactory.h"
#include "comm/BaseCommunicator.h"
#include "comm/LLC_ESPNow.h"
#include "util/Print.h"
#include "sense/SensorSuite.h"
#include <Arduino.h>
#include <ESP32Servo.h>


// Robot
Robot* myRobot = nullptr;

// Communication
BaseCommunicator* baseComm = nullptr;

// Control input from base station
ControlInput cmd;
ReceivedData rcv; 

// Data storage for the sensors 
float senses[myRobot->MAX_SENSORS];

const int TIME_STEP_MICRO = 4000;
float groundAltitude = 0;
int dt = 1000;
unsigned long clockTime;
unsigned long printTime;



void setup() {
    Serial.begin(115200);
    Serial.println("Start!");
    clockTime = micros();
    printTime = micros();
    // init communication
    baseComm = new BaseCommunicator(new LLC_ESPNow());
    baseComm->setMainBaseStation();

    // init robot with new parameters
    myRobot = RobotFactory::createRobot("SBlimp");
    paramUpdate();

    // updates the ground altitude for the ground feedback
    // TODO: make some way to access the actual ground height from robot
    int numSenses = myRobot->sense(senses);
    groundAltitude = senses[1];//height
}


void loop() {
  // Retrieves cmd.params from ground station and checks flags
  recieveCommands();

  // Get sensor values
  int numSenses = myRobot->sense(senses);

  // send values to ground station
  rcv.flag = 1;
  rcv.values[0] = senses[1] - groundAltitude;  //height
  rcv.values[1] = senses[5];  //yaw
  rcv.values[2] = senses[10];  //battery
  rcv.values[3] = senses[0];  //temperature
  rcv.values[4] = 0;  // Free slot for custom usage
  rcv.values[5] = 0;  // Free slot for custom usage
  bool sent = baseComm->sendMeasurements(&rcv); // sends at most 3 packets per second to ground station

  // print sensor values every second
  // senses => [temperature, altitude, veloctity in altitude, roll, pitch, yaw, rollrate, pitchrate, yawrate, null, battery]
  if (micros() - printTime > 1000000){
    for (int i = 0; i < numSenses-1; i++){
      Serial.print(senses[i]);
      Serial.print(",");
    }
    Serial.println(senses[numSenses-1]);
    printTime = micros();
  }

  // Send command to the actuators
  myRobot->control(senses, cmd.params, 5);

  // makes the clock rate of the loop consistant. 
  fixClockRate();
}

void recieveCommands(){
  if (baseComm->isNewMsgCmd()){
    // New command received
    cmd = baseComm->receiveMsgCmd();
    if (int(cmd.params[11]) == 1){
      paramUpdate();
    }
    // Print command
    Serial.print("Cmd arrived: ");
    printControlInput(cmd);
  }
}

void paramUpdate(){

    myRobot->getPreferences();
    baseComm->setMainBaseStation();
    
}

void fixClockRate() {

  dt = (int)(micros()-clockTime);
  while (TIME_STEP_MICRO - dt > 0){
    dt = (int)(micros()-clockTime);
  }
  clockTime = micros();
}
