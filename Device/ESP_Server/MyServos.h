
#define SERVO_COUNT 2

enum RUBIK_SERVO{
  SERVO_SPIN = 0,
  SERVO_TOP,
};

void servos_setup();

void set_servo_pos(enum RUBIK_SERVO, int angle);

void servos_loop();