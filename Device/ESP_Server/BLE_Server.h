// BLE - Bluetooth Low Energy.

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define RGB_CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

/*
Sets up the bluetooth server.
*/
void ble_setup();

/*
Run every loop to handle the bluetooth server.
*/
void ble_loop();