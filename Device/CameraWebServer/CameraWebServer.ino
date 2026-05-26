#include "esp_camera.h"
#include <WiFi.h>

// ===========================
// Select camera model in board_config.h
// ===========================
#include "board_config.h"
#include "wifi_credentials.h"

void startCameraServer();
void setupLedFlash();

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  
  // OPTIMIZATION 1: Use SVGA (800x600). It's the sweet spot. 
  // UXGA is too slow/large, QVGA is too blurry for edge detection.
  config.frame_size = FRAMESIZE_SVGA; 
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  
  // OPTIMIZATION 2: Lower number = less compression/fewer artifacts.
  // Crucial so cv.Canny doesn't pick up JPEG noise as cube edges.
  config.jpeg_quality = 10; 
  config.fb_count = 1;

  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10; // Keep quality high even with PSRAM
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST; // Ensures Python always gets the newest frame
    } else {
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  // OPTIMIZATION 3: Configure Sensor specifically for Computer Vision
  sensor_t *s = esp_camera_sensor_get();
  
  // Flip image if necessary (depends on how your camera is mounted)
  s->set_vflip(s, 1); 
  // s->set_hmirror(s, 1); // Uncomment if left/right are inverted

  // --- COMPUTER VISION TWEAKS ---
  s->set_brightness(s, 0);     // 0 prevents washing out white/yellow colors
  s->set_contrast(s, 1);       // +1 Higher contrast helps Canny Edge Detection find the grid
  s->set_saturation(s, 2);     // +2 Boost saturation! This forces Red/Orange to be distinctly different
  s->set_sharpness(s, 1);      // +1 Sharpens the physical black lines on the cube
  
  s->set_whitebal(s, 1);       // Enable Auto White Balance
  s->set_awb_gain(s, 1);       // Enable AWB Gain
  s->set_wb_mode(s, 0);        // 0 = Auto. (If you use a specific desk lamp, set to 2 or 3 for consistency)
  s->set_exposure_ctrl(s, 1);  // Auto Exposure on
  s->set_aec2(s, 0);           // Disable DSP AEC (prevents weird brightness flickering)
  s->set_bpc(s, 1);            // Black pixel correction
  s->set_wpc(s, 1);            // White pixel correction
  s->set_raw_gma(s, 1);        // Gamma correction
  s->set_lenc(s, 1);           // Lens correction (removes dark corners)

#if defined(LED_GPIO_NUM)
  setupLedFlash();
#endif

  WiFi.setHostname(SELF_NETWORK_HOSTNAME);
  WiFi.begin(NETWORK_SSID, NETWORK_PASSWORD);
  WiFi.setSleep(false);

  Serial.println("WiFi connecting");
  for (int connection_attempts=0; WiFi.status() != WL_CONNECTED; connection_attempts++){
    Serial.print("\r"); 
    Serial.print(connection_attempts);
    delay(500);
  }
  Serial.println("\nWiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://"); 
  Serial.print(WiFi.localIP()); 
  Serial.println("' to connect");
}

void loop() {
  // Do nothing. Everything is done in another task by the web server
  delay(10000);
}