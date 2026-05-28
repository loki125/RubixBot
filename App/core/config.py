from enum import Enum

class CameraConfig:
    # Preprocessing Constants
    EDGE_DETECT_KERNEL_SIZE = 5
    DILATION_ITERATIONS = 10
    EROSION_ITERATIONS = 4
    GAUSSIAN_BLUR_SIZE = (9, 9)
    CANNY_LOW_THRESHOLD = 10
    CANNY_HIGH_THRESHOLD = 30

    # Geometric Validation Limits
    SQUARE_SIDE_RATIO_LIMIT = 0.4   # Max difference between longest/shortest sides
    RHOMBUS_DIAGONAL_LIMIT = 0.6    # Min ratio of diagonals (prevents skewed shapes)
    MAX_ANGLE_INCLINATION_DEG = 45  # Max tilt angle allowed relative to horizon
    MAX_AREA_DEVIATION_LIMIT = 0.75 # Max variation allowed from the median facelet size

    # HSV Color Classifier Boundaries
    HSV_WHITE_SAT_MAX = 50
    HSV_WHITE_VAL_MIN = 150
    HSV_BLACK_VAL_MAX = 40

    HUE_LIMIT_RED_LOW = 8
    HUE_LIMIT_RED_HIGH = 165
    HUE_LIMIT_ORANGE = 22
    HUE_LIMIT_YELLOW = 38
    HUE_LIMIT_GREEN = 85
    HUE_LIMIT_BLUE = 135


IMAGE_PATH = "image/current.jpeg"
DEBUG_PATH = "image/debug_cube_detection.jpg"
DEFAULT_PORT = 8000
CAM_IP = "10.151.37.177"
SERVO_IP = "10.151.37.143"

class TopState(Enum):
    OPEN = 0
    CLOSED = 1
    FLIP = 2

class BottomState(Enum):
    HOME = 0
    CW = 1
    CCW = 2

class RobotConfig:
    # --- ABSOLUTE SERVO ANGLES (0 to 180 degrees) ---

    BOTTOM_CCW_ANGLE = 20      # Fully CCW position (-90°)
    BOTTOM_HOME_ANGLE = 110     # Center/Home position (0°)
    BOTTOM_CW_ANGLE = 215      # Fully CW position (+90°)

    TOP_FLIP_ANGLE = 40        # Flipper fully up (lifts the cube)
    TOP_OPEN_ANGLE = 100       # Top cover wide open (cube completely free)
    TOP_CLOSE_ANGLE = 140       # Top cover closed (locks middle/top layers)

    # --- ACTION DELAYS (Seconds) ---
    DELAY_FLIP = 0.65          # Time to execute a flip
    DELAY_OPEN = 0.65          # Time to raise cover
    DELAY_CLOSE = 0.50         # Time to lower cover
    DELAY_SPIN = 0.75          # Time to spin the turntable
    DELAY_ROTATE = 0.80        # Time to rotate a locked layer

    # --- KOCIEMBA DICTIONARIES ---
    ROBOT_MOVES_DICT = {
        'U1': 'F2R1S3',     'U2': 'F2R1S3R1S3', 'U3': 'F2S1R3',      
        'D1': 'S1R3',       'D2': 'S1R3S1R3',   'D3': 'R1S3',  
        'F1': 'F1R1S3',     'F2': 'F1R1S3R1S3', 'F3': 'F1S1R3',
        'B1': 'F3R1S3',     'B2': 'F3R1S3R1S3', 'B3': 'F3S1R3',
        'L1': 'S3F3R1',     'L2': 'S3F3R1S3R1', 'L3': 'S1F1R3',
        'R1': 'S3F1R1',     'R2': 'S3F1R1S3R1', 'R3': 'S1F3R3'
    }

    STARTING_H_FACES = {'L': 'L', 'F': 'F', 'R': 'R'}
    STARTING_V_FACES = {'D': 'D', 'F': 'F', 'U': 'U'}

    OPPOSITE_FACES = {
        'F': 'B', 'B': 'F', 
        'U': 'D', 'D': 'U', 
        'R': 'L', 'L': 'R'
    }

    KOCIEMBA_FACE_ORDER = ["U", "R", "F", "D", "L", "B"]
