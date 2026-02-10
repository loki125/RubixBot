import bleak
import asyncio
import struct

# DEVICE = "40:4C:CA:41:CD:D6"
DEVICE = "40:4C:CA:43:0A:EE"
CHARACTERISTICS = \
    {
        "Light": "beb5483e-36e1-4688-b7f5-ea07361b26a8",
        "ServoLeft": "5a41dac7-2769-4b4f-96e1-26c49c7b50d4",
        "ServoRight": "7ddf96a9-6145-4e9e-bee8-85a4257347b3",
        "ServoUp": "3599075c-c02b-4318-900f-33d24a525e3d",
        "ServoDown": "83400224-6ec6-4151-8228-d8ae396ded4b"
    }


class BLEConnection:
    """
    Wrapper for the bleak client.
    Should make it easy to handle the server connection like this without really going into the bleak docs.
    """

    def __init__(self, device_address, debug=False):
        # TODO: scan devices to find our device instead of using a hardcoded address.
        self._connection = bleak.BleakClient(device_address)
        self._debug = debug

    async def set_characteristic_value(self, identifier: str, struct_format, *data, print_data=False):
        """
        Helper function to send data over the BLE.
        identifier (str): UUID of the characteristic as str.
        struct_format (str): The format to send the data as, refer to the struct library formatting,
        maximum should be 20 bytes but haven't checked.
        *data (any): The data to format, in order of the struct format.
        """
        data = struct.pack(struct_format, *data)
        if print_data:
            print(data.hex())
        await self._connection.write_gatt_char(CHARACTERISTICS[identifier], data)

    ### Enter and exit methods are for "with ble_connection", to make sure the socket closes correctly.
    # since our connection implemented them we can send the data to the connection under us, 
    async def __aenter__(self):
        await self._connection.connect()
        # for characteristic in CHARACTERISTICS.values():
        # await client.start_notify(characteristic, callback) # on change do callback.
        if self._debug:
            print("Connected with:", self._connection.name)
            services = self._connection.services
            print(f"Services({len(services.services)}): {services}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._connection.disconnect()
        if exc_type is not None and self._debug:
            print("Disconnected with:", self._connection.name)
            print("Exception occurred:", exc_val)
            return False
        return None


# we can get also data: got = await _connection.read_gatt_char(CHARACTERISTICS["Identifier"]).
# It is highly preferable to use the callback function rather than getting it directly.
# Unimplemented as the camera hasn't arrived.
def callback(sender: bleak.BleakGATTCharacteristic, data: bytearray):
    """
    Gets called when the server calls notify, data may change but this will only get called when server calls notify().
    Made so there won't be a mutex issue where one is reading the value while it's changing.
    """
    uuid = sender.uuid
    if uuid == CHARACTERISTICS["Light"]:
        print("Light characteristic was written to")
        # on_light_write(sender, data)
    print(f"Data received from {sender}: {data}")


async def set_rgb(connection: BLEConnection, red, green, blue):
    """
    Sets the built-in RGB to the given colors.
    data sent as 3 floats representing red, green and blue values in that order.
    """
    await connection.set_characteristic_value("Light", "<3f", red, green, blue)


async def set_angle(connection: BLEConnection, servo, angle):
    servos = ["ServoLeft", "ServoRight", "ServoUp", "ServoDown"]
    await connection.set_characteristic_value(servos[servo], "I", angle)


async def main():
    print("Connecting...")
    client = BLEConnection(DEVICE, debug=True)
    async with client:
        for i in range(4):
            await set_angle(client, i, 90)
            await asyncio.sleep(1)  # wait before sending next one.
            await set_angle(client, i, 180)
            await asyncio.sleep(1)  # wait before sending next one.
            await set_angle(client, i, 0)
            await asyncio.sleep(1)  # wait before sending next one.


if __name__ == '__main__':
    asyncio.run(main())
