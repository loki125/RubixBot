import time
from enum import Enum, auto
from typing import List, Tuple, Union, Dict

# ENUMS & TYPE DEFINITIONS

class Face(Enum):
    U = 'U' # Up
    D = 'D' # Down
    R = 'R' # Right
    L = 'L' # Left
    B = 'B' # Back
    F = 'F' # Front

class Servos(Enum):
    FrontLinear = auto(); FrontRoat = auto()
    BackLinear = auto(); BackRoat = auto()
    LeftLinear = auto(); LeftRoat = auto()
    RightLinear = auto(); RightRoat = auto()

class LinearServoInstr(Enum):
    RETRACT = -90
    EXTEND = 90

class RoatServoInstr(Enum):
    SPIN_CW = 90   
    SPIN_CCW = -90 
    UPRIGHT = 0    

class Timing(Enum):
    HorizontalTime = 0.5  
    ClawTime = 0.3        
    DefaultTime = 0.1     

class CameraInstr(Enum):
    CAPTURE_FB = auto()  # Capture while Front/Back claws hold the cube
    CAPTURE_LR = auto()  # Capture while Left/Right claws hold the cube

ServoAction = Tuple[Servos, Union[LinearServoInstr, RoatServoInstr]]
Instruction = Union[ServoAction, Timing, CameraInstr]


#  MOVEMENT MACROS (TURNS & ROLLS)


def turn_face(linear_servo: Servos, rot_servo: Servos, spin_direction: RoatServoInstr) -> List[Instruction]:
    """Standard 90-degree face turn."""
    return[
        (rot_servo, spin_direction), Timing.ClawTime,             # 1. Spin face
        (linear_servo, LinearServoInstr.RETRACT), Timing.HorizontalTime,  # 2. Release
        (rot_servo, RoatServoInstr.UPRIGHT), Timing.ClawTime,             # 3. Reset claw
        (linear_servo, LinearServoInstr.EXTEND), Timing.HorizontalTime    # 4. Regrab
    ]

def turn_face_double(linear_servo: Servos, rot_servo: Servos) -> List[Instruction]:
    """For Kociemba '2' moves (180 deg). Do two 90-degree turns back-to-back."""
    return turn_face(linear_servo, rot_servo, RoatServoInstr.SPIN_CW) + \
           turn_face(linear_servo, rot_servo, RoatServoInstr.SPIN_CW)

# --- ROLLING THE CUBE ---
# These macros physically rotate the entire floating cube so we can access U/D faces.

# Rolls the cube left (U goes to L, D goes to R) -> Used for U/D Kociemba moves
ROLL_CUBE_LEFT: List[Instruction] =[
    (Servos.LeftLinear, LinearServoInstr.RETRACT), (Servos.RightLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.FrontRoat, RoatServoInstr.SPIN_CCW), (Servos.BackRoat, RoatServoInstr.SPIN_CCW), Timing.ClawTime,
    (Servos.LeftLinear, LinearServoInstr.EXTEND), (Servos.RightLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
    (Servos.FrontLinear, LinearServoInstr.RETRACT), (Servos.BackLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.FrontRoat, RoatServoInstr.UPRIGHT), (Servos.BackRoat, RoatServoInstr.UPRIGHT), Timing.ClawTime,
    (Servos.FrontLinear, LinearServoInstr.EXTEND), (Servos.BackLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
]

# Rolls the cube right (Returns from ROLL_CUBE_LEFT)
ROLL_CUBE_RIGHT: List[Instruction] =[
    (Servos.LeftLinear, LinearServoInstr.RETRACT), (Servos.RightLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.FrontRoat, RoatServoInstr.SPIN_CW), (Servos.BackRoat, RoatServoInstr.SPIN_CW), Timing.ClawTime,
    (Servos.LeftLinear, LinearServoInstr.EXTEND), (Servos.RightLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
    (Servos.FrontLinear, LinearServoInstr.RETRACT), (Servos.BackLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.FrontRoat, RoatServoInstr.UPRIGHT), (Servos.BackRoat, RoatServoInstr.UPRIGHT), Timing.ClawTime,
    (Servos.FrontLinear, LinearServoInstr.EXTEND), (Servos.BackLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
]

# Rolls the cube Forward (U goes to F, F goes to D)
ROLL_CUBE_FORWARD: List[Instruction] =[
    (Servos.FrontLinear, LinearServoInstr.RETRACT), (Servos.BackLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.LeftRoat, RoatServoInstr.SPIN_CCW), (Servos.RightRoat, RoatServoInstr.SPIN_CCW), Timing.ClawTime,
    (Servos.FrontLinear, LinearServoInstr.EXTEND), (Servos.BackLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
    (Servos.LeftLinear, LinearServoInstr.RETRACT), (Servos.RightLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.LeftRoat, RoatServoInstr.UPRIGHT), (Servos.RightRoat, RoatServoInstr.UPRIGHT), Timing.ClawTime,
    (Servos.LeftLinear, LinearServoInstr.EXTEND), (Servos.RightLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
]

# Rolls the cube Backward (Returns from ROLL_CUBE_FORWARD)
ROLL_CUBE_BACKWARD: List[Instruction] =[
    (Servos.FrontLinear, LinearServoInstr.RETRACT), (Servos.BackLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.LeftRoat, RoatServoInstr.SPIN_CW), (Servos.RightRoat, RoatServoInstr.SPIN_CW), Timing.ClawTime,
    (Servos.FrontLinear, LinearServoInstr.EXTEND), (Servos.BackLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
    (Servos.LeftLinear, LinearServoInstr.RETRACT), (Servos.RightLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.LeftRoat, RoatServoInstr.UPRIGHT), (Servos.RightRoat, RoatServoInstr.UPRIGHT), Timing.ClawTime,
    (Servos.LeftLinear, LinearServoInstr.EXTEND), (Servos.RightLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
]

# Aliases to keep Kociemba code readable based on earlier logic
FLIP_CUBE_SIDEWAYS = ROLL_CUBE_LEFT
UNFLIP_CUBE_BACK = ROLL_CUBE_RIGHT


# CAMERA SCAN SEQUENCE MACRO 

# Sequence to capture the DOWN face dynamically by moving blocking claws
SCAN_SEQUENCE: List[Instruction] =[
    # 1. Left/Right let go. Front/Back hold the cube. Take picture 1.
    (Servos.LeftLinear, LinearServoInstr.RETRACT), (Servos.RightLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    CameraInstr.CAPTURE_FB, 
    
    # 2. Left/Right grab. Front/Back let go. Take picture 2.
    (Servos.LeftLinear, LinearServoInstr.EXTEND), (Servos.RightLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
    (Servos.FrontLinear, LinearServoInstr.RETRACT), (Servos.BackLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    CameraInstr.CAPTURE_LR, 
    
    # 3. Front/Back grab. Return to fully held default state.
    (Servos.FrontLinear, LinearServoInstr.EXTEND), (Servos.BackLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
]


#  MAPS (KOCIEMBA & FACE SCANNING) ---

KOCIEMBA_MAP: Dict[str, List[Instruction]] = {
    "F":  turn_face(Servos.FrontLinear, Servos.FrontRoat, RoatServoInstr.SPIN_CW),
    "F'": turn_face(Servos.FrontLinear, Servos.FrontRoat, RoatServoInstr.SPIN_CCW),
    "F2": turn_face_double(Servos.FrontLinear, Servos.FrontRoat),
    
    "B":  turn_face(Servos.BackLinear, Servos.BackRoat, RoatServoInstr.SPIN_CW),
    "B'": turn_face(Servos.BackLinear, Servos.BackRoat, RoatServoInstr.SPIN_CCW),
    "B2": turn_face_double(Servos.BackLinear, Servos.BackRoat),
    
    "L":  turn_face(Servos.LeftLinear, Servos.LeftRoat, RoatServoInstr.SPIN_CW),
    "L'": turn_face(Servos.LeftLinear, Servos.LeftRoat, RoatServoInstr.SPIN_CCW),
    "L2": turn_face_double(Servos.LeftLinear, Servos.LeftRoat),
    
    "R":  turn_face(Servos.RightLinear, Servos.RightRoat, RoatServoInstr.SPIN_CW),
    "R'": turn_face(Servos.RightLinear, Servos.RightRoat, RoatServoInstr.SPIN_CCW),
    "R2": turn_face_double(Servos.RightLinear, Servos.RightRoat),

    "U":  FLIP_CUBE_SIDEWAYS + turn_face(Servos.LeftLinear, Servos.LeftRoat, RoatServoInstr.SPIN_CW) + UNFLIP_CUBE_BACK,
    "U'": FLIP_CUBE_SIDEWAYS + turn_face(Servos.LeftLinear, Servos.LeftRoat, RoatServoInstr.SPIN_CCW) + UNFLIP_CUBE_BACK,
    "U2": FLIP_CUBE_SIDEWAYS + turn_face_double(Servos.LeftLinear, Servos.LeftRoat) + UNFLIP_CUBE_BACK,
    
    "D":  FLIP_CUBE_SIDEWAYS + turn_face(Servos.RightLinear, Servos.RightRoat, RoatServoInstr.SPIN_CW) + UNFLIP_CUBE_BACK,
    "D'": FLIP_CUBE_SIDEWAYS + turn_face(Servos.RightLinear, Servos.RightRoat, RoatServoInstr.SPIN_CCW) + UNFLIP_CUBE_BACK,
    "D2": FLIP_CUBE_SIDEWAYS + turn_face_double(Servos.RightLinear, Servos.RightRoat) + UNFLIP_CUBE_BACK,
}

FACE_SCAN_MAP: Dict[Face, List[Instruction]] = {
    Face.D: SCAN_SEQUENCE, # Already pointing down at the camera
    Face.L: ROLL_CUBE_LEFT + SCAN_SEQUENCE + ROLL_CUBE_RIGHT,
    Face.R: ROLL_CUBE_RIGHT + SCAN_SEQUENCE + ROLL_CUBE_LEFT,
    Face.F: ROLL_CUBE_FORWARD + SCAN_SEQUENCE + ROLL_CUBE_BACKWARD,
    Face.B: ROLL_CUBE_BACKWARD + SCAN_SEQUENCE + ROLL_CUBE_FORWARD,
    # Up requires a 180 flip (roll forward twice, scan, unroll backward twice)
    Face.U: ROLL_CUBE_FORWARD + ROLL_CUBE_FORWARD + SCAN_SEQUENCE + ROLL_CUBE_BACKWARD + ROLL_CUBE_BACKWARD,
}

class DeviceInterface:
    """
    Custom interface for executing hardware instructions to the robotic servos and camera.
    """
    def __init__(self, image_path_fb: str, image_path_lr: str):
        self.image_path_fb = image_path_fb
        self.image_path_lr = image_path_lr

    def _move_servo(self, servo: Servos, action: int):
        """Hardware API call to move a servo."""
        # Replace this print statement with your actual servo driving code
        print(f"    [API] -> {servo.name} moving to {action}°")

    def _capture_image(self, path: str):
        """Hardware API call to capture an image."""
        # Replace this with cv2.VideoCapture / cv2.imwrite code
        print(f"    [CAMERA] -> SNAP! Image saved to '{path}'")
        # time.sleep(0.5) # Optional extra delay for camera shutter

    def execute_instructions(self, instructions: List[Instruction]):
        """Iterates through macro lists and triggers hardware timing and actions seamlessly."""
        for instr in instructions:
            if isinstance(instr, Timing):
                sleep_time = instr.value + Timing.DefaultTime.value
                print(f"[WAIT] Sleeping for {sleep_time:.1f}s")
                time.sleep(sleep_time) 
                
            elif isinstance(instr, CameraInstr):
                if instr == CameraInstr.CAPTURE_FB:
                    self._capture_image(self.image_path_fb)
                elif instr == CameraInstr.CAPTURE_LR:
                    self._capture_image(self.image_path_lr)
                    
            else:
                # It's a regular servo action tuple
                servo, action_enum = instr
                self._move_servo(servo, action_enum.value)

    def solve_from_kociemba(self, kociemba_output: str):
        """Executes a Kociemba solution string on the robot."""
        moves = kociemba_output.strip().split()
        print(f"\n[+] Starting Solve Sequence: {moves}\n")
        
        for i, move in enumerate(moves):
            print(f"=== Move {i+1}/{len(moves)}: {move} ===")
            if move in KOCIEMBA_MAP:
                self.execute_instructions(KOCIEMBA_MAP[move])
            else:
                print(f"    [ERROR] Move '{move}' not found in map!")
            print(f"=== {move} Complete (Cube returned to Original State) ===\n")

    def get_face_image(self, face: Face) -> bool:
        """Orients the cube, captures two unobstructed images of a Face, and restores position."""
        print(f"\n[+] Preparing to scan Face {face.name}...")
        if face in FACE_SCAN_MAP:
            self.execute_instructions(FACE_SCAN_MAP[face])
            print(f"[+] Scan of Face {face.name} complete! Cube returned to original state.\n")
            return True
        else:
            print(f"[-] Error: Face {face.name} not mapped.")
            return False


# ==========================================
# --- 6. EXAMPLE USAGE ---
# ==========================================

if __name__ == "__main__":
    # 1. Initialize our robot with the paths for the two camera snapshots
    robot = DeviceInterface(
        image_path_fb="scans/current_face_FB_hold.jpg",
        image_path_lr="scans/current_face_LR_hold.jpg"
    )
    
    # --- TEST 1: Scan a Face ---
    # Will roll the cube, take 2 pictures avoiding claws, and roll back.
    print("--- TEST 1: Scanning Front Face ---")
    robot.get_face_image(Face.F)
    
    # --- TEST 2: Execute a Kociemba Solve ---
    # Note: Using an abbreviated string for the test
    print("--- TEST 2: Executing Move Sequence ---")
    mock_solution = "U R2 F'"
    robot.solve_from_kociemba(mock_solution)