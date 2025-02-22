#include <Arduino.h>
#include <SoftwareSerial.h>
#include "TFMini.h"


#define BUTTON_PIN 8 // Input Capture Pin (ICP)

#define BLOCKED 1
#define NOT_BLOCKED 0

#define CAR_LENGTH 0.1016 // 4 inches to meters.
#define TRAIN_WATCH_TIMEOUT 2 // 2 seconds.
#define TRAIN_CAR_GAP_TIME_ALLOTMENT 2 // 2 seconds.

SoftwareSerial mySerial(10, 11);      // Uno RX (TFMINI TX), Uno TX (TFMINI RX) //10 gr
TFMini tfmini;


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);

  Serial.begin(TFMINI_BAUDRATE); //115200 sends the bits too fast so they get corrupt.
  tfmini.begin(&mySerial);
  Serial.println("Setup Complete");
}

void sendDataOverSerial(uint8_t location_id, uint16_t blocked_time, unsigned long timestamp){
  Serial.print("{\"location_id\": ");
  Serial.print(location_id);
  Serial.print(", \"timestamp\": ");
  Serial.print(timestamp);
  Serial.print(", \"blocked_time\": ");
  Serial.print(blocked_time);
  Serial.println("}");
}

void updateHoldCycles(int buttonState, uint8_t* holdValue, uint16_t* holdCycles){
  if (buttonState == *holdValue){
    holdCycles++;
  } else { // value changed
    *holdValue = buttonState;
    *holdCycles = 1;
  }
}

void updateTrainIsPresent(uint8_t holdValue, uint16_t holdCycles, bool* train_is_present){
  // sensor is not blocked for longer than the TRAIN_WATCH_TIMEOUT time
  *train_is_present = (holdValue == 0) && (holdCycles > TRAIN_WATCH_TIMEOUT);
}

void updateElapsedBlockedTime(uint8_t holdValue, uint16_t holdCycles, uint16_t* elapsed_blocked_time){
  if (holdValue == BLOCKED){

  }
}

void loop() {
  static uint8_t holdValue = 0;
  static uint16_t holdCycles = 0;
  static bool train_is_present = 0;
  static uint16_t elapsed_blocked_time = 0;
  Serial.print("first");
  uint16_t dist = tfmini.getDistance();
  Serial.print("second");
  uint16_t strength = tfmini.getRecentSignalStrength();
  
  int buttonState = digitalRead(BUTTON_PIN);
  digitalWrite(LED_BUILTIN, buttonState ? HIGH : LOW);
  updateHoldCycles(buttonState, &holdValue, &holdCycles);
  updateTrainIsPresent(holdValue, holdCycles, &train_is_present);
  sendDataOverSerial(5, holdCycles, millis());
}