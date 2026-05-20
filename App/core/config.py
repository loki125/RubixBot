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


DEFAULT_PORT = 8000
IMAGE_PATH = "image/current.jpeg"


# Maps standard solver movements to the physical robot's capabilities.
# F = Flip, R = Rotate base, S = Spin cube
ROBOT_MOVES_DICT = {
    'U1': 'F2R1S3',     'U2': 'F2R1S3R1S3', 'U3': 'F2S1R3',
    'D1': 'R1S3',       'D2': 'R1S3R1S3',   'D3': 'S1R3',
    'F1': 'F1R1S3',     'F2': 'F1R1S3R1S3', 'F3': 'F1S1R3',
    'B1': 'F3R1S3',     'B2': 'F3R1S3R1S3', 'B3': 'F3S1R3',
    'L1': 'S3F3R1',     'L2': 'S3F3R1S3R1', 'L3': 'S1F1R3',
    'R1': 'S3F1R1',     'R2': 'S3F1R1S3R1', 'R3': 'S1F3R3'
}

# Initial tracking state of the cube's orientation
STARTING_H_FACES = {'L': 'L', 'F': 'F', 'R': 'R'}
STARTING_V_FACES = {'D': 'D', 'F': 'F', 'U': 'U'}

# Mapping to quickly find the opposite face
OPPOSITE_FACES = {
    'F': 'B', 'B': 'F', 
    'U': 'D', 'D': 'U', 
    'R': 'L', 'L': 'R'
}

KOCIEMBA_FACE_ORDER = ["U", "R", "F", "D", "L", "B"]