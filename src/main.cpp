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

// Setup software serial port 
SoftwareSerial mySerial(10, 11);      // Uno RX (TFMINI TX), Uno TX (TFMINI RX)
TFMini tfmini;

void sendDataOverSerial(uint8_t location_id, uint16_t distance, uint16_t signal_strength, unsigned long timestamp){
  Serial.print("{\"location_id\": ");
  Serial.print(location_id);
  Serial.print(", \"timestamp\": ");
  Serial.print(timestamp);
  Serial.print(", \"distance\": ");
  Serial.print(distance);
  Serial.print(", \"signal_strength\": ");
  Serial.print(signal_strength);
  Serial.println("}");
}

void setup() {
  // Step 1: Initialize hardware serial port (serial debug port)
  Serial.begin(115200);
  delay(100);
  // wait for serial port to connect. Needed for native USB port only
  while (!Serial);
     
  Serial.println ("Initializing...");

  // Step 2: Initialize the data rate for the SoftwareSerial port
  mySerial.begin(TFMINI_BAUDRATE); //this is also 115200bd

  // Step 3: Initialize the TF Mini sensor
  tfmini.begin(&mySerial);  
  delay(10);  
}


void loop() {
  uint16_t dist = tfmini.getDistance();
  uint16_t strength = tfmini.getRecentSignalStrength();

  // Serial.print(dist);
  // Serial.print(" cm      sigstr: ");
  // Serial.println(strength);
  sendDataOverSerial(5, dist, strength, millis());

  delay(10); 
}