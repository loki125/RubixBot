#ifndef MyWebServer_h
#define MyWebServer_h

#include "ServoWebServer.h"
#include "HttpInfo.h"
#include "Utils.h"
#include "MyServos.h"

// #include <Arduino.h>
#include <WebServer.h>
#include <WiFi.h>

#include <uri/UriRegex.h>

WebServer server(80);

// Site/api/servo{1/2}/{0-180}
void processServoRequest(){
  Serial.println(F("Starting_check"));
  int servo_number = server.pathArg(0).toInt() - 1; // no need to check for valid number cause regex did as well.
  Serial.println("servo numbered.");
  int angle_number = server.pathArg(1).toInt(); // same thing just need to make sure it's within 180 degrees.
  Serial.println("Hello there.");
  if (angle_number > 180) {
    server.send(400, "text/plain", "Invalid angle");
    return;
  } // we don't check '-' sign so only positives
  // servo logic goes here.
  set_servo_pos(
    (RUBIK_SERVO)servo_number,
    angle_number
  );

  char state[100] = { 0 };

  sprintf(state, "Servo<{%d}> set to angle({%d})", servo_number, angle_number);

  Serial.println(state);
  server.send(200, "text/plain", state);
}

void processColorRequest(){
  String hex_value = server.pathArg(0);
  // given input is 6 characters of 0-9 or a-f or A-F
  float rgb[3] = { 0.0 };
  int val = 0;
  for (int i = 0; i < 6; i++){
    char hex_val = hex_value[i];
    if (hex_val >= 'a'){ // Checks them in order of biggest ascii value so it will always happen in order.
      val += hex_val - 'a' + 10; 
    }
    else if (hex_val >= 'A'){
      val += hex_val - 'A' + 10;
    }
    else{
      val += hex_val - '0';
    }
    if (i % 2){ // if odd.
      rgb[i / 2] = val / 255.0;
      val = 0;
    }
    else{
      val *= 16;
    }
  }
  set_rgb(rgb[0], rgb[1], rgb[2]);
  Serial.println("Resetting color to: " + hex_value);
  server.send(200, "text/plain", "Color set to: " + hex_value);
}

void webserver_setup(){
  servos_setup();

  WiFi.setHostname(DEVICE_HOSTNAME);

  WiFi.mode(WIFI_STA);
  if (strlen(NETWORK_SSID) == 0) { // if no network name then act as independent network
    WiFi.begin();
    Serial.println("No wifi network given, acting as server");
  } else {
    WiFi.begin(NETWORK_SSID, NETWORK_PASSWORD);
    Serial.printf("Connecting to %s\n", NETWORK_SSID);
  }

  Serial.println(F("Connect to WiFi...\n"));
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println(".");
  }
  Serial.println(F("connected.\nConnect on{}\n"));

  server.on("/", HTTP_GET, []() { // entering the site without any /api after.
    Serial.println(F("Get message got."));
    server.send(200, "text/html", FPSTR(mainPage));
  });

  // Regex checks: /api/servo/{1-2}/{0-infinity}, Eg: /api/servo/1/180
  // 1-2 is for which servo we should activate, last number is the angle, makes it easier to check the angle with code since the servo sets might have different angles and checking for 180 with regex is quite the connundrum anyway.
  // also, the ^ is for start of the string, and $ is for the end, so we don't have like foo/api/servo1/180/bar or anything. Makes it very strict
  server.on(UriRegex("^\\/api\\/servo\\/([1-2])\\/([0-9]+)$"), processServoRequest);
  
  // Checks for RGB in hex values. Eg: /api/color/#FF0000
  server.on(UriRegex("^\\/api\\/color\\/#?([A-Fa-f0-9]{6})$"), processColorRequest);

  server.begin();
	Serial.print(F("Open <http://"));
  Serial.print(F(WiFi.getHostname()));
  Serial.print(F(" or "));
  Serial.print(F(WiFi.localIP().toString().c_str()));
  Serial.print("\n");
}


void webserver_loop(){
  server.handleClient();

  servos_loop;
}

#endif