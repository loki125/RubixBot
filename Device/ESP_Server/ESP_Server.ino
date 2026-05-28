#include "Utils.h"
#include "ServoWebServer.h"

void setup() {
  // Serial.begin(115200); // I figured out what messed up with the serial monitor :D. It should work if connected to the right usb-c port on the board.
  // set_rgb(0.3, 0, 0); // low red to signal startup.

  webserver_setup();
  // Serial.println("Ready!");
}

void loop() {
  webserver_loop();
}
