import socket
import urllib.request
from enum import Enum


class ServoType(Enum):
    SPIN = 0
    TOP = 1


class ServoClient:
    def __init__(self):
        # Resolve ESP32 hostname to IP
        ip_address = socket.gethostbyname("EspServoController")
        print(f"Connected to ESP board at: {ip_address}")

        self.color_format = f"http://{ip_address}/api/color/{{}}"
        self.servo_format = f"http://{ip_address}/api/servo/{{}}/{{}}"

    def _post(self, url: str):
        """Helper: perform HTTP POST using urllib"""
        try:
            req = urllib.request.Request(url, method="POST")
            with urllib.request.urlopen(req) as resp:
                return resp.status == 200
        except Exception:
            return False

    def set_rgb(self, red, green, blue):
        """Sets the built-in RGB to the given colors synchronously."""
        hexed_color = "".join(
            hex(int(x * 255))[2:].rjust(2, "0")
            for x in (red, green, blue)
        )

        url = self.color_format.format(hexed_color)
        return self._post(url)

    def angle_servo(self, servo: ServoType, angle):
        """Sends absolute target angle to the servo synchronously."""
        servo_num = 1 if servo == ServoType.SPIN else 2
        url = self.servo_format.format(servo_num, int(angle))
        return self._post(url)