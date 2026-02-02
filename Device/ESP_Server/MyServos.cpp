#ifndef MyServos_h
#define MyServos_h

#include "MyServos.h"
#include <ESP32Servo.h>

// #include <Arduino.h>

const int servoPin = 18;
Servo myServo;

/*
This is basic version of the servo program to test it.
There's a multiple servo example in which they attach and detach the servos from the loop which I don't understand why.
There's also an idea I had to have it in an array, but seeing the example makes me want to test it first and I'll just do it a different time, (Got tired after spending 3 hours only to figure out both the pins I tested were used by the library and that's why it wasn't working.)
*/

void servos_setup(){
  // The library's example reserved all timers from the board, not sure if entirely nessesary, I'll keep unless it breaks something else.
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myServo.setPeriodHertz(50);    // Most servos use a 50 hz pwm frequency.
	myServo.attach(servoPin, 500, 2500); // Attaches the servo and identifies the min and max power signal.
  // If the servo's angles aren't perfect try to change these min and max values.
}

void set_servo_pos(enum RUBIK_SERVO, int angle){
	myServo.write(angle);
}

void servos_loop(){
}

#endif