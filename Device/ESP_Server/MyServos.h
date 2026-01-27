/*
 Don't have the servos' yet so leave this here so these will be functions.
*/

enum RUBIK_SERVO{
  Left = 0,
  Right,
  Up,
  down
};

void servos_setup();

void set_servo_pos(enum RUBIK_SERVO, int angle);

void servos_loop();