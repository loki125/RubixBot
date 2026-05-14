import socket

import requests
import cv2

url_format = "http://{ip_addr}:81/stream"

def main():
    ip_address = socket.gethostbyname("RubikCamera")
    url = url_format.format(ip_addr = ip_address)
    cap = cv2.VideoCapture(url)
    while True:
        ret, frame = cap.read()

        if ret:
            cv2.imshow("Frame:", frame)

            if cv2.waitKey(10) & 0xFF == ord("q"):
               print("Farewell!")
               break
        else:
            print("Video failed")

if __name__ == '__main__':
    main()