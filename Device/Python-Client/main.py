import asyncio
from enum import Enum
import socket

import cv2
import numpy as np
import requests


class CameraClient:
    def __init__(self):
        ip_address = socket.gethostbyname("RubikCamera")
        self.camera_url = f"http://{ip_address}/capture"

    def get_image(self):
        answer = requests.get(self.camera_url)
        if answer.status_code != 200:
            return None
        img_np = np.asarray(bytearray(answer.content), dtype=np.uint8)
        img = cv2.imdecode(img_np, -1)
        return img

class ServoType(Enum):
    SPIN = 0
    TOP = 1

class ServoClient:
    # Site/api/servo{1/2}/{0-180}
    def __init__(self):
        ip_address = socket.gethostbyname("EspServoController")
        print(f"ip_address: {ip_address}")
        self.color_format = "http://{ip}/api/color/{}".replace("{ip}", ip_address)
        self.servo_format = "http://{ip}/api/servo/{}/{}".replace("{ip}", ip_address)

    async def set_rgb(self, red, green, blue):
        """
        Sets the built-in RGB to the given colors.
        Parameters type: float
        """
        hexed_color = "".join([hex(int(x * 255))[2:].rjust(2, '0') for x in (red, green, blue)])
        url = self.color_format.format(hexed_color)
        return requests.post(url)

    async def _angle_servo(self, servo: ServoType, angle):
        if servo == ServoType.SPIN:
            servo_num = 1
        else:
            servo_num = 2
        url = self.servo_format.format(servo_num, int(angle))
        return requests.post(url)

    async def egg(self):
        pass


async def main():
    print("Connecting...")
    cli = ServoClient()
    got = await cli.set_rgb(15 / 255, 0.0, 0.0)
    for x in range(0, 181, 180 // 4):
        got = await cli._angle_servo(ServoType.SPIN, x)
        # await asyncio.sleep(0.5)
        got = await cli.angle_servo(ServoType.TOP, x)
        print(got.content)
        await asyncio.sleep(0.5)
    got = await cli.angle_servo(ServoType.SPIN, 0)
    got = await cli.angle_servo(ServoType.TOP, 0)


if __name__ == '__main__':
    asyncio.run(main())
