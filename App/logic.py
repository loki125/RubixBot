import cv2
import numpy as np
# import kociemba
from enum import Enum
import time

from Instructions import *  # Make sure your Enums from the previous file are imported


class ImageProc:
    def __init__(self, image_path_fb: str, image_path_lr: str):
        # We now require BOTH images to fuse them together
        self.image_path_fb = image_path_fb
        self.image_path_lr = image_path_lr

    def map_colors(self) -> list:
        """
        Reads both images, extracts the 9 colors from each, and fuses them 
        to bypass the physical blindspots caused by the claws.
        """

    def _extract_grid_colors(self, img) -> list:
        """
        Instead of contours (which fail if claws block the square shape), 
        we sample the center pixel of a 3x3 grid over the cube area.
        """
        # NOTE: You will need to tune these margins based on how much of the camera 
        # frame the cube actually takes up! Assuming cube is centered.
        height, width = img.shape[:2]

        # Define the bounding box of the cube in the image (e.g., 20% margin)
        margin_x = int(width * 0.2)
        margin_y = int(height * 0.2)

        cube_w = width - (2 * margin_x)
        cube_h = height - (2 * margin_y)

        cell_w = cube_w // 3
        cell_h = cube_h // 3

        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        detected_colors = []

        for row in range(3):
            for col in range(3):
                # Calculate the exact center pixel of each of the 9 stickers
                cx = margin_x + (col * cell_w) + (cell_w // 2)
                cy = margin_y + (row * cell_h) + (cell_h // 2)

                pixel_hsv = hsv_img[cy, cx]
                color_char = self._hsv_to_color(pixel_hsv)
                detected_colors.append(color_char)

        return detected_colors

    def _hsv_to_color(self, hsv_pixel) -> str:
        """
        Maps an HSV pixel to a standard Rubik's Cube color.
        NOTE: Tune these ranges based on your camera hardware and lighting!
        """
        h, s, v = hsv_pixel
        if s < 50 and v > 150: return 'W'  # White
        if s < 50 and v < 100: return 'W'  # Fallback

        if h < 10 or h > 165:
            return 'R'  # Red
        elif 10 <= h < 25:
            return 'O'  # Orange
        elif 25 <= h < 35:
            return 'Y'  # Yellow
        elif 35 <= h < 85:
            return 'G'  # Green
        elif 85 <= h < 140:
            return 'B'  # Blue

        return 'W'  # Default fallback


class CubeLogic:
    def __init__(self):
        pass

    def scan_cube(self) -> bool:
        pass

    def solve(self):
        pass
