/*
 Don't have the servos' yet so leave this here so these will be functions.
*/

#define SERVO_COUNT 4

enum RUBIK_SERVO{
  SERVO_LEFT = 0,
  SERVO_RIGHT,
  SERVO_UP,
  SERVO_DOWN
};

void servos_setup();

void set_servo_pos(enum RUBIK_SERVO, int angle);

void servos_loop();