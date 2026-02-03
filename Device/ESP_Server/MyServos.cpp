#ifndef MyServos_h
#define MyServos_h

#include "MyServos.h"
#include <ESP32Servo.h>

// #include <Arduino.h>

const int servoPins[SERVO_COUNT] = {
	18, 19, 21, 22
};

// If the servo's angles aren't perfect try to change these min and max values.
int minUs = 500;
int maxUs = 2500;

Servo myServos[SERVO_COUNT];

void servos_setup(){
  // The library's example reserved all timers from the board, not sure if entirely nessesary, I'll keep unless it breaks something else.
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	for (int i = 0; i < SERVO_COUNT; i++){
		myServos[i].setPeriodHertz(50);    // Most servos use a 50 hz pwm frequency.
		// myServos[i].attach(servoPins[i], minUs, maxUs); // Attaches the servo and identifies the min and max power signal.
	}
	for (int i = 0; i < SERVO_COUNT; i++){
		// myServos[i].setPeriodHertz(50);    // Most servos use a 50 hz pwm frequency.
		myServos[i].attach(servoPins[i], minUs, maxUs); // Attaches the servo and identifies the min and max power signal.
	}
  Serial.println("Servos running!");
}

void set_servo_pos(enum RUBIK_SERVO servo_id, int angle){
	myServos[servo_id].write(angle);
}

void servos_loop(){

}

#endif