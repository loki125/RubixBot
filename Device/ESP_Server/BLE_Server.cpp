/*
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleServer.cpp
*/
#ifndef Utils_h
#define Utils_h

#include "Arduino.h"

#include "BLE_Server.h"

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include "Utils.h"

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

int connectedClients = 0;

class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *pServer) {
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

enum CHARACTERISTICS {
  RGB_CHARACTERISTIC = 0,
};

BLECharacteristic * pCharacteristics[] = { nullptr, };

void ble_setup() {
  Serial.println("Starting BLE work!");

  // String is the name that shows up on adverisement.
  BLEDevice::init("Sisyphus Esp32");
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristics[RGB_CHARACTERISTIC] = pService->createCharacteristic(
    RGB_CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_INDICATE
  );
  // pCharacteristic[x]->setValue("Hello World says Sisyphus");
  // pCharacteristic[x]->getValue();
  
  pService->start();
  
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();

  Serial.println("Advertising...");
}

// TODO: Check how to implement non string data

/*
data sent as string of 3 chars 0-9 as brightess level.
*/
void check_rgb()
{
  String data = pCharacteristics[RGB_CHARACTERISTIC]->getValue();
  float red = float((char)data[0] - 48) / 10.0;
  float green = float((char)data[1] - 48) / 10.0;
  float blue = float((char)data[2] - 48) / 10.0;
  set_rgb(red, green, blue);
}

void ble_loop() {
  check_rgb();
  // put your main code here, to run repeatedly:
  delay(100);
}

#endif
