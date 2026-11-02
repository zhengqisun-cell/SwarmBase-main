/**
 * BICOPTER with altitude control
 * This code runs a bicopter with altitude control using the feedback from a barometer.
 * For this example, your robot needs a barometer sensor.
 */

#include "BlimpSwarm.h"
#include "robot/RobotFactory.h"
#include "state/nicla/ManualState.h"
#include "comm/BaseCommunicator.h"
#include "comm/LLC_ESPNow.h"
#include "util/Print.h"
#include "sense/SensorSuite.h"
#include <Arduino.h>
#include <ESP32Servo.h>


// Robot
FullBicopter* myRobot = nullptr;

// Sensor
NiclaSuite* nicla = nullptr;

// Behavior
RobotStateMachine* stateMachine = nullptr;
nicla_t terms; 
hist_t* hist;

// Communication
BaseCommunicator* baseComm = nullptr;

// Control input from base station
ControlInput behave;
ControlInput cmd;
ReceivedData rcv; 

// Data storage for the sensors 
float senses[myRobot->MAX_SENSORS];

const int TIME_STEP_MICRO = 4000;

int niclaOffset = 11;
int dt = 1000;
unsigned long clockTime;
unsigned long printTime;
unsigned long nicla_change_time;

// int nicla_flag = 0;

void setup() {
    Serial.begin(115200);
    Serial.println("Start!");
    clockTime = micros();
    printTime = micros();
    // init communication
    baseComm = new BaseCommunicator(new LLC_ESPNow());
    baseComm->setMainBaseStation();

    // init robot with new parameters
    myRobot = new FullBicopter();//RobotFactory::createRobot("FullBicopter");
    myRobot->startup();

    nicla = &(myRobot->sensorsuite);
    stateMachine = new RobotStateMachine(new ManualState());
    
    paramUpdate();
    hist->nicla_flag = 0x80;

    nicla->changeNiclaMode(0x80);

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
  if (cmd.params[0] == 5 && cmd.params[6] == 1) { 
    rcv.flag = 1;
    rcv.values[0] = senses[1];  //height
    rcv.values[1] = senses[5];  //yaw
    rcv.values[2] = senses[niclaOffset + 5];  //x
    rcv.values[3] = senses[niclaOffset + 6];  //y
    rcv.values[4] = senses[niclaOffset + 7];  //w
    rcv.values[5] = senses[10];  //battery
    Serial.println("Sending Feedback.");
    bool sent = baseComm->sendMeasurements(&rcv);
    cmd.params[0] = 1; // temp assign manual control with these new params for retaining stillness
    cmd.params[2] = senses[1]; // set height to height
    cmd.params[4] = senses[5]; // set yaw to yaw
  } else if(cmd.params[0] == 5 && cmd.params[6] == 0) {
    rcv.flag = 0;
    Serial.println("Stopping Feedback");
    cmd.params[0] = 1; // temp assign manual control with these new params for retaining stillness
    cmd.params[2] = senses[1]; // set height to height
    cmd.params[4] = senses[5]; // set yaw to yaw
  } else if (cmd.params[6] == 1){
    rcv.flag = 1;
    rcv.values[0] = senses[1];  //height
    rcv.values[1] = senses[5];  //yaw
    rcv.values[2] = senses[niclaOffset + 5];  //x
    rcv.values[3] = senses[niclaOffset + 6];  //y
    rcv.values[4] = senses[niclaOffset + 7];  //w
    rcv.values[5] = senses[10];  //battery
    bool sent = baseComm->sendMeasurements(&rcv);

  }
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


  // adjusts the state based on several factors
  niclaStateChange((int)(cmd.params[0]), (int)(cmd.params[7]));

  // Create Behavior based on sensory input to put into behave
  stateMachine->update(senses, cmd.params, behave.params);

  // Send command to the actuators
  myRobot->control(senses, behave.params, 5);

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

void paramUpdate() {
    myRobot->getPreferences();
    baseComm->setMainBaseStation();
    updateNiclaParams();
}

void updateNiclaParams() {
    NiclaConfig::getInstance()->loadConfiguration();
    
    hist = NiclaConfig::getInstance()->getDynamicHistory();
    const nicla_t& config = NiclaConfig::getInstance()->getConfiguration();
    terms = config; // Copy configuration data
}

void niclaStateChange(int cmdFlag, int target_color) {
  int nicla_flag = senses[niclaOffset + 0]; //flag received by nicla
  if (micros() - nicla_change_time > 50000) { // positive edge to avoid spamming
    nicla_change_time = micros();
    int hist_flag = hist->nicla_flag;
    if (cmdFlag == 2) { // normal state machine mode
      if (hist->nicla_desired == 1 && nicla_flag & 0x40) { // if desire mode is goal mode and nicla in ball mode
        Serial.println("go to goal");
        if (target_color == 1) {
          nicla->changeNiclaMode(0x81);
        } else {
          nicla->changeNiclaMode(0x80);
        }
        updateNiclaParams();
        hist->z_estimator = terms.default_height;
      } else if (hist->nicla_desired == 0 && nicla_flag & 0x80) { // if desire mode is ball mode and nicla in goal mode
        Serial.println("go to ball");
        nicla->changeNiclaMode(0x40); //switch nicla to ball mode
        updateNiclaParams();
        hist->z_estimator = terms.default_height;
      }
    } 
    else if (cmdFlag == 3) { //balloon only mode (enforce 0x40)
      hist->nicla_desired = 0;
      if (nicla_flag & 0x80) {
        updateNiclaParams();
        Serial.println("go to ball");
        nicla->changeNiclaMode(0x40);
      }
      hist->start_ball_time= millis();
      hist->num_captures = 0;
    } 
    else if (cmdFlag == 4) { //goal only mode (enforce 0x80)
      if (hist_flag != 4) {
        hist->goal_direction = senses[5];
      }
      hist->nicla_desired = 1;
      hist->start_ball_time= millis();
      hist->num_captures = 0;
      if (nicla_flag & 0x40) {
        updateNiclaParams();
        Serial.println("go to goal");
        if (target_color == 1){
          nicla->changeNiclaMode(0x81);
        } else {
          nicla->changeNiclaMode(0x80);
        }
      }
    }
  }
  
}

void fixClockRate() {

  dt = (int)(micros()-clockTime);
  while (TIME_STEP_MICRO - dt > 0){
    dt = (int)(micros()-clockTime);
  }
  clockTime = micros();
}
