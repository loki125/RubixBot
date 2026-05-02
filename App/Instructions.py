import time
from enum import Enum, auto
from typing import List, Tuple, Union, Dict

# --- 1. Enums ---
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

ServoAction = Tuple[Servos, Union[LinearServoInstr, RoatServoInstr]]
Instruction = Union[ServoAction, Timing]


# --- 2. Macro Sequences ---

def turn_face(linear_servo: Servos, rot_servo: Servos, spin_direction: RoatServoInstr) -> List[Instruction]:
    """Standard 90-degree turn."""
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

# FLIP (Roll cube to put U on Left and D on Right)
FLIP_CUBE_SIDEWAYS: List[Instruction] =[
    (Servos.LeftLinear, LinearServoInstr.RETRACT), (Servos.RightLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.FrontRoat, RoatServoInstr.SPIN_CCW), (Servos.BackRoat, RoatServoInstr.SPIN_CCW), Timing.ClawTime,
    (Servos.LeftLinear, LinearServoInstr.EXTEND), (Servos.RightLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
    (Servos.FrontLinear, LinearServoInstr.RETRACT), (Servos.BackLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.FrontRoat, RoatServoInstr.UPRIGHT), (Servos.BackRoat, RoatServoInstr.UPRIGHT), Timing.ClawTime,
    (Servos.FrontLinear, LinearServoInstr.EXTEND), (Servos.BackLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
]

# UNFLIP (Roll cube back to original state)
UNFLIP_CUBE_BACK: List[Instruction] =[
    (Servos.LeftLinear, LinearServoInstr.RETRACT), (Servos.RightLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.FrontRoat, RoatServoInstr.SPIN_CW), (Servos.BackRoat, RoatServoInstr.SPIN_CW), Timing.ClawTime,
    (Servos.LeftLinear, LinearServoInstr.EXTEND), (Servos.RightLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
    (Servos.FrontLinear, LinearServoInstr.RETRACT), (Servos.BackLinear, LinearServoInstr.RETRACT), Timing.HorizontalTime,
    (Servos.FrontRoat, RoatServoInstr.UPRIGHT), (Servos.BackRoat, RoatServoInstr.UPRIGHT), Timing.ClawTime,
    (Servos.FrontLinear, LinearServoInstr.EXTEND), (Servos.BackLinear, LinearServoInstr.EXTEND), Timing.HorizontalTime,
]


# --- 3. The 18-Move Kociemba Map ---
# Guaranteed to return to original state after EVERY move!

KOCIEMBA_MAP: Dict[str, List[Instruction]] = {
    # DIRECT MOVES (Front, Back, Left, Right)
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

    # INDIRECT MOVES (Up, Down) - Flips cube, does the turn(s), unflips cube back to original state
    "U":  FLIP_CUBE_SIDEWAYS + turn_face(Servos.LeftLinear, Servos.LeftRoat, RoatServoInstr.SPIN_CW) + UNFLIP_CUBE_BACK,
    "U'": FLIP_CUBE_SIDEWAYS + turn_face(Servos.LeftLinear, Servos.LeftRoat, RoatServoInstr.SPIN_CCW) + UNFLIP_CUBE_BACK,
    "U2": FLIP_CUBE_SIDEWAYS + turn_face_double(Servos.LeftLinear, Servos.LeftRoat) + UNFLIP_CUBE_BACK,
    
    "D":  FLIP_CUBE_SIDEWAYS + turn_face(Servos.RightLinear, Servos.RightRoat, RoatServoInstr.SPIN_CW) + UNFLIP_CUBE_BACK,
    "D'": FLIP_CUBE_SIDEWAYS + turn_face(Servos.RightLinear, Servos.RightRoat, RoatServoInstr.SPIN_CCW) + UNFLIP_CUBE_BACK,
    "D2": FLIP_CUBE_SIDEWAYS + turn_face_double(Servos.RightLinear, Servos.RightRoat) + UNFLIP_CUBE_BACK,
}


# --- 4. Execution & API ---

def move_servo(servo: Servos, action: int):
    """Your custom API call."""
    print(f"  [API] -> {servo.name} to {action}°")

def execute_instructions(instructions: List[Instruction]):
    """Iterate and execute servo movements and precise timings."""
    for instr in instructions:
        if isinstance(instr, Timing):
            sleep_time = instr.value + Timing.DefaultTime.value
            print(f"  [WAIT] {sleep_time:.1f}s")
            time.sleep(sleep_time) # Uncomment for actual hardware
        else:
            servo, action_enum = instr
            move_servo(servo, action_enum.value)

def solve_from_kociemba(kociemba_output: str):
    """Parses Kociemba output string and maps to physical servos."""
    # Kociemba outputs look like: "U2 R' D2 F"
    moves = kociemba_output.strip().split()
    
    print(f"\n[+] Starting Solve Sequence: {moves}\n")
    
    for i, move in enumerate(moves):
        print(f"=== Move {i+1}/{len(moves)}: {move} ===")
        
        # Look up the move in our map
        if move in KOCIEMBA_MAP:
            instructions = KOCIEMBA_MAP[move]
            execute_instructions(instructions)
        else:
            print(f"  [ERROR] Move '{move}' not found in map!")
        
        print(f"=== {move} Complete (Cube in Original State) ===\n")

# --- Example Usage ---
if __name__ == "__main__":
    # Mock Kociemba Output String
    kociemba_solution = "U2 F' R"
    
    solve_from_kociemba(kociemba_solution)