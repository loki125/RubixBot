import time
import kociemba
from .config import RobotConfig, TopState, BottomState
from .servo import ServoClient, ServoType

class RobotClient:
    def __init__(self):
        self.instructions_map = None
        self._h_faces = {}
        self._v_faces = {}
        
        self.servo = ServoClient()
        self.top_state = TopState.OPEN
        self.bottom_state = BottomState.HOME

    def _send_top(self, angle: int, delay: float, target_state: TopState):
        """Moves the top servo to an absolute angle and updates state."""
        self.servo.angle_servo(ServoType.TOP, angle)
        self.top_state = target_state
        time.sleep(delay)

    def _send_bottom(self, angle: int, delay: float, target_state: BottomState):
        """Moves the bottom servo to an absolute angle and updates state."""
        self.servo.angle_servo(ServoType.SPIN, angle)
        self.bottom_state = target_state
        time.sleep(delay)

    def _ensure_cover_open(self):
        """Ensures the top cover is raised before spinning."""
        if self.top_state != TopState.OPEN:
            self._send_top(RobotConfig.TOP_OPEN_ANGLE, RobotConfig.DELAY_OPEN, TopState.OPEN)

    def _ensure_cover_closed(self):
        """Ensures the top cover is lowered before rotating a layer."""
        if self.top_state != TopState.CLOSED:
            self._send_top(RobotConfig.TOP_CLOSE_ANGLE, RobotConfig.DELAY_CLOSE, TopState.CLOSED)

    def flip_cube(self, amount=1):
        """Flips the cube to change the orientation."""
        for i in range(amount):
            # 1. Raise flipper up
            self._send_top(RobotConfig.TOP_FLIP_ANGLE, RobotConfig.DELAY_FLIP, TopState.FLIP)
            # 2. If we need to flip again, return to open to let the cube settle
            if i < (amount - 1):
                self._send_top(RobotConfig.TOP_OPEN_ANGLE, RobotConfig.DELAY_OPEN, TopState.OPEN)

    def cw_cube(self, amount=1):
        """Spins the entire cube clockwise."""
        self._ensure_cover_open()
        
        if self.bottom_state == BottomState.HOME:
            self._send_bottom(RobotConfig.BOTTOM_CW_ANGLE, RobotConfig.DELAY_SPIN, BottomState.CW)
        else:
            self._send_bottom(RobotConfig.BOTTOM_HOME_ANGLE, RobotConfig.DELAY_SPIN, BottomState.HOME)

    def ccw_cube(self, amount=1):
        """Spins the entire cube counter-clockwise."""
        self._ensure_cover_open()
        
        if self.bottom_state == BottomState.HOME:
            self._send_bottom(RobotConfig.BOTTOM_CCW_ANGLE, RobotConfig.DELAY_SPIN, BottomState.CCW)
        else:
            self._send_bottom(RobotConfig.BOTTOM_HOME_ANGLE, RobotConfig.DELAY_SPIN, BottomState.HOME)
        
    def rotate_base(self, amount=1):
        """Rotates ONLY the bottom layer (required to actually solve/scramble)."""
        self._ensure_cover_closed()
        
        direction = "CCW" if amount == 3 else "CW"
        if self.bottom_state == BottomState.HOME:
            if direction == "CW":
                self._send_bottom(RobotConfig.BOTTOM_CW_ANGLE, RobotConfig.DELAY_ROTATE, BottomState.CW)
            else:
                self._send_bottom(RobotConfig.BOTTOM_CCW_ANGLE, RobotConfig.DELAY_ROTATE, BottomState.CCW)
        else:
            self._send_bottom(RobotConfig.BOTTOM_HOME_ANGLE, RobotConfig.DELAY_ROTATE, BottomState.HOME)
            
        self._send_top(RobotConfig.TOP_OPEN_ANGLE, RobotConfig.DELAY_OPEN, TopState.OPEN)

    def solve(self, cube_map: dict) -> list:
        """Generates and translates solution instructions using the Kociemba algorithm."""
        kociemba_string = self._serialize_cube_map(cube_map)
        
        try:
            solution = kociemba.solve(kociemba_string)
        except Exception as e:
            raise ValueError(
                f"The cube is mathematically unsolvable (Kociemba error: {e}). "
                f"This usually means a corner/edge is physically twisted, or there was a color error during scanning.\n"
                f"Serialized string sent to solver: {kociemba_string}"
            ) from e
            
        if not solution:
            return []
            
        return self._translate_to_robot_moves(solution)

    def execute_move(self, move: str):
        """Executes a single compiled physical move on the hardware."""
        action = move[0]
        amount = int(move[1])

        if action == 'F':
            self.flip_cube(amount)
        elif action == 'S':
            if amount == 3:
                self.ccw_cube(1)
            else:
                self.cw_cube(amount)
        elif action == 'R':
            self.rotate_base(amount)

    def _serialize_cube_map(self, cube_map: dict) -> str:
        """Validates scanned data and serializes it to a 54-character Kociemba string."""
        for face in RobotConfig.KOCIEMBA_FACE_ORDER:
            colors = cube_map.get(face)
            if not colors or len(colors) != 9 or '?' in colors:
                raise ValueError(f"Scan Error: Face '{face}' is invalid (must have 9 facelets and no '?').")

        color_to_face = {colors[4]: face for face, colors in cube_map.items()}
        if len(color_to_face) != 6:
            raise ValueError("Scan Error: Duplicate center colors detected. Each face must have a unique center color.")

        try:
            return "".join(color_to_face[col] for f in RobotConfig.KOCIEMBA_FACE_ORDER for col in cube_map[f])
        except KeyError as e:
            raise ValueError(f"Scan Error: Color '{e.args[0]}' does not match any detected center color.")
    
    def _translate_to_robot_moves(self, kociemba_solution: str) -> list:
        """Translates standard solver string (U2 L1...) to physical commands."""
        self._reset_orientation()
        raw_moves = kociemba_solution.strip().split()
        robot_moves_str = ""

        for move in raw_moves:
            adapted_move = self._adapt_kociemba_move(move)
            robot_seq = RobotConfig.ROBOT_MOVES_DICT.get(adapted_move, "")
            robot_moves_str += robot_seq
            self._update_orientation(robot_seq)

        optimized_str = self._optimize_moves(robot_moves_str)
        return self._parse_to_instruction_list(optimized_str)

    def _reset_orientation(self):
        """Resets the virtual cube orientation back to default."""
        self._h_faces = RobotConfig.STARTING_H_FACES.copy()
        self._v_faces = RobotConfig.STARTING_V_FACES.copy()

    def _adapt_kociemba_move(self, move: str) -> str:
        """Finds which physical side the requested face is currently on."""
        target_face = move[0]
        rotations = move[1]

        for side, current_face in self._h_faces.items():
            if current_face == target_face:
                return side + rotations
                
        for side, current_face in self._v_faces.items():
            if current_face == target_face:
                return side + rotations
                
        return 'B' + rotations

    def _update_orientation(self, movement_sequence: str):
        """Tracks macroscopic changes to the cube's orientation in 3D space."""
        instructions = self._parse_to_instruction_list(movement_sequence)
        
        for action, amount_str in instructions:
            amount = int(amount_str)
            
            if action == 'F':
                for _ in range(amount): 
                    self._flip_effect()
            elif action == 'S':
                if amount == 3:
                    self._spin_ccw_effect()
                else:
                    for _ in range(amount): 
                        self._spin_cw_effect()

    def _optimize_moves(self, moves_str: str) -> str:
        """Removes opposing redundant spins to save physical solve time."""
        prev_moves = ""
        while prev_moves != moves_str:
            prev_moves = moves_str
            moves_str = moves_str.replace('S1S3', '').replace('S3S1', '')
        return moves_str

    def _parse_to_instruction_list(self, sequence: str) -> list:
        """Converts a flat string 'F2R1S3' into a list ['F2', 'R1', 'S3']."""
        return [sequence[i:i+2] for i in range(0, len(sequence), 2)]

    def _flip_effect(self):
        """Updates virtual tracking when the physical robot flips the cube."""
        old_f = self._v_faces['F']
        
        self._v_faces['D'] = old_f
        self._v_faces['F'] = self._v_faces['U']
        self._v_faces['U'] = RobotConfig.OPPOSITE_FACES[old_f]
        self._h_faces['F'] = self._v_faces['F']

    def _spin_cw_effect(self):
        """Updates virtual tracking when physical robot spins clockwise."""
        old_f = self._h_faces['F']
        
        self._h_faces['R'] = old_f
        self._h_faces['F'] = self._h_faces['L']
        self._h_faces['L'] = RobotConfig.OPPOSITE_FACES[old_f]
        self._v_faces['F'] = self._h_faces['F']

    def _spin_ccw_effect(self):
        """Updates virtual tracking when physical robot spins counter-clockwise."""
        old_f = self._h_faces['F']
        
        self._h_faces['L'] = old_f
        self._h_faces['F'] = self._h_faces['R']
        self._h_faces['R'] = RobotConfig.OPPOSITE_FACES[old_f]
        self._v_faces['F'] = self._h_faces['F']