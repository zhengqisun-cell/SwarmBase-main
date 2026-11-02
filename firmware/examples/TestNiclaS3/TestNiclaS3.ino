// Bench test for the Nicla Vision link on a generic ESP32-S3 board.
// Uses UART1 on GPIO18/17 so it never shares GPIO43/44 with a USB-UART bridge.
// Wiring: Nicla J2-3 UART_TX -> GPIO18, Nicla J2-4 UART_RX <- GPIO17, GND <-> GND.
// Type b / y / o / d + Enter in the monitor to send 0x40 / 0x80 / 0x81 / 0x41.

#include <Arduino.h>
#include <IBusBM.h>

#define NICLA_RX_PIN 18
#define NICLA_TX_PIN 17

HardwareSerial NiclaSerial(1);
IBusBM IBus;
uint8_t lastRec = 0;
unsigned long printTime = 0;

void sendMode(uint8_t mode) {
  NiclaSerial.write(mode);
  Serial.printf("[MODE] sent 0x%02X\n", mode);
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  IBus.begin(NiclaSerial, IBUSBM_NOTIMER, NICLA_RX_PIN, NICLA_TX_PIN);
  Serial.printf("TestNiclaS3: RX=GPIO%d TX=GPIO%d 115200 8N1\n", NICLA_RX_PIN, NICLA_TX_PIN);
  sendMode(0x40);
}

void loop() {
  IBus.loop();

  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'b') sendMode(0x40);
    else if (c == 'y') sendMode(0x80);
    else if (c == 'o') sendMode(0x81);
    else if (c == 'd') sendMode(0x41);
  }

  if (millis() - printTime >= 100) {
    printTime = millis();
    uint8_t rec = IBus.cnt_rec;
    uint8_t frames = rec - lastRec;
    lastRec = rec;
    uint16_t flag = IBus.readChannel(0);
    const char* mode = (flag & 0x80) ? "goal" : (flag & 0x40) ? "balloon" : "none";
    Serial.printf("frames/100ms=%u flag=0x%02X mode=%s det=%u ch=", frames, flag, mode, flag & 0x03);
    for (int i = 0; i < 10; i++) {
      if (i) Serial.print(',');
      Serial.print(IBus.readChannel(i));
    }
    Serial.println();
  }
}
