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

class BLE_Connection:
    """
    Wrapper for the bleak client, should make it easy to handle the server connection like this without really going into the bleak docs.
    """
    def __init__(self, device_address, debug=False):
        # TODO: scan devices to find our device instead of using a hardcoded address.
        self._connection = bleak.BleakClient(device_address)
        self._debug = debug

    async def set_characteristic_value(self, identifier: str, struct_format, *data, print_data = False):
        """
        Helper function to send data over the BLE.
        identifier (str): UUID of the characteristic as str.
        struct_format (str): The format to send the data as, refer to the struct library formatting, maximum should be 20 bytes but haven't checked.
        *data (any): The data to format, in order of the struct format.
        """
        data = struct.pack(struct_format, *data)
        if print_data:
            print(data.hex())
        await self._connection.write_gatt_char(CHARACTERISTICS[identifier], data)

    ### Enter and exit methods are for "with ble_connection", to make sure the socket closes correctly.
    # since our connection implemented them we can send the data to the connection under us, 
    async def __aenter__(self, *args, **kwargs):
        a = await self._connection.__aenter__(*args, **kwargs) # can also do connection.connect which is what's in the aenter but yes :D
        # for characteristic in CHARACTERISTICS.values():
            # await client.start_notify(characteristic, callback) # on change do callback.
        if self._debug: 
            print("Connected with:", self._connection.name)
            services = self._connection.services
            print(f"Services({len(services.services)}): {services}")
        return self

    async def __aexit__(self, *args, **kwargs):
        print("Exit")
        a = await self._connection.__aexit__(*args, **kwargs)
        return a


# we can get also data: got = await _connection.read_gatt_char(CHARACTERISTICS["Identifier"]), Though it is highly preferrable to use the callback function.
# Also note that we didn't connect the callback to the bluetooth connection as I don't have exactly a reason to use it for now I left it unimplemented.
def callback(sender: bleak.BleakGATTCharacteristic, data: bytearray):
    """
    Gets called when the server calls notify, data may change but this will only get called when server calls notify().
    Made so there won't be a mutex issue where one is reading the value while it's changing.
    """
    uuid = sender.uuid
    if uuid == CHARACTERISTICS["Light"]:
        print("Light characteristic was written to") 
        # on_light_write(sender, data)
    print(f"Data recieved from {sender}: {data}")


async def set_rgb(connection: BLE_Connection, red, green, blue):
    """
    Sets the built in RGB to the given colors.
    data sent as 3 floats repressenting red, green and blue values in that order.
    """
    await connection.set_characteristic_value("Light", "<3f", red, green, blue, print_data=True)

async def main():
    print("Connecting...")
    async with BLE_Connection(DEVICE, debug=True) as client:

        for i in list(range(18)) + [0]:
            # await set_rgb(client, i / 16, i / 32, i / 64)
            await client.set_characteristic_value("ServoRight", "I", i * 10)
            await asyncio.sleep(0.25) # wait before sending next one.


if __name__ == '__main__':
    # Async functions let us control code flow in a unique way so that if we need to wait for something the program can do other things at the same time.
    # Kind of like threads doing multiple things in multiple spots of code, but in one thread, can indeed have issues but can be highly usefull.
    # For example getting many images at once, if we need to download many images then we ask for many and if one's still loading then we go for a different one. 
    asyncio.run(main())