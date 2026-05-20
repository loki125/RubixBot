import Kociemba
from .config import ROBOT_MOVES_DICT, STARTING_H_FACES, STARTING_V_FACES, OPPOSITE_FACES, KOCIEMBA_FACE_ORDER

class RobotClient:
    def __init__(self):
        self.instructions_map = None
        self._h_faces = {}
        self._v_faces = {}

    def solve(self, cube_map: dict) -> list:
        """Generates and translates solution instructions using the Kociemba algorithm."""
        try:
            # Convert dictionary of colors to standard 54-char string representation
            kociemba_string = self._serialize_cube_map(cube_map)
            solution = Kociemba.solve(kociemba_string)
            
            if not solution:
                return []
                
            return self._translate_to_robot_moves(solution)
        except Exception as e:
            print(f"Error generating instructions: {e}")
            return []

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


    def flip_cube(self, amount=1):
        """Flips the cube to change the orientation."""
        pass

    def cw_cube(self, amount=1):
        """Spins the entire cube clockwise."""
        pass

    def ccw_cube(self, amount=1):
        """Spins the entire cube counter-clockwise."""
        pass
        
    def rotate_base(self, amount=1):
        """Rotates ONLY the bottom layer (required to actually solve/scramble)."""
        pass

    def _serialize_cube_map(self, cube_map: dict) -> str:
        """
        Maps scanned colors to relative face identifiers using center pieces (index 4), 
        and serializes them to a 54-character Kociemba-compatible string.
        """
        # Map center colors to their corresponding face identifiers
        color_to_face = {}
        for face, colors in cube_map.items():
            if not colors or len(colors) < 5:
                raise ValueError(f"Face '{face}' does not contain valid color scanning data.")
            # Center color (index 4) dictates the face's base identity
            color_to_face[colors[4]] = face

        # Build the standard 54-character representation string
        serialized_chars = []
        for face in KOCIEMBA_FACE_ORDER:
            face_colors = cube_map.get(face, [])
            
            for color in face_colors:
                face_letter = color_to_face.get(color)
                if not face_letter:
                    raise ValueError(f"Color discrepancy: '{color}' on face '{face}' has no matching center.")
                serialized_chars.append(face_letter)

        return "".join(serialized_chars)
    
    def _translate_to_robot_moves(self, kociemba_solution: str) -> list:
        """Translates standard solver string (U2 L1...) to physical commands."""
        self._reset_orientation()
        raw_moves = kociemba_solution.strip().split()
        robot_moves_str = ""

        for move in raw_moves:
            adapted_move = self._adapt_kociemba_move(move)
            robot_seq = ROBOT_MOVES_DICT.get(adapted_move, "")
            robot_moves_str += robot_seq
            self._update_orientation(robot_seq)

        optimized_str = self._optimize_moves(robot_moves_str)
        return self._parse_to_instruction_list(optimized_str)

    def _reset_orientation(self):
        """Resets the virtual cube orientation back to default."""
        self._h_faces = STARTING_H_FACES.copy()
        self._v_faces = STARTING_V_FACES.copy()

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
        self._v_faces['U'] = OPPOSITE_FACES[old_f]
        self._h_faces['F'] = self._v_faces['F']

    def _spin_cw_effect(self):
        """Updates virtual tracking when physical robot spins clockwise."""
        old_f = self._h_faces['F']
        
        self._h_faces['R'] = old_f
        self._h_faces['F'] = self._h_faces['L']
        self._h_faces['L'] = OPPOSITE_FACES[old_f]
        self._v_faces['F'] = self._h_faces['F']

    def _spin_ccw_effect(self):
        """Updates virtual tracking when physical robot spins counter-clockwise."""
        old_f = self._h_faces['F']
        
        self._h_faces['L'] = old_f
        self._h_faces['F'] = self._h_faces['R']
        self._h_faces['R'] = OPPOSITE_FACES[old_f]
        self._v_faces['F'] = self._h_faces['F']