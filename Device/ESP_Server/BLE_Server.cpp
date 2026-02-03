#include "BLECharacteristic.h"
/*
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleServer.cpp
*/
#ifndef Utils_h
#define Utils_h

#include "BLE_Server.h"
#include "Arduino.h"
#include "MyServos.h"

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include "Utils.h"

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

// private functions:
void rgb_read(BLECharacteristic *pCharacteristic);
void servo_read(BLECharacteristic *pCharacteristic);


int connectedClients = 0;

/*
Profile level callbacks, for general connections like users connecting and disconnecting.
*/
class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *pServer) {
    connectedClients++;
    Serial.print("Client connected. Total clients: ");
    Serial.println(connectedClients);
    set_rgb(0, 1, 0);
    delay(500);
  };

  void onDisconnect(BLEServer *pServer) {
    connectedClients--;
    Serial.print("Client disconnected. Total clients: ");
    Serial.println(connectedClients);
    BLEDevice::startAdvertising();
    set_rgb(1, 0, 0);
    delay(500);
  }
};

/*
Characteristics level callbacks, for "events" specifically for Characteristics.
The parameter BLECharacteristic* is a pointer to a the logical characteristic, You can(preferably) use this one instead of the array of the pcharacteristics array.
onWrite(BLECharacteristic*) Gets called when a user writes data into a characteristic.
Not sure for their usages but there's also these possible callbacks:
OnRead(BLECharacteristic*);
OnNotify(BLECharacteristic*);
OnStatus(BLECharacteristic*, Status s, uint32_t code);
*/
class CharacteristicsCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic){ // data was written by different client.
    String Characteristic_UUID = pCharacteristic->getUUID().toString();
    Serial.printf("Characteristic %s Has been modified\n", Characteristic_UUID.c_str());
    
    for (int i = 0; i < SERVO_COUNT; i++){
      if (Characteristic_UUID == SERVO_CHARACTERISTICS_UUIDS[i]){
        servo_read(pCharacteristic);
        return;
      }
    }
    if (Characteristic_UUID == RGB_CHARACTERISTIC_UUID){
      rgb_read(pCharacteristic);
    }
    else {
        Serial.println("Huh? I don't think this characteristic is right...");
    }
  }
};

// CharacteristicsCallbacks callback = new CharacteristicsCallbacks();
BLECharacteristic * pCharacteristics[5] = { nullptr };

void ble_setup() {
  servos_setup();
  Serial.println("Starting BLE work!");

  // String is the name that shows up on adverisement.
  BLEDevice::init("Sisyphus Esp32");
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pDebugService = pServer->createService(DEBUG_SERVICE_UUID);
  pCharacteristics[RGB_CHARACTERISTIC] = pDebugService->createCharacteristic(
    RGB_CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_INDICATE
  );
  pDebugService->start();
  pCharacteristics[RGB_CHARACTERISTIC]->setCallbacks(new CharacteristicsCallbacks());

  BLEService *pServoService = pServer->createService(SERVO_SERVICE_UUID);
  for (int i = 0; i < SERVO_COUNT; i++){
    pCharacteristics[i + 1] = pServoService->createCharacteristic(
      SERVO_CHARACTERISTICS_UUIDS[i],
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_INDICATE
    );
    pCharacteristics[i + 1]->setCallbacks(new CharacteristicsCallbacks());  
  }
  pServoService->start();
  Serial.println("OOE!");
  
  
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(DEBUG_SERVICE_UUID);
  pAdvertising->addServiceUUID(RGB_CHARACTERISTIC_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // "functions that help with iPhone connections issue", not sure if needed but was in the example and I don't see a harm in it. 
  pAdvertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();

  Serial.println("Advertising...");
}

struct RGB_data{
  float red;
  float green;
  float blue;
};

/*
Data is sent as 3 floats repressenting the brightness of each color red, gree, and blue in that order.
*/
void rgb_read(BLECharacteristic *pCharacteristic)
{
  size_t data_length = pCharacteristic->getLength();
  if (data_length != sizeof(struct RGB_data)){
    Serial.println("Invalid data size for RGB Characteristic.");
    return;
  }
  struct RGB_data* data = (RGB_data*)pCharacteristic->getData();
  // struct RGB_data data = pCharacteristics[RGB_CHARACTERISTIC]->getValue();
  set_rgb(data->red, data->green, data->blue);
}

struct Servo_Data{
  unsigned int angle; // angle to set the servo to, 0-180
};

void servo_read(BLECharacteristic *pCharacteristic)
{
  size_t data_length = pCharacteristic->getLength();
  if (data_length != sizeof(struct Servo_Data)){
    Serial.println("Invalid data size for Servo Characteristic.");
    return;
  }
  struct Servo_Data* data = (Servo_Data*)pCharacteristic->getData();
  unsigned int angle = data->angle;
  
  String Characteristic_UUID = pCharacteristic->getUUID().toString();
  if (Characteristic_UUID == SERVO_LEFT_CHARACTERISTIC_UUID)
      set_servo_pos(SERVO_LEFT, angle);
  else if (Characteristic_UUID == SERVO_RIGHT_CHARACTERISTIC_UUID)
      set_servo_pos(SERVO_RIGHT, angle);
  else if (Characteristic_UUID == SERVO_UP_CHARACTERISTIC_UUID)
      set_servo_pos(SERVO_UP, angle);
  else if (Characteristic_UUID == SERVO_DOWN_CHARACTERISTIC_UUID) // last check isn't needed but feels more "correct"
      set_servo_pos(SERVO_DOWN, angle);
  // assuming the check was done before we needn't check invalid input.
}

void ble_loop() {
  // put your main code here, to run repeatedly:
}

#endif
