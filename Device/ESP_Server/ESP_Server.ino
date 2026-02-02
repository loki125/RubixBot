#include "BLE_Server.h"
#include "Utils.h"
#include "MyServos.h"

void setup() {
  Serial.begin(115200); // I figured out what messed up with the serial monitor :D. It should work if connected to the right usb-c port on the board.
  set_rgb(0.3, 0, 0); // low red to signal startup.

  // ble_setup();
  servos_setup();
  Serial.println("Ready!");

}

void loop() {
  // ble_loop();
  servos_loop();
  if (Serial.available()){
  set_servo_pos(SERVO_LEFT, 180);
  delay(2000);
  set_servo_pos(SERVO_LEFT, 0);
  Serial.println(Serial.readString());
  }
}
