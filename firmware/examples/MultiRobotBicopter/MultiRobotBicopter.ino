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

int niclaOffset = NICLA_OFFSET; // Nicla values start after sensorSuite (11) + ultrasonic (1)
const bool BALLOON_ONLY = true; // Keep the camera in balloon tracking (0x40); goal modes are not used
int dt = 1000;
unsigned long clockTime;
unsigned long printTime;
unsigned long nicla_change_time;
int nicla_color_sent = 0;
unsigned long nicla_color_time = 0;

// Low-rate diagnostics after actuation; seq links received and executed commands.
unsigned long commandSequence = 0;
unsigned long outputLogTime = 0;
unsigned long configLogTime = 0;
bool configLogPending = true;

// Wireless health telemetry: pages rotate under flag 1; pages 2-4 put -page in values[5]
// (battery is never negative) so the PC can see sensor health without a USB cable.
int telemetryPage = 1;
unsigned long healthWindowStart = 0;
int maxLoopUs = 0;
int imuChanges = 0;
int niclaFrames = 0;
uint8_t lastNiclaCount = 0;
unsigned long healthCommandStart = 0;
float lastImuSample[3] = {0, 0, 0};

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
    hist->nicla_flag = BALLOON_ONLY ? 0x40 : 0x80;
    if (BALLOON_ONLY) hist->nicla_desired = 0;

    nicla->changeNiclaMode(BALLOON_ONLY ? 0x40 : 0x80);

    // updates the ground altitude for the ground feedback
    // TODO: make some way to access the actual ground height from robot
    int numSenses = myRobot->sense(senses);
    
}


void loop() {
  // Retrieves cmd.params from ground station and checks flags
  recieveCommands();

  // Get sensor values
  int numSenses = myRobot->sense(senses);
  trackHealth();
  
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
    fillTelemetry(telemetryPage);
    if (baseComm->sendMeasurements(&rcv)) {
      if (telemetryPage == 4) resetHealthWindow();
      telemetryPage = telemetryPage % 4 + 1;
    }
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
  niclaColorChange((int)(cmd.params[7]));

  // Create Behavior based on sensory input to put into behave
  stateMachine->update(senses, cmd.params, behave.params);

  // Send command to the actuators
  myRobot->control(senses, behave.params, 5);
  logExecutedOutputs();

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
    ++commandSequence;
    Serial.printf("[CMD] seq=%lu t_us=%lu params=", commandSequence, micros());
    for (int i = 0; i < 13; ++i) {
        if (i) Serial.print(',');
        Serial.printf("%.9g", cmd.params[i]);
    }
    Serial.println();
  }
}

void paramUpdate() {
    myRobot->getPreferences();
    baseComm->setMainBaseStation();
    updateNiclaParams();
    configLogPending = true;
}

void updateNiclaParams() {
    NiclaConfig::getInstance()->loadConfiguration();
    
    hist = NiclaConfig::getInstance()->getDynamicHistory();
    const nicla_t& config = NiclaConfig::getInstance()->getConfiguration();
    terms = config; // Copy configuration data
}

void niclaStateChange(int cmdFlag, int target_color) {
  if (BALLOON_ONLY && (cmdFlag == 2 || cmdFlag == 4)) cmdFlag = 3; // treat every autonomous mode as balloon-only
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

// Balloon color from the base (cmd.params[7]): 0 keeps the camera's own setting,
// 1 purple, 2 green, 3 both, 4 red -> camera bytes 0x42..0x45.
void niclaColorChange(int target_color) {
  if (!BALLOON_ONLY || target_color < 1 || target_color > 4) return;
  bool changed = target_color != nicla_color_sent;
  if (changed || millis() - nicla_color_time > 1000) { // resend once a second in case the camera rebooted
    nicla->changeNiclaMode(0x41 + target_color);
    nicla_color_sent = target_color;
    nicla_color_time = millis();
    if (changed) Serial.printf("[NICLA] color=%d byte=0x%02X\n", target_color, 0x41 + target_color);
  }
}

// At most two snapshots per second, even when commands arrive faster.
// These are software output settings; no external PWM or shaft feedback is implied.
void logExecutedOutputs() {
    unsigned long now = millis();
    if (now - outputLogTime < 500) return;
    outputLogTime = now;
    if (configLogPending || now - configLogTime >= 10000) {
        configLogPending = false;
        configLogTime = now;
        const feedback_t& p = myRobot->PDterms;
        Serial.printf("[CFG] zEn=%d yawEn=%d rollEn=%d pitchEn=%d rotateEn=%d",
            p.zEn, p.yawEn, p.rollEn, p.pitchEn, p.rotateEn);
        Serial.printf(" kpz=%.9g kdz=%.9g kiz=%.9g z_int_low=%.9g z_int_high=%.9g",
            p.kpz, p.kdz, p.kiz, p.z_int_low, p.z_int_high);
        Serial.printf(" kpyaw=%.9g kppyaw=%.9g kdyaw=%.9g kddyaw=%.9g kiyaw=%.9g kiyawrate=%.9g yawRateIntRange=%.9g",
            p.kpyaw, p.kppyaw, p.kdyaw, p.kddyaw, p.kiyaw, p.kiyawrate, p.yawRateIntRange);
        Serial.printf(" kproll=%.9g kdroll=%.9g kppitch=%.9g kdpitch=%.9g lx=%.9g",
            p.kproll, p.kdroll, p.kppitch, p.kdpitch, p.lx);
        Serial.printf(" servoBeta=%.9g servoRange=%.9g servo_move_min=%.9g botZlim=%.9g pitchOffset=%.9g pitchInvert=%.9g\n",
            p.servoBeta, p.servoRange, p.servo_move_min, p.botZlim, p.pitchOffset, p.pitchInvert);
    }
    Serial.printf("[EXEC] seq=%lu t_us=%lu dt_us=%d pitch_zero=%.3f pz_valid=%d yaw_rate=%.3f imu_stale=%d beh=", commandSequence, micros(), dt,
        myRobot->pitchZero(), (int)myRobot->pitchZeroValid(), myRobot->lastYawRate(), (int)myRobot->imuStale());
    for (int i = 0; i < 5; ++i) {
        if (i) Serial.print(',');
        Serial.printf("%.9g", behave.params[i]);
    }
    Serial.print(" sensors=");
    for (int i = 0; i < 11; ++i) {
        if (i) Serial.print(',');
        Serial.printf("%.9g", senses[i]);
    }
    Serial.printf(" integral=%.9g,%.9g,%.9g",
        myRobot->z_integral, myRobot->yaw_integral, myRobot->yawrate_integral);
    myRobot->printActuatorOutputs();
}

void trackHealth() {
  bool changed = false;
  for (int i = 0; i < 3; ++i) {
    if (senses[3 + i] != lastImuSample[i]) changed = true;
    lastImuSample[i] = senses[3 + i];
  }
  if (changed) ++imuChanges;
  uint8_t count = nicla->niclaFrameCount();
  niclaFrames += (uint8_t)(count - lastNiclaCount);
  lastNiclaCount = count;
}

void resetHealthWindow() {
  healthWindowStart = millis();
  healthCommandStart = commandSequence;
  maxLoopUs = 0;
  imuChanges = 0;
  niclaFrames = 0;
}

void fillTelemetry(int page) {
  rcv.flag = 1;
  if (page == 1) {
    rcv.values[0] = senses[1];  //height
    rcv.values[1] = senses[5];  //yaw
    rcv.values[2] = senses[niclaOffset + 5];  //x
    rcv.values[3] = senses[niclaOffset + 6];  //y
    rcv.values[4] = senses[niclaOffset + 7];  //w
    rcv.values[5] = senses[10];  //battery
  } else if (page == 2) {     // attitude
    rcv.values[0] = senses[3];  // body pitch (IMU X angle)
    rcv.values[1] = senses[4];  // body roll
    rcv.values[2] = senses[6];  // pitch rate
    rcv.values[3] = myRobot->lastYawRate();  // heading rate used by the yaw loop (Euler rate when yawRateEuler)
    rcv.values[4] = behave.params[2]; // height target
    rcv.values[5] = -2;
  } else if (page == 3) {     // outputs
    rcv.values[0] = myRobot->lastActuator(0); // motor 1 (0..1)
    rcv.values[1] = myRobot->lastActuator(1); // motor 2
    rcv.values[2] = myRobot->lastActuator(2); // servo 1 (deg)
    rcv.values[3] = myRobot->lastActuator(3); // servo 2
    rcv.values[4] = behave.params[4]; // yaw target
    rcv.values[5] = -3;
  } else {                    // health since the last page 4
    float seconds = max(0.001f, (millis() - healthWindowStart) / 1000.0f);
    rcv.values[0] = millis() / 1000.0f;            // uptime; drops on a reset/brownout
    rcv.values[1] = imuChanges / seconds;          // IMU sample changes per second
    rcv.values[2] = niclaFrames / seconds;         // camera frames per second
    rcv.values[3] = (commandSequence - healthCommandStart) / seconds; // commands per second
    rcv.values[4] = maxLoopUs / 1000.0f;           // longest loop work time (ms)
    rcv.values[5] = -4;
  }
}

void fixClockRate() {

  dt = (int)(micros()-clockTime);
  if (dt > maxLoopUs) maxLoopUs = dt; // work time of this loop before the wait
  while (TIME_STEP_MICRO - dt > 0){
    dt = (int)(micros()-clockTime);
  }
  clockTime = micros();
}
