import cv2
import numpy as np
import math
import statistics
import threading
import urllib.request
import socket
import os
from .config import CameraConfig

class CameraClient:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self._lock = threading.Lock()

        try:
            ip_address = socket.gethostbyname("RubikCamera")
            self.camera_url = f"http://{ip_address}/capture"
        except (socket.gaierror, Exception) as e:
            print("couldnt find camera, abourting")
            raise SystemExit("Aborting execution due to connection error.") from e

    def __enter__(self):
        self._lock.acquire()
        self.get_image()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    def get_image(self):
        """
        Sends a request to the camera API to capture a new image,
        saves it to image_path/current.jpeg, and returns it as an OpenCV image.
        """
        try:
            with urllib.request.urlopen(self.camera_url) as response:
                if response.status != 200:
                    return None
                data = response.read()

            img_np = np.asarray(bytearray(data), dtype=np.uint8)
            img = cv2.imdecode(img_np, -1)

            dir_name = os.path.dirname(self.image_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            cv2.imwrite(self.image_path, img)
            return True

        except Exception:
            return False

    def detect_cube(self, facelets_in_width=11):
        """
        Detects the cube by loading the image directly from self.image_path.
        """
        if not self.get_image():
            pass  # If camera capture fails, attempt to analyze existing image if available
        
        image = cv2.imread(self.image_path)
        if image is None:
            return None

        h, w = image.shape[:2]
        min_area, max_area = self._calculate_dynamic_area_limits(w, facelets_in_width)
        eroded_edges = self._preprocess_image_edges(image)
        
        contours, hierarchy = cv2.findContours(eroded_edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:
            return None
            
        hierarchy = hierarchy[0]
        facelets = []
        
        for contour, hier in zip(contours, hierarchy):
            # Filter: Skip if the contour contains nested sub-contours (not a basic facelet)
            if hier[2] >= 0: 
                continue
                
            perimeter = cv2.arcLength(contour, True)
            convex_contour = cv2.convexHull(contour, False)
            approx = cv2.approxPolyDP(convex_contour, 0.1 * perimeter, True)
            
            if len(approx) != 4:
                continue

            area = cv2.contourArea(approx)
            if min_area < area < max_area:
                flat_vertices = np.squeeze(approx)
                if flat_vertices.ndim != 2 or flat_vertices.shape[0] != 4 or not self._check_square_geometry(flat_vertices):
                    continue
                
                ordered_pts = self._sort_points_clockwise(flat_vertices)
                inclination = self._calculate_inclination(ordered_pts)
                
                if abs(inclination) > CameraConfig.MAX_ANGLE_INCLINATION_DEG:
                    continue
                moments = cv2.moments(approx)
                if moments['m00'] != 0:
                    cx = int(moments['m10'] / moments['m00'])
                    cy = int(moments['m01'] / moments['m00'])
                    
                    facelets.append({
                        'area': area,
                        'cx': cx,
                        'cy': cy,
                        'contour': approx,
                        'cont_ordered': ordered_pts
                    })
                                
        # Clean up outliers and structure grid
        facelets = self._filter_facelets_by_size(facelets)
        
        if len(facelets) == 9:
            return self._order_grid_positions(facelets)
            
        return None
    
    def analyze_face(self, facelets):
        """
        Loads the image from self.image_path and extracts color codes from detected facelets.
        """
        if not facelets or len(facelets) != 9:
            return None
            
        image = cv2.imread(self.image_path)
        if image is None:
            return None

        colors = []
        for f in facelets:
            hsv_vals = self._get_average_hsv(image, f['cx'], f['cy'], f['area'])
            if hsv_vals is None:
                colors.append('?')
                continue
                
            hue, sat, val = hsv_vals
            color_char = self._classify_color(hue, sat, val)
            colors.append(color_char)
            
        return colors
    
    def _get_average_hsv(self, image, cx, cy, area):
        """
        Samples a small dynamic window around the center of a facelet,
        averages the pixels, and returns Hue, Saturation, and Value.
        """
        side_length = int(math.sqrt(area))
        sample_radius = max(2, int(side_length / 6))
        
        ymin, ymax = max(0, cy - sample_radius), min(image.shape[0], cy + sample_radius)
        xmin, xmax = max(0, cx - sample_radius), min(image.shape[1], cx + sample_radius)
        
        roi = image[ymin:ymax, xmin:xmax]
        if roi.size == 0:
            return None
            
        # Calculate quadratic mean BGR (limits noise/extreme pixel values)
        blue = np.sqrt(np.mean(roi[:, :, 0].astype(float) ** 2))
        green = np.sqrt(np.mean(roi[:, :, 1].astype(float) ** 2))
        red = np.sqrt(np.mean(roi[:, :, 2].astype(float) ** 2))
        
        bgr_pixel = np.array([[[blue, green, red]]], dtype=np.uint8)
        hsv = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)[0][0]
        return hsv[0], hsv[1], hsv[2]

    def _classify_color(self, h, s, v):
        """Classifies an HSV reading into its corresponding single-character color code."""
        if s < CameraConfig.HSV_WHITE_SAT_MAX and v > CameraConfig.HSV_WHITE_VAL_MIN:
            return 'W' 
        elif v < CameraConfig.HSV_BLACK_VAL_MAX:
            return 'K'  # Black/Shadow
            
        if h < CameraConfig.HUE_LIMIT_RED_LOW or h > CameraConfig.HUE_LIMIT_RED_HIGH:
            return 'R'  
        elif CameraConfig.HUE_LIMIT_RED_LOW <= h < CameraConfig.HUE_LIMIT_ORANGE:
            return 'O' 
        elif CameraConfig.HUE_LIMIT_ORANGE <= h < CameraConfig.HUE_LIMIT_YELLOW:
            return 'Y'  
        elif CameraConfig.HUE_LIMIT_YELLOW <= h < CameraConfig.HUE_LIMIT_GREEN:
            return 'G'
        elif CameraConfig.HUE_LIMIT_GREEN <= h < CameraConfig.HUE_LIMIT_BLUE:
            return 'B' 
            
        return '?'

    def _preprocess_image_edges(self, image):
        """
        Converts image to grayscale, blurs to reduce noise, detects 
        edges with Canny, and applies dilation/erosion to join disconnected lines.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, CameraConfig.GAUSSIAN_BLUR_SIZE, 0)
        canny = cv2.Canny(blurred, CameraConfig.CANNY_LOW_THRESHOLD, CameraConfig.CANNY_HIGH_THRESHOLD)
        
        kernel = np.ones((CameraConfig.EDGE_DETECT_KERNEL_SIZE, CameraConfig.EDGE_DETECT_KERNEL_SIZE), np.uint8)
        dilated = cv2.dilate(canny, kernel, iterations=CameraConfig.DILATION_ITERATIONS)
        eroded = cv2.erode(dilated, kernel, iterations=CameraConfig.EROSION_ITERATIONS)
        
        return eroded

    def _calculate_dynamic_area_limits(self, image_width, facelets_in_width=11):
        """
        Dynamically scales the acceptable minimum and maximum area for 
        a facelet square based on the resolution of the image.
        """
        offset_factor = CameraConfig.EDGE_DETECT_KERNEL_SIZE * (1 + CameraConfig.DILATION_ITERATIONS - CameraConfig.EROSION_ITERATIONS)
        
        min_area = int(image_width / facelets_in_width - offset_factor) ** 2
        max_area = int(image_width / 5.5 - offset_factor) ** 2
        
        return min_area, max_area

    def _check_square_geometry(self, vertices):
        """
        Analyzes four points to check if they resemble a square.
        Ensures edge lengths are similar and diagonals are balanced.
        """
        edges = []
        for i in range(4):
            next_i = (i + 1) % 4
            dist = math.sqrt((vertices[next_i][0] - vertices[i][0])**2 + 
                            (vertices[next_i][1] - vertices[i][1])**2)
            edges.append(dist)
        
        edge_variation = (max(edges) - min(edges)) * 4 / sum(edges)
        
        diagonals = []
        for i in range(2):
            opp_i = i + 2
            dist = math.sqrt((vertices[opp_i][0] - vertices[i][0])**2 + 
                            (vertices[opp_i][1] - vertices[i][1])**2)
            diagonals.append(dist)
            
        diagonal_ratio = min(diagonals) / max(diagonals)
        
        is_square = (edge_variation < CameraConfig.SQUARE_SIDE_RATIO_LIMIT) and (diagonal_ratio > CameraConfig.RHOMBUS_DIAGONAL_LIMIT)
        return is_square

    def _calculate_inclination(self, ordered_points):
        """Calculates the tilt angle of the square relative to the horizon."""
        p1, p2 = ordered_points[0], ordered_points[1]
        if p2[0] != p1[0]:
            return -math.atan((p2[1] - p1[1]) / (p2[0] - p1[0])) * 180 / math.pi
        return 0

    def _sort_points_clockwise(self, vertices):
        """Sorts 4 vertices into standard Clockwise order starting from top-left."""
        x_sorted = vertices[np.argsort(vertices[:, 0]), :]
        left_most = x_sorted[:2, :]
        right_most = x_sorted[2:, :]
        
        left_most = left_most[np.argsort(left_most[:, 1]), :]
        tl, bl = left_most
        
        tl_reshaped = tl.reshape(1, 2)
        distances = np.linalg.norm(tl_reshaped[:, np.newaxis, :] - right_most[np.newaxis, :, :], axis=-1)[0]
        br, tr = right_most[np.argsort(distances)[::-1], :]
        
        return np.array([tl, tr, br, bl], dtype='int32')

    def _filter_facelets_by_size(self, facelets):
        """Filters out detected facelets that deviate too far from the median size."""
        if len(facelets) < 7:
            return facelets
            
        areas = [f['area'] for f in facelets]
        median_area = statistics.median(areas)
        
        filtered = []
        for f in facelets:
            deviation = abs(f['area'] - median_area) / median_area
            if deviation <= CameraConfig.MAX_AREA_DEVIATION_LIMIT:
                filtered.append(f)
                
        return filtered

    def _order_grid_positions(self, facelets):
        """Sorts 9 unordered facelets spatially from top-left to bottom-right (3x3 grid)."""
        pts = np.array([[f['cx'], f['cy']] for f in facelets], dtype=int)
        x_sorted = pts[np.argsort(pts[:, 0]), :]
        
        left_col = x_sorted[:3, :]
        mid_col = x_sorted[3:6, :]
        right_col = x_sorted[6:, :]
        
        mid_col_sorted = mid_col[np.argsort(mid_col[:, 1]), :]
        tm, mm, bm = mid_col_sorted
        
        left_col_sorted = left_col[np.argsort(left_col[:, 1]), :]
        tl, ml, bl = left_col_sorted
        
        tl_reshaped = tl.reshape(1, 2)
        dist = np.linalg.norm(tl_reshaped[:, np.newaxis, :] - right_col[np.newaxis, :, :], axis=-1)[0]
        br, mr, tr = right_col[np.argsort(dist)[::-1], :]
        
        ordered_coordinates = np.array([tl, tm, tr, ml, mm, mr, bl, bm, br], dtype='int32')
        
        sorted_facelets = []
        facelets_pool = facelets.copy()
        for coord in ordered_coordinates:
            for i, f in enumerate(facelets_pool):
                if f['cx'] == coord[0] and f['cy'] == coord[1]:
                    sorted_facelets.append(f)
                    facelets_pool.pop(i)
                    break
                    
        return sorted_facelets