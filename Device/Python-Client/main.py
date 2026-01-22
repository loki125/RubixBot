import bleak
import asyncio
import struct


# DEVICE = "40:4C:CA:41:CD:D6"
DEVICE = "40:4C:CA:43:0A:EE"
CHARACTERISTICS = \
{
    "Light": "beb5483e-36e1-4688-b7f5-ea07361b26a8",
}

def callback(sender: bleak.BleakGATTCharacteristic, data: bytearray):
    print(f"{sender}: {data}")


# to get data: got = await client_socket.read_gatt_char(CHARACTERISTICS["My Identifier"])    
# to send data: await client_socket.write_gatt_char(CHARACTERISTICS["My Identifier"], data)
# TODO: Check how to implement non bstring data

async def set_rgb(client_socket, red, green, blue):
    """
    Sets the built in RGB to the given colors.
    data sent as string of 3 chars 0-9 as brightess level.
    """
    # 3 big endian 4 byte floats in series.
    vals = [int(val * 10 // 1) % 10 + 48 for val in (red, green, blue)]
    data = bytes(vals) + b"\x00"
    # data = b"900\x00"
    print(data)
    await client_socket.write_gatt_char(CHARACTERISTICS["Light"], data)

async def main():
    print("Connecting...")
    async with bleak.BleakClient(DEVICE) as client:
        # for characteristic in CHARACTERISTICS.values():
            # await client.start_notify(characteristic, callback) # on change do callback.

        for i in list(range(10)) + [0]: # for from 1-9 then 0.
            await set_rgb(client, i / 10, i/20, 0)
            await asyncio.sleep(0.25) # wait before sending next one.


if __name__ == '__main__':
    asyncio.run(main())