import bleak
import asyncio
import struct


# DEVICE = "40:4C:CA:41:CD:D6"
DEVICE = "40:4C:CA:43:0A:EE"
CHARACTERISTICS = \
{
    "Light": "beb5483e-36e1-4688-b7f5-ea07361b26a8",
}

class BLE_Connection:
    def __init__(self, device_address, debug=False):
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
        print("Enter")
        a = await self._connection.__aenter__(*args, **kwargs) # can also do connection.connect which is what's in the aenter but yes :D
        print(a)
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


# to get data: got = await client_socket.read_gatt_char(CHARACTERISTICS["My Identifier"])    
# to send data: await client_socket.write_gatt_char(CHARACTERISTICS["My Identifier"], data)
# TODO: Check how to implement non bstring data

async def set_rgb(connection: BLE_Connection, red, green, blue):
    """
    Sets the built in RGB to the given colors.
    data sent as string of 3 chars 0-9 as brightess level.
    """
    await connection.set_characteristic_value("Light", "<3f", red, green, blue, print_data=True)

async def main():
    print("Connecting...")
    async with BLE_Connection(DEVICE, debug=True) as client:

        for i in list(range(16)) + [0]: # for from 1-9 then 0.
            await set_rgb(client, i / 16, i / 32, i / 64)
            await asyncio.sleep(0.25) # wait before sending next one.


if __name__ == '__main__':
    asyncio.run(main())