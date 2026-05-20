import http.server
import socketserver
import sys
import random

from .core.camera import CameraClient
from .core.robot import RobotClient
from .core.config import DEFAULT_PORT, IMAGE_PATH

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self):
        self.cube_map = {
            "U": None,
            "R": None,
            "F": None,
            "D": None,
            "L": None,
            "B": None
        }

        self.cube_status : bool = False
        self.camera = CameraClient(image_path=IMAGE_PATH)
        self.cube = RobotClient()

        self.endpoints = {
            '/api/cam_status': self.handle_cam_status,
            '/api/cube_scan': self.handle_cube_scan,
            '/api/cube_solving': self.handle_cube_solving,
            '/api/cube_scramble': self.handle_cube_scramble
        }

        super().__init__()

    def do_GET(self):
        self.endpoints[self.path]() if self.path in self.endpoints else super().do_GET()
    
    def handle_cam_status(self) -> bool:
        """ Checks if the camera can detect a cube in its current view."""

        with self.camera as cam:
            return False if cam.detect_cube() is None else True

    def handle_cube_scan(self):
        """Captures images of all 6 faces of the cube and map them to the cube_map."""

        if not self.handle_cam_status():
            return "No cube detected. Please position the cube in view of the camera and try again."

        first_faces = ["U", "B", "D", "F"]
        with self.camera as cam:
            for face in first_faces:
                self.cube_map[face] = cam.detect_cube()
                self.cube.flip_cube() 
            
            self.cube.cw_cube() 
            self.cube_map["R"] = cam.detect_cube()

            self.cube.flip_cube(2)  
            self.cube_map["L"] = cam.detect_cube()
            
            self.cube.ccw_cube() 
            self.cube.flip_cube()  

        self.cube_status = True
        return "Cube scanned successfully. Ready for solving or scrambling."

    def handle_cube_solving(self):
        """Computes the solution for the current cube state and executes the moves to solve it."""
        if not self.cube_status:
            return "Cube state not available. Please scan the cube first."
        
        solution_instructions : list = self.cube.solve(self.cube_map)

        for move in solution_instructions:
            self.cube.execute_move(move)

        return "Cube solved successfully."

    def handle_cube_scramble(self, move_count=5):
        """Generates a random scramble and executes the moves to scramble the cube."""

        for _ in range(move_count):
            move = random.choice(["U", "R", "F", "D", "L", "B"]) + random.choice(["", "'", "2"])
            self.cube.execute_move(move)

def run_server():
    port = None

    if len(sys.argv) > 1:
        raw_port = sys.argv[1]
        try:
            port = int(raw_port)
        except ValueError:
            print(f"Error: Port must be a number. Received: '{raw_port}'")
            sys.exit(1)
    else:
        port = DEFAULT_PORT

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), MyHandler) as httpd:
        try:
            print(f"Server running on http://localhost:{port}")
            httpd.serve_forever()

        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.server_close()


if __name__ == "__main__":
    run_server()