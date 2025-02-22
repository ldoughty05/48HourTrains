/*
This example communicates to the TFMini using a SoftwareSerial port at 115200, 
while communicating the distance results through the default Arduino hardware
Serial debug port. 

SoftwareSerial for some boards can be unreliable at high speeds (such as 115200). 
The driver includes some limited error detection and automatic retries, that
means it can generally work with SoftwareSerial on (for example) an UNO without
the end-user noticing many communications glitches, as long as a constant refresh
rate is not required. 

The (UNO) circuit:
 * Uno RX is digital pin 10 (TX/Green of TF Mini)
 * Uno TX is digital pin 11 (RX/White of TF Mini)

*/
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "TFMini.h"

#define BLOCKED 1
#define NOT_BLOCKED 0

#define SENSOR_DISTANCE_FROM_TRAIN 5
#define CAR_LENGTH 0.1016 // 4 inches to meters.
#define TRAIN_WATCH_TIMEOUT 2 // 2 seconds.
#define TRAIN_CAR_GAP_TIME_ALLOTMENT 2 // 2 seconds.

// Setup software serial port 
SoftwareSerial mySerial(10, 11);      // Uno RX (TFMINI TX), Uno TX (TFMINI RX)
TFMini tfmini;

void sendDataOverSerial(uint8_t locationId, uint16_t distance, uint16_t signalStrength, bool isBlocked, uint16_t trainVelocity, unsigned long timestamp){
  Serial.print("{\"location_id\": ");
  Serial.print(locationId);
  Serial.print(", \"distance\": ");
  Serial.print(distance);
  Serial.print(", \"signal_strength\": ");
  Serial.print(signalStrength);
  Serial.print(", \"is_blocked\": ");
  Serial.print(isBlocked);
  Serial.print(", \"train_velocity\": ");
  Serial.print(trainVelocity);
  Serial.print(", \"timestamp\": ");
  Serial.print(timestamp);
  Serial.println("}");
}

void setup() {
  // Step 1: Initialize hardware serial port (serial debug port)
  Serial.begin(TFMINI_BAUDRATE);
  delay(100);
  // wait for serial port to connect. Needed for native USB port only
  while (!Serial);
     
  Serial.println ("Initializing...");

  // Step 2: Initialize the data rate for the SoftwareSerial port
  mySerial.begin(TFMINI_BAUDRATE); //this is also 115200bd

  // Step 3: Initialize the TF Mini sensor
  tfmini.begin(&mySerial);  
  delay(10);  
  Serial.println ("Ready.");
}

bool getIsBlocked(uint16_t lidar_distance){
  return lidar_distance <= SENSOR_DISTANCE_FROM_TRAIN;
}

void updateHoldTime(int buttonState, uint8_t* holdValue, unsigned long* leadingEdgeTime, unsigned long* holdTime){
  if (buttonState == *holdValue){
    *holdTime = millis() - *leadingEdgeTime;
  } else { // value changed
    *holdValue = buttonState;
    *leadingEdgeTime = millis();
    *holdTime = 0;
  }
}

void updateTrainIsPresent(uint8_t holdValue, unsigned long holdTime, uint8_t* numCars, unsigned long* timeTrainFirstFound, unsigned long* elapsedBlockTime, bool* trainIsPresent){
  // sensor is not blocked for longer than the TRAIN_WATCH_TIMEOUT time
  if (!(*trainIsPresent) && ((holdValue == 1) || (holdTime < TRAIN_WATCH_TIMEOUT))){
    // First time seeing the train.
    *timeTrainFirstFound = millis();
    *trainIsPresent = true;
  } else if(*trainIsPresent && (holdValue == 0)){
    if (holdTime >= TRAIN_WATCH_TIMEOUT){
      // Train was here but it's gone now.
      *elapsedBlockTime = millis() - *timeTrainFirstFound;
      *trainIsPresent = false;
    } else if (holdTime == 0){ // we can expect this to be exactly zero because updateHoldTime detected the value changed THIS cycle.
      // This is just a gap. Train is probably still going.
      *numCars++;
    }
  }
}

void updateVelocity(uint8_t numCars, unsigned long elapsedBlockTime, uint16_t* trainVelocity){
  // An alternative (and probably better) implementation would get the velocity for each cart.
  // This implementation tries to take an average for the whole train, but it does not currently take the gaps into account.
  *trainVelocity = numCars * CAR_LENGTH / elapsedBlockTime;
}


void loop() {
  static uint8_t holdValue = 0;
  static unsigned long leadingEdgeTime = 0; // the time stamp for whenever blocked first changed to BLOCKED or NOT_BLOCKED.
  static unsigned long holdTime = 0; // how long the reading has stayed either BLOCKED or NOT_BLOCKED.
  static bool trainIsPresent = 0;
  static uint8_t numCars = 0;
  static unsigned long elapsedBlockTime = 0;
  static unsigned long timeTrainFirstFound = 0;
  static uint16_t trainVelocity = 0;
  uint16_t strength = tfmini.getRecentSignalStrength();
  uint16_t dist = tfmini.getDistance();
  bool isBlocked = getIsBlocked(dist);

  updateHoldTime(isBlocked, &holdValue, &leadingEdgeTime, &holdTime);
  updateTrainIsPresent(holdValue, holdTime, &numCars, &timeTrainFirstFound, &elapsedBlockTime, &trainIsPresent);
  updateVelocity(numCars, elapsedBlockTime, &trainVelocity);
  sendDataOverSerial(5, dist, strength, isBlocked, trainVelocity, millis());

  delay(100); 
}