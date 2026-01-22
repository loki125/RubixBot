#include "BLE_Server.h"
#include "Utils.h"

void setup() {
  Serial.begin(115200); // Serial monitor doesn't seem to work with our chip so debug doesn't work but I rather keep this in case we swap it somewhen.
  set_rgb(0.3, 0, 0); // red means not ready.

  ble_setup();

}

void loop() {
  ble_loop();
}
