/**
 * RAW BICOPTER
 * This code runs a bicopter in raw mode. Meaning that the input from the base station (using joystick) goes directly
 * to motors.
 */

#include "BlimpSwarm.h"
#include "robot/RobotFactory.h"
#include "comm/BaseCommunicator.h"
#include "comm/LLC_ESPNow.h"
#include "util/Print.h"
#include <Arduino.h>
#include <ESP32Servo.h>


// MAC of the base station
uint8_t base_mac[6] = {0xC0, 0x49, 0xEF, 0xE3, 0x34, 0x78};  // fixme load this from memory

const float TIME_STEP = .01;
// Robot
Robot* myRobot = nullptr;
// Communication
BaseCommunicator* baseComm = nullptr;
// Control input from base station
ControlInput cmd;


void setup() {
    Serial.begin(115200);
    Serial.println("Start!");

    // init communication
    baseComm = new BaseCommunicator(new LLC_ESPNow());
    baseComm->setMainBaseStation();

    // init robot with new parameters
    myRobot = RobotFactory::createRobot("RawBicopter");
}

void loop() {

    if (baseComm->isNewMsgCmd()){
      // New command received
      cmd = baseComm->receiveMsgCmd();

      // Print command
      Serial.print("Cmd arrived: ");
      printControlInput(cmd);

    }

    // Send command to the actuators
    myRobot->actuate(cmd.params, 5);

    sleep(TIME_STEP);
}



