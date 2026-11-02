#include "BlimpSwarm.h"
#include "robot/RobotFactory.h"
#include <Arduino.h>

Robot* myRobot = nullptr;

float sensorData[Robot::MAX_SENSORS];
// Actuation commands:
float actuationCommands[] = {0.0, 0.0, 0.0, 0.0};


void setup() {
    // Start the serial communication
    Serial.begin(9600);

    // Create a RawBicopter using the RobotFactory
    myRobot = RobotFactory::createRobot("RawBicopter");

    if (myRobot != nullptr) {
        Serial.println("RawBicopter created successfully.");
        // Perform initial operations if necessary
    } else {
        Serial.println("Failed to create RawBicopter.");
    }
}

void loop() {
    // Check if the robot was created successfully
    if (myRobot != nullptr) {
        // Sense
        int numSensors = myRobot->sense(sensorData);
        // Process sensor data
        // ...

        // Actuate
        testActuators(actuationCommands);
        myRobot->actuate(actuationCommands, sizeof(actuationCommands) / sizeof(actuationCommands[0]));


        // Print 
        Serial.print("Cmds: ");
        for (int i = 0; i < 4; i++) {
            Serial.print(actuationCommands[i]);
            Serial.print(" ");  // Print a space between numbers
        }
        Serial.println(); // Print a newline after the array
    }
    // Other loop code, if any

    delay(100); // Delay for demonstration purposes
}

void cleanUp() {
    if (myRobot != nullptr) {
        delete myRobot;
        myRobot = nullptr;
    }
}

void testActuators(float actuationCmd[4]) {
    int servo_delta = 1;
    int motor_delta = 10;

    if (actuationCmd[0] < 180) {
        actuationCmd[0] += servo_delta;
    } else if (actuationCmd[1] < 180) {
        actuationCmd[1] += servo_delta;
    } else if (actuationCmd[2] < 2000) {
        actuationCmd[2] += motor_delta;
    } else if (actuationCmd[3] < 2000) {
        actuationCmd[3] += motor_delta;

    }
}