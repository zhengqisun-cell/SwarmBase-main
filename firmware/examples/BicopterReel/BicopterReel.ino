/**
 * BICOPTER with altitude control
 * This code runs a bicopter with altitude control using the feedback from a barometer.
 * For this example, your robot needs a barometer sensor.
 */

#include "BlimpSwarm.h"
#include "robot/RobotFactory.h"
#include "state/nicla/NiclaState.h"
#include "comm/BaseCommunicator.h"
#include "comm/LLC_ESPNow.h"
#include "util/Print.h"
#include "sense/SensorSuite.h"
#include <Arduino.h>
#include <ESP32Servo.h>

#define SERVO3 D3
Servo servoR ;

// Robot
Robot* myRobot = nullptr;

// Behavior
RobotStateMachine* stateMachine = nullptr;

// Communication
BaseCommunicator* baseComm = nullptr;

// Control input from base station
ControlInput behave;
ControlInput cmd;
ReceivedData rcv; 

// Data storage for the sensors 
float senses[myRobot->MAX_SENSORS];

const int TIME_STEP_MICRO = 4000;

int dt = 1000;
unsigned long clockTime;
unsigned long printTime;



void setup() {
    Serial.begin(115200);
    Serial.println("Start!");
    clockTime = micros();
    printTime = micros();
    // init communication

	  ESP32PWM::allocateTimer(4);
    pinMode(SERVO3, OUTPUT);
    servoR.attach(SERVO3, 550, 2450);
    servoR.setPeriodHertz(45); // Standard 50hz servo


    baseComm = new BaseCommunicator(new LLC_ESPNow());
    baseComm->setMainBaseStation();

    // init robot with new parameters
    myRobot = RobotFactory::createRobot("FullBicopter");
    stateMachine = new RobotStateMachine(new LevyWalk());
    paramUpdate();

    // updates the ground altitude for the ground feedback
    // TODO: make some way to access the actual ground height from robot
    int numSenses = myRobot->sense(senses);
    
}


void loop() {
  // Retrieves cmd.params from ground station and checks flags
  recieveCommands();

  // Get sensor values
  int numSenses = myRobot->sense(senses);
  
  // send values to ground station
  rcv.flag = 1;
  rcv.values[0] = senses[1];  //height
  rcv.values[1] = senses[5];  //yaw
  rcv.values[2] = senses[16];  //x
  rcv.values[3] = senses[17];  //y
  rcv.values[4] = senses[18];  //w
  rcv.values[5] = senses[19];  //h
  bool sent = baseComm->sendMeasurements(&rcv);

  // print sensor values every second
  // senses => [temperature, altitude, veloctity in altitude, roll, pitch, yaw, rollrate, pitchrate, yawrate, null, battery]
  if (micros() - printTime > 515106){
      Serial.print(dt/1000.0f);
      Serial.print(",");
    for (int i = 0; i < numSenses-1; i++){
      Serial.print(senses[i]);
      Serial.print(",");
    }
    
    Serial.println(senses[numSenses-1]);
    printTime = micros();
  }

  // Create Behavior based on sensory input to put into behave
  stateMachine->update(senses, cmd.params, behave.params);

  // Send command to the actuators
  myRobot->control(senses, behave.params, 5);

  if (cmd.params[0] == 0) {
    servoR.write((int) 86);
  } else {
    int angle = constrain(cmd.params[6]-4, 0, 180) ; // cant handle values between PI and 2PI
    servoR.write((int) angle);
  }
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
    NiclaConfig::getInstance()->loadConfiguration();
    
}

void fixClockRate() {

  dt = (int)(micros()-clockTime);
  while (TIME_STEP_MICRO - dt > 0){
    dt = (int)(micros()-clockTime);
  }
  clockTime = micros();
}
