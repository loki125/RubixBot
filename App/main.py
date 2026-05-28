import http.server
import socketserver
import sys
import os
import json
import time
import threading
from urllib.parse import urlparse, parse_qs

from core.camera import CameraClient
from core.robot import RobotClient
from core.config import DEFAULT_PORT, IMAGE_PATH, DEBUG_PATH

class SolverWorker(threading.Thread):
    def __init__(self, cube):
        super().__init__(daemon=True)
        self.cube = cube
        self.moves = []
        self.index = 0
        self.state = "IDLE"  # States: IDLE, SOLVING, PAUSED, ERROR
        self.error = None
        self.lock = threading.Lock()

    def run(self):
        while True:
            move_to_exec = None
            with self.lock:
                if self.state == "SOLVING":
                    if self.index < len(self.moves):
                        move_to_exec = self.moves[self.index]
                    else:
                        self.state = "IDLE"

            if move_to_exec:
                try:
                    self.cube.execute_move(move_to_exec)
                    time.sleep(0.70)
                    
                    with self.lock:
                        if self.state in ["SOLVING", "PAUSED"]:
                            self.index += 1
                except ValueError as e:
                    with self.lock:
                        self.error = str(e)
                        self.state = "ERROR"
            else:
                time.sleep(0.1)


class MyHandler(http.server.SimpleHTTPRequestHandler):
    cube_map = {
        'U': None, 
        'R': None,
        'F': None,
        'D': None, 
        'L': None, 
        'B': None
    }
    
    camera = CameraClient(image_path=IMAGE_PATH)
    cube = RobotClient()
    solver = SolverWorker(cube)  

    def __init__(self, *args, **kwargs):
        self.endpoints = {
            '/api/cam_status': self.handle_cam_status,
            '/api/face_scan': self.handle_face_scan,
            '/api/start_solve': self.handle_start_solve,
            '/api/pause_solve': self.handle_pause_solve,
            '/api/resume_solve': self.handle_resume_solve,
            '/api/reset_solve': self.handle_reset_solve,
            '/api/solve_status': self.handle_solve_status,
            '/api/execute_move': self.handle_execute_move,
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
        # Mute log spam for polling endpoints
        if "/api/image_timestamp" in self.path or "/api/solve_status" in self.path:
            return
        return

    def send_text_response(self, message: str, status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

    def handle_image_timestamp(self):
        if not os.path.exists(DEBUG_PATH):
            response_data = {"timestamp": 0, "path": f"/{DEBUG_PATH}"}
        else:
            mtime = os.path.getmtime(DEBUG_PATH)
            response_data = {"timestamp": mtime, "path": f"/{DEBUG_PATH}"}

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def handle_cam_status(self):
        with MyHandler.camera as cam:
            has_cube = cam.detect_cube() is not None
        
        if has_cube:
            self.send_text_response("Cube detected in view.")
        else:
            self.send_text_response("No cube detected.")

    def handle_face_scan(self): 
        query = parse_qs(urlparse(self.path).query)
        face = query.get('face', [None])[0]

        if not face:
            self.send_text_response("Missing 'face' parameter in request.", 400)
            return

        with MyHandler.camera as cam:
            facelets = cam.detect_cube()
            if facelets is None:
                self.send_text_response("No face detected.", 400)
                return

            MyHandler.cube_map[face] = cam.analyze_face(facelets)
        
        print(f"Cube map: {MyHandler.cube_map}")
        self.send_text_response(f"Face '{face}' scanned successfully.")

    def handle_start_solve(self):
        with MyHandler.solver.lock:
            if MyHandler.solver.state in ["SOLVING", "PAUSED"]:
                self.send_text_response("Solve already in progress.", 400)
                return
                
        try:
            solution_instructions: list = MyHandler.cube.solve(MyHandler.cube_map)
            print(f"Solution instructions: {solution_instructions}")
            
            with MyHandler.solver.lock:
                MyHandler.solver.moves = solution_instructions
                MyHandler.solver.index = 0
                MyHandler.solver.error = None
                MyHandler.solver.state = "SOLVING"
            
            self.send_text_response(f"Solve started! Total moves: {len(solution_instructions)}")
        except ValueError as e:
            self.send_text_response(f"\nSolve Failed:\n{str(e)}", 400)

    def handle_pause_solve(self):
        with MyHandler.solver.lock:
            if MyHandler.solver.state == "SOLVING":
                MyHandler.solver.state = "PAUSED"
        self.send_text_response("Solve paused. Hardware will halt after current move finishes.")

    def handle_resume_solve(self):
        with MyHandler.solver.lock:
            if MyHandler.solver.state == "PAUSED":
                MyHandler.solver.state = "SOLVING"
        self.send_text_response("Solve resumed.")

    def handle_reset_solve(self):
        with MyHandler.solver.lock:
            MyHandler.solver.state = "IDLE"
            MyHandler.solver.moves = []
            MyHandler.solver.index = 0
            MyHandler.solver.error = None
        self.send_text_response("Solve sequence reset.")

    def handle_solve_status(self):
        with MyHandler.solver.lock:
            state = MyHandler.solver.state
            index = MyHandler.solver.index
            moves = MyHandler.solver.moves
            error = MyHandler.solver.error

        current_move = moves[index] if index < len(moves) else None
        
        response_data = {
            "state": state,
            "current_move": current_move,
            "index": index,
            "total": len(moves),
            "error": error
        }
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def handle_execute_move(self):
        with MyHandler.solver.lock:
            if MyHandler.solver.state in ["SOLVING", "PAUSED"]:
                self.send_text_response("Cannot execute manual move while a solve sequence is active.", 400)
                return

        query = parse_qs(urlparse(self.path).query)
        move = query.get('move', [None])[0]

        try:
            self.cube.execute_move(move)
        except ValueError as e:
            self.send_text_response(str(e), 400)
            return

        self.send_text_response("Move executed successfully.")


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

    os.makedirs(os.path.dirname(IMAGE_PATH), exist_ok=True)

    MyHandler.solver.start()

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", port), MyHandler) as httpd:
        try:
            print(f"Server running on http://localhost:{port}")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()