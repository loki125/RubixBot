import http.server
import socketserver
import sys
import os
import json
import random
from urllib.parse import urlparse 

from core.camera import CameraClient
from core.robot import RobotClient
from core.config import DEFAULT_PORT, IMAGE_PATH

class MyHandler(http.server.SimpleHTTPRequestHandler):
    cube_map = {
        "U": None,
        "R": None,
        "F": None,
        "D": None,
        "L": None,
        "B": None
    }
    cube_status: bool = False
    camera = CameraClient(image_path=IMAGE_PATH)
    cube = RobotClient()

    def __init__(self, *args, **kwargs):
        self.endpoints = {
            '/api/cam_status': self.handle_cam_status,
            '/api/cube_scan': self.handle_cube_scan,
            '/api/cube_solving': self.handle_cube_solving,
            '/api/cube_scramble': self.handle_cube_scramble,
            '/api/image_timestamp': self.handle_image_timestamp
        }
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path).path
        
        if parsed_path in self.endpoints:
            self.endpoints[parsed_path]()
        else:
            self.path = parsed_path 
            super().do_GET()

    def log_message(self, format, *args):
        if "/api/image_timestamp" in self.path:
            return
        super().log_message(format, *args)

    def send_text_response(self, message: str, status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

    def handle_image_timestamp(self):
        """Returns the last modified time of the image so the UI knows when to reload it."""
        if not os.path.exists(IMAGE_PATH):
            response_data = {
                "timestamp": 0, 
                "path": f"/{IMAGE_PATH}"
            }
        else:
            mtime = os.path.getmtime(IMAGE_PATH)
            response_data = {
                "timestamp": mtime,
                "path": f"/{IMAGE_PATH}"
            }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def handle_cam_status(self):
        """ Checks if the camera can detect a cube in its current view."""
        with MyHandler.camera as cam:
            has_cube = cam.detect_cube() is not None
        
        MyHandler.cube_status = has_cube 
        if has_cube:
            self.send_text_response("Cube detected in view.")
        else:
            self.send_text_response("No cube detected.")

    def handle_cube_scan(self):
        """Captures images of all 6 faces of the cube and map them to the cube_map."""
        with MyHandler.camera as cam:
            if cam.detect_cube() is None:
                self.send_text_response("No cube detected. Please position the cube and try again.", 400)
                return

        first_faces = ["U", "R", "D", "L"]       
        with MyHandler.camera as cam:
            for face in first_faces:
                facelets = cam.detect_cube()
                MyHandler.cube_map[face] = cam.analyze_face(facelets) if facelets else None
                MyHandler.cube.flip_cube() 
            
            MyHandler.cube.cw_cube() 
            MyHandler.cube.flip_cube()
            facelets = cam.detect_cube()
            MyHandler.cube_map["B"] = cam.analyze_face(facelets) if facelets else None

            MyHandler.cube.flip_cube(2)  
            facelets = cam.detect_cube()
            MyHandler.cube_map["F"] = cam.analyze_face(facelets) if facelets else None
            
            MyHandler.cube.ccw_cube() 
            MyHandler.cube.flip_cube()

        MyHandler.cube_status = True
        print(f"Cube map: {MyHandler.cube_map}")
        self.send_text_response("Cube scanned successfully. Ready for solving or scrambling.")

    def handle_cube_solving(self):
        """Computes the solution for the current cube state and executes the moves to solve it."""
        if not MyHandler.cube_status:
            self.send_text_response("Cube state not available. Please scan the cube first.", 400)
            return
        
        try:
            solution_instructions: list = MyHandler.cube.solve(MyHandler.cube_map)
            print(f"Solution instructions: {solution_instructions}")
            for move in solution_instructions:
                MyHandler.cube.execute_move(move)

            self.send_text_response("Cube solved successfully.")
        except ValueError as e:
            self.send_text_response(f"\nSolve Failed:\n{str(e)}", 400)

    def handle_cube_scramble(self):
        """Generates a random scramble and executes the moves to scramble the cube."""
        move_count = 5
        for _ in range(move_count):
            move = random.choice(["S", "F", "R"]) + random.choice(["", "'", "2"])
            MyHandler.cube.execute_move(move)

        self.send_text_response("Cube scrambled successfully.")

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

    # Failsafe: Ensure the image folder exists before starting the server
    os.makedirs(os.path.dirname(IMAGE_PATH), exist_ok=True)

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