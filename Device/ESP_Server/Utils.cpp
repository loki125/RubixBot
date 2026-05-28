#ifndef Utils_h
#define Utils_h

#include "Utils.h"
#include "Arduino.h"

void set_rgb(float red, float green, float blue)
{
#ifdef RGB_BUILTIN
  rgbLedWrite(RGB_BUILTIN,
    red * RGB_BRIGHTNESS, 
    green * RGB_BRIGHTNESS, 
    blue * RGB_BRIGHTNESS
  );  // Red
#endif 
}

#endif