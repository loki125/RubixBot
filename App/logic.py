import cv2
import numpy as np
import kociemba
from enum import Enum
import time

from Instructions import * # Make sure your Enums from the previous file are imported

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
        img_fb = cv2.imread(self.image_path_fb)
        img_lr = cv2.imread(self.image_path_lr)

        if img_fb is None or img_lr is None:
            print("[ImageProc] Could not read one or both images. Returning mock colors.")
            return ['U'] * 9 

        # Extract 9 colors from both images using a fixed-grid approach
        colors_fb = self._extract_grid_colors(img_fb)
        colors_lr = self._extract_grid_colors(img_lr)

        # FUSE THE IMAGES:
        # img_lr: Left/Right claws are blocking the sides, but Top & Bottom are clear.
        # img_fb: Front/Back claws are blocking top/bottom, but Middle is clear.
        final_colors = [
            colors_lr[0], colors_lr[1], colors_lr[2], # Top Row (From LR image)
            colors_fb[3], colors_fb[4], colors_fb[5], # Middle Row (From FB image)
            colors_lr[6], colors_lr[7], colors_lr[8]  # Bottom Row (From LR image)
        ]
        
        return final_colors

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
        detected_colors =[]

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
        if s < 50 and v > 150: return 'W' # White
        if s < 50 and v < 100: return 'W' # Fallback
        
        if h < 10 or h > 165: return 'R'  # Red
        elif 10 <= h < 25:    return 'O'  # Orange
        elif 25 <= h < 35:    return 'Y'  # Yellow
        elif 35 <= h < 85:    return 'G'  # Green
        elif 85 <= h < 140:   return 'B'  # Blue
        
        return 'W' # Default fallback


class CubeLogic:
    def __init__(self, image_path_fb: str, image_path_lr: str):
        self.device = DeviceInterface(
            image_path_fb=image_path_fb, 
            image_path_lr=image_path_lr
        )

        self.image_proc = ImageProc(
            image_path_fb=image_path_fb, 
            image_path_lr=image_path_lr
        )
        self.cube_state = {}

    def scan_cube(self) -> bool:
        """
        Uses the DeviceInterface to orient the cube, takes dual pictures for all 6 faces,
        and fuses them via ImageProc.
        """
        print("\n==============================")
        print("--- Initiating Cube Scan ---")
        print("==============================")
        
        # Kociemba requires the faces in a specific order: U, R, F, D, L, B
        scan_order =[Face.U, Face.R, Face.F, Face.D, Face.L, Face.B]

        for face in scan_order:
            # 1. Device handles the physical movement, rolling, and takes both pictures!
            success = self.device.get_face_image(face)
            if not success:
                print(f"[CubeLogic] Error: Failed to capture face {face.name}")
                return False
            
            # 2. ImageProc reads the newly saved images, fuses them, and extracts 9 colors
            colors = self.image_proc.map_colors()
            
            # 3. Store the result
            self.cube_state[face] = colors
            print(f"--> {face.name} Face Colors Detected: {colors}")

        return True

    def solve(self):
        """
        Main solving function. Scans, translates colors to Kociemba notation, 
        generates the algorithm, and sends it to the hardware.
        """
        if not self.scan_cube():
            print("\n[CubeLogic] Aborting solve due to scanning failure.")
            return

        print("\n--- Calculating Solution ---")
        
        # Map center colors to their Face (e.g., Yellow -> U)
        color_to_face = {}
        for face, colors in self.cube_state.items():
            center_color = colors[4] # Index 4 is the center of the 3x3 array
            color_to_face[center_color] = face.value

        # Build the 54-character Kociemba string
        kociemba_order =[Face.U, Face.R, Face.F, Face.D, Face.L, Face.B]
        cube_string = ""
        
        try:
            for face in kociemba_order:
                for color in self.cube_state[face]:
                    # Map 'W', 'Y', etc. to 'U', 'R', 'F', etc.
                    cube_string += color_to_face[color]
        except KeyError as e:
            print(f"[CubeLogic] Color mapping failed! Found unknown center color: {e}")
            print("Ensure lighting is consistent and center tiles are correctly read.")
            return

        print(f"Computed Cube String: {cube_string}")

        # Solve via Kociemba
        try:
            solution_string = kociemba.solve(cube_string)
            print(f"Solution Algorithm: {solution_string}")
        except Exception as e:
            print(f"\n[CubeLogic] Kociemba solve error: {e}")
            print("This usually means the camera misread a color. Check the CV mapping!")
            return

        # Send the solution string back to the robot execution pipeline!
        print("\n--- Executing Hardware Solution ---")
        self.device.solve_from_kociemba(solution_string)
        print("\n[CubeLogic] Cube successfully solved!")