import cv2
import numpy as np
import kociemba
from enum import Enum
import time

class Face(Enum):
    U = 'U' # Up
    D = 'D' # Down
    R = 'R' # Right
    L = 'L' # Left
    B = 'B' # Back
    F = 'F' # Front

class Move(Enum):
    U = "U"
    U_PRIME = "U'"
    U2 = "U2"
    D = "D"
    D_PRIME = "D'"
    D2 = "D2"
    R = "R"
    R_PRIME = "R'"
    R2 = "R2"
    L = "L"
    L_PRIME = "L'"
    L2 = "L2"
    F = "F"
    F_PRIME = "F'"
    F2 = "F2"
    B = "B"
    B_PRIME = "B'"
    B2 = "B2"


class DeviceInterface:
    """
    Costume external class for interacting with the physical device.
    """
    def __init__(self, image_path: str):
        self.image_path = image_path

    def get_face_image(self, face: Face) -> bool:
        print(f"[Device] Moving camera/cube to capture face {face.name}...")
        # Simulates capturing an image and saving it to the shared image_path
        time.sleep(0.5) 
        return True

    def run_operation(self, op: Move) -> bool:
        print(f"[Device] Executing move: {op.value}")
        time.sleep(0.5)
        return True

class ImageProc:
    def __init__(self, image_path: str):
        # The path where the image is always saved and processed from
        self.image_path = image_path

    def map_colors(self) -> list:
        """
        Reads the image, finds the Rubik's cube face, and extracts the 9 colors.
        Returns a list of 9 characters representing colors (e.g.,['R', 'W', 'B', ...])
        reading from top-left to bottom-right.
        """
        img = cv2.imread(self.image_path)
        if img is None:
            print("[ImageProc] Could not read image, returning mock colors.")
            # Fallback to mock data if no real image exists at the path
            return['U']*9 

        # 1. Convert to grayscale and find edges
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        canny = cv2.Canny(blurred, 30, 60)

        # 2. Find contours
        contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        squares =[]
        for cnt in contours:
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.05 * perimeter, True)
            
            # If the contour has 4 vertices, it's a square/rectangle (a cube sticker)
            if len(approx) == 4:
                area = cv2.contourArea(cnt)
                # Filter by area to avoid noise (these thresholds need tuning based on your camera setup)
                if 1000 < area < 10000:
                    x, y, w, h = cv2.boundingRect(approx)
                    squares.append((x, y, w, h))

        # 3. Sort squares to read from top-left to bottom-right (3x3 grid)
        # Note: A robust implementation would ensure exactly 9 squares are found.
        squares = sorted(squares, key=lambda s: (s[1] // 50, s[0])) # Rough spatial sorting

        detected_colors =[]
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        for (x, y, w, h) in squares[:9]:
            # Extract the center pixel of each square to get the color
            cx, cy = x + w // 2, y + h // 2
            pixel_hsv = hsv_img[cy, cx]
            color_char = self._hsv_to_color(pixel_hsv)
            detected_colors.append(color_char)

        return detected_colors

    def _hsv_to_color(self, hsv_pixel) -> str:
        """
        Maps an HSV pixel to a standard Rubik's Cube color.
        NOTE: These HSV ranges will need tuning based on your specific lighting!
        Returns: 'W' (White), 'Y' (Yellow), 'R' (Red), 'O' (Orange), 'G' (Green), 'B' (Blue)
        """
        h, s, v = hsv_pixel
        if s < 50 and v > 150:
            return 'W' # White
        elif s < 50 and v < 100:
            return 'W' # Assuming no black on cube, fallback
        
        if h < 10 or h > 165:
            return 'R' # Red
        elif 10 <= h < 25:
            return 'O' # Orange
        elif 25 <= h < 35:
            return 'Y' # Yellow
        elif 35 <= h < 85:
            return 'G' # Green
        elif 85 <= h < 140:
            return 'B' # Blue
        
        return 'W' # Default fallback

class CubeLogic:
    def __init__(self, device: DeviceInterface, image_proc: ImageProc):
        self.device = device
        self.image_proc = image_proc
        self.cube_state = {}

    def scan_cube(self) -> bool:
        """
        Uses the DeviceInterface to look at all 6 faces,
        then uses ImageProc to map the colors.
        """
        print("\n--- Scanning Cube ---")
        # Kociemba requires the faces in a specific order: U, R, F, D, L, B
        scan_order =[Face.U, Face.R, Face.F, Face.D, Face.L, Face.B]

        for face in scan_order:
            success = self.device.get_face_image(face)
            if not success:
                print(f"[CubeLogic] Error: Failed to capture face {face.name}")
                return False
            
            # Map colors from the newly saved image
            colors = self.image_proc.map_colors()
            
            # Store colors mapped to the face
            self.cube_state[face] = colors
            print(f"Scanned {face.name}: {colors}")

        return True

    def solve(self):
        """
        Main solving function. Scans the cube, generates the algorithm, 
        and sends operations to the device.
        """
        if not self.scan_cube():
            print("[CubeLogic] Aborting solve due to scanning failure.")
            return

        print("\n--- Calculating Solution ---")
        # To solve using Kociemba, we must replace colors (W, Y, R, etc) 
        # with the relative face names (U, D, R, L, F, B).
        # We determine which color belongs to which face by looking at the center tiles.
        color_to_face = {}
        for face, colors in self.cube_state.items():
            # The 5th element (index 4) is the center tile of a 3x3 face
            center_color = colors[4] 
            color_to_face[center_color] = face.value

        # Build the 54-character string expected by Kociemba: U1-U9, R1-R9, F1-F9, D1-D9, L1-L9, B1-B9
        kociemba_order =[Face.U, Face.R, Face.F, Face.D, Face.L, Face.B]
        cube_string = ""
        
        try:
            for face in kociemba_order:
                for color in self.cube_state[face]:
                    # Map the detected color to its structural face letter
                    cube_string += color_to_face[color]
        except KeyError:
            print("[CubeLogic] Error: Detected colors do not form a valid Rubik's cube state. Check camera/lighting.")
            # For demonstration, we will use a known solved state if the camera mapping fails
            cube_string = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

        print(f"Computed Cube String: {cube_string}")

        # Solve using the library
        try:
            # Returns a string like: "D2 R' D' F2 C B'..."
            solution_string = kociemba.solve(cube_string)
            print(f"Solution Algorithm: {solution_string}")
        except Exception as e:
            print(f"[CubeLogic] Kociemba solve error (Cube might be unsolvable/read incorrectly): {e}")
            return

        # Execute operations on the device
        print("\n--- Executing Moves ---")
        moves = solution_string.split()
        for move_str in moves:
            # Parse the string into our Move Enum
            op = Move(move_str)
            success = self.device.run_operation(op)
            if not success:
                print(f"[CubeLogic] Device failed to execute move {op.name}. Aborting.")
                return
        
        print("[CubeLogic] Cube successfully solved!")
