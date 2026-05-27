import cv2 as cv
import numpy as np
import math
import threading
import urllib.request
import socket
import os
import logging
from .config import CameraConfig, DEBUG_PATH, CAM_IP

# Set up logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CameraClient:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self._lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)

        try:
            ip_address = socket.gethostbyname("RubikCamera")
        except (socket.gaierror, Exception) as e:
            self.logger.warning(f"Unable to resolve camera hostname. Using fallback IP. Error: {e}")
            ip_address = CAM_IP
            
        self.camera_url = f"http://{ip_address}/capture"
        self.logger.info(f"Initialized CameraClient with URL: {self.camera_url}")

        self.draw_colours = {
            'red'   : (0, 0, 255),
            'orange': (0, 165, 255),
            'blue'  : (255, 0, 0),
            'green' : (0, 255, 0),
            'white' : (255, 255, 255),
            'yellow': (0, 255, 255)
        }

    def __enter__(self):
        self._lock.acquire()
        self.get_image()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    def get_image(self):
        self.logger.debug("Attempting to capture image from camera...")
        try:
            with urllib.request.urlopen(self.camera_url, timeout=10) as response:
                if response.status != 200:
                    self.logger.error(f"Failed to fetch image, HTTP status: {response.status}")
                    return None
                data = response.read()

            img_np = np.asarray(bytearray(data), dtype=np.uint8)
            img = cv.imdecode(img_np, -1)

            dir_name = os.path.dirname(self.image_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            cv.imwrite(self.image_path, img)
            self.logger.info(f"Image successfully saved to {self.image_path}")
            return True

        except Exception as e:
            self.logger.error(f"Exception during image capture: {e}")
            return False

    def detect_cube(self):
        self.logger.info("Starting calibrated cube detection...")
        if not self.get_image():
            self.logger.warning("Capture failed, attempting to use existing image.")
        
        image = cv.imread(self.image_path)
        if image is None:
            self.logger.error("No image found to process.")
            return None

        img_h, img_w = image.shape[:2]

        # ==========================================
        # 1. SHAPE DETECTION ENGINE
        # ==========================================
        b, g, r = cv.split(image)
        blur_size = (7, 7)
        b = cv.GaussianBlur(b, blur_size, 0)
        g = cv.GaussianBlur(g, blur_size, 0)
        r = cv.GaussianBlur(r, blur_size, 0)
        
        canny_b = cv.Canny(b, 15, 45)
        canny_g = cv.Canny(g, 15, 45)
        canny_r = cv.Canny(r, 15, 45)
        
        edges = cv.bitwise_or(canny_b, cv.bitwise_or(canny_g, canny_r))
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
        thick_edges = cv.dilate(edges, kernel, iterations=2)
        blobs = cv.bitwise_not(thick_edges)
        
        contours, _ = cv.findContours(blobs, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        
        raw_squares = []
        min_area = (img_w * img_h) * 0.003
        max_area = (img_w * img_h) * 0.10 
        
        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)
            area = cv.contourArea(contour)
            bbox_area = w * h
            if bbox_area == 0: continue
            
            extent = area / float(bbox_area) 
            ratio = w / float(h)
            
            if min_area < area < max_area and 0.6 <= ratio <= 1.6 and extent > 0.45:
                raw_squares.append({
                    "x": x, "y": y, "w": w, "h": h, 
                    "extent": extent,
                    "contour": contour
                })

        # ==========================================
        # 2. FILTER OUT DUPLICATES
        # ==========================================
        filtered_squares = []
        for sq in raw_squares:
            cx = sq["x"] + (sq["w"] // 2)
            cy = sq["y"] + (sq["h"] // 2)
            
            is_duplicate = False
            for i, ex in enumerate(filtered_squares):
                ex_cx = ex["x"] + (ex["w"] // 2)
                ex_cy = ex["y"] + (ex["h"] // 2)
                dist = math.hypot(cx - ex_cx, cy - ex_cy)
                
                if dist < min(sq["w"], ex["w"]) * 0.6:
                    is_duplicate = True
                    if sq["extent"] > ex["extent"]:
                        filtered_squares[i] = sq
                    break
            
            if not is_duplicate:
                filtered_squares.append(sq)

        if len(filtered_squares) > 9:
            avg_x = sum(s["x"] for s in filtered_squares) / len(filtered_squares)
            avg_y = sum(s["y"] for s in filtered_squares) / len(filtered_squares)
            filtered_squares = sorted(filtered_squares, key=lambda s: math.hypot((s["x"] + s["w"]/2) - avg_x, (s["y"] + s["h"]/2) - avg_y))[:9]

        # ==========================================
        # 3. HSV CLASSIFICATION (WITH LOGO FILTER)
        # ==========================================
        hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        square_contours = []
        
        for sq in filtered_squares:
            x, y, w, h = sq["x"], sq["y"], sq["w"], sq["h"]
            
            inset_x = int(w * 0.35)
            inset_y = int(h * 0.35)
            hsv_roi = hsv_image[y+inset_y : y+h-inset_y, x+inset_x : x+w-inset_x]
            
            if hsv_roi.size == 0:
                continue

            # LOGO VS GLARE FILTER:
            s_channel = hsv_roi[:, :, 1]
            desaturated_ratio = np.sum(s_channel < 75) / s_channel.size
            
            if desaturated_ratio > 0.65:
                sq["colour"] = 'white'
            else:
                pixels = hsv_roi.reshape(-1, 3)
                sorted_by_sat = pixels[pixels[:, 1].argsort()[::-1]]
                top_num = max(1, int(len(sorted_by_sat) * 0.3))
                saturated_pixels = sorted_by_sat[:top_num]

                med_h = np.median(saturated_pixels[:, 0])
                med_s = np.median(saturated_pixels[:, 1])
                med_v = np.median(saturated_pixels[:, 2])

                sq["colour"] = self._classify_hsv(med_h, med_s, med_v)
                
            square_contours.append(sq)

        # ==========================================
        # 4. MATHEMATICAL GRID RECONSTRUCTION
        # ==========================================
        if 6 <= len(square_contours) < 9:
            self.logger.info(f"Only found {len(square_contours)}/9 squares. Reconstructing missing grid coordinates...")
            
            avg_w = int(sum(s["w"] for s in square_contours) / len(square_contours))
            avg_h = int(sum(s["h"] for s in square_contours) / len(square_contours))
            
            xs = sorted([s["x"] for s in square_contours])
            ys = sorted([s["y"] for s in square_contours])
            
            min_x, max_x = xs[0], xs[-1]
            min_y, max_y = ys[0], ys[-1]
            
            step_x = (max_x - min_x) / 2.0
            step_y = (max_y - min_y) / 2.0
            
            grid_matrix = [[None for _ in range(3)] for _ in range(3)]
            
            for sq in square_contours:
                col = round((sq["x"] - min_x) / step_x) if step_x > 0 else 0
                row = round((sq["y"] - min_y) / step_y) if step_y > 0 else 0
                col = max(0, min(2, col))
                row = max(0, min(2, row))
                grid_matrix[row][col] = sq
                
            reconstructed_squares = []
            for r in range(3):
                for c in range(3):
                    if grid_matrix[r][c] is not None:
                        reconstructed_squares.append(grid_matrix[r][c])
                    else:
                        vx = int(min_x + c * step_x)
                        vy = int(min_y + r * step_y)
                        
                        inset_x = int(avg_w * 0.35)
                        inset_y = int(avg_h * 0.35)
                        hsv_roi = hsv_image[vy+inset_y : vy+avg_h-inset_y, vx+inset_x : vx+avg_w-inset_x]
                        
                        if hsv_roi.size > 0:
                            s_channel = hsv_roi[:, :, 1]
                            desaturated_ratio = np.sum(s_channel < 75) / s_channel.size
                            if desaturated_ratio > 0.65:
                                color = 'white'
                            else:
                                pixels = hsv_roi.reshape(-1, 3)
                                sorted_by_sat = pixels[pixels[:, 1].argsort()[::-1]]
                                top_num = max(1, int(len(sorted_by_sat) * 0.3))
                                saturated_pixels = sorted_by_sat[:top_num]
                                
                                med_h = np.median(saturated_pixels[:, 0])
                                med_s = np.median(saturated_pixels[:, 1])
                                med_v = np.median(saturated_pixels[:, 2])
                                color = self._classify_hsv(med_h, med_s, med_v)
                        else:
                            color = "unknown"
                            
                        reconstructed_squares.append({
                            "x": vx, "y": vy, "w": avg_w, "h": avg_h,
                            "colour": color,
                            "reconstructed": True
                        })
            square_contours = reconstructed_squares

        # ==========================================
        # 5. DRAW OVERLAYS & VALIDATE
        # ==========================================
        debug_image = image.copy()
        for sq in square_contours:
            box_color = (0, 165, 255) if "reconstructed" in sq else (0, 255, 0)
            cv.rectangle(debug_image, (sq["x"], sq["y"]), (sq["x"]+sq["w"], sq["y"]+sq["h"]), box_color, 2)
            cv.putText(debug_image, f"{sq['colour']}", (sq["x"] + 5, sq["y"] + 25), 
                        cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv.LINE_AA)
            
        cv.putText(debug_image, f"Found: {len(square_contours)}/9", (15, img_h - 15),
                    cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        cv.imwrite(DEBUG_PATH, debug_image)
        self.logger.info(f"Saved detection map to {DEBUG_PATH} (Found: {len(square_contours)}/9)")

        if len(square_contours) == 9:
            square_contours_sorted_y = sorted(square_contours, key=lambda item: item["y"])

            sorted_rows = []
            for i in range(0, 9, 3):
                unsorted_row = square_contours_sorted_y[i:i+3]
                sorted_rows.append(sorted(unsorted_row, key=lambda item: item["x"]))

            ordered_squares = sorted_rows[0] + sorted_rows[1] + sorted_rows[2]
            middle_square = ordered_squares[4]

            x_min = min(ordered_squares, key=lambda item: item["x"])
            x_max = max(ordered_squares, key=lambda item: item["x"])
            y_min = square_contours_sorted_y[0]
            y_max = square_contours_sorted_y[-1]

            gap_width = int(middle_square["w"] * 2.8)
            gap_height = int(middle_square["h"] * 2.8)

            if (middle_square["x"] - x_min["x"] <= gap_width and
                x_max["x"] - middle_square["x"] <= gap_width and
                middle_square["y"] - y_min["y"] <= gap_height and 
                y_max["y"] - middle_square["y"] <= gap_height):

                self.logger.info("Grid passed spatial structure validation.")
                self._draw_mini_cube(debug_image, ordered_squares)
                cv.imwrite(DEBUG_PATH, debug_image)
                return ordered_squares
            else:
                self.logger.warning("Failed spatial check: Grid positions are too far apart.")
        else:
            self.logger.warning(f"Did not find exactly 9 matching contours. Current count: {len(square_contours)}")
            
        return None

    def analyze_face(self, ordered_squares):
        if not ordered_squares or len(ordered_squares) != 9:
            return None
        return [square["colour"] for square in ordered_squares]

    # ==========================================
    # HSV CLASSIFICATION LOGIC
    # ==========================================
    def _classify_hsv(self, h, s, v):
        # 1. White Check: Saturation is very low
        if s < 55: 
            return 'white'
            
        # 2. Color classification based on Hue
        # (Shifted Yellow/Orange boundary from 25 to 21 to solve the warm-yellow issue)
        if h < 7 or h > 160:
            return 'red'
        elif 7 <= h < 21:
            return 'orange'
        elif 21 <= h < 45:
            return 'yellow'
        elif 45 <= h < 90:
            return 'green'
        elif 90 <= h < 140:
            return 'blue'
            
        return 'unknown'

    def _draw_mini_cube(self, image, squares):
        mx, my = 10, 10
        pos = 0
        for i in range(3):
            for j in range(3):
                col = self.draw_colours.get(squares[pos]["colour"], (128,128,128))
                cv.rectangle(image, (mx, my), (mx + 20, my + 20), col, -1)
                mx += 25
                pos += 1
            mx = 10
            my += 25