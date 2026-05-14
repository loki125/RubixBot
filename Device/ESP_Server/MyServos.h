/*
  We'll have 8 servos total, in pairs of side(left/right/up/down) and (push/spin) as one servo pushes the other on the cube to cause friction and the other spins to rotate the cube.
*/

#define SERVO_COUNT 2

enum RUBIK_SERVO{
  SERVO_SPIN = 0,
  SERVO_TOP,
};

void servos_setup();

void set_servo_pos(enum RUBIK_SERVO, int angle);

void servos_loop();