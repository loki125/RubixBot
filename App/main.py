from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .logic import *
import random

IMAGE_FB="scans/current_face_FB_hold.jpg",
IMAGE_LR="scans/current_face_LR_hold.jpg"

# Initialize the architecture
cube_solver = CubeLogic(image_path_fb=IMAGE_FB, image_path_lr=IMAGE_LR)
    
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount
@app.startup_event("startup")
def startup():
    print("Starting up...")


@app.get("/solve")
def solve_cube():
    try:
        cube_solver.solve()
        return {"message": "Cube solving initiated."}
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

@app.get("/scramble")
def scramble_cube():
    # Standard Kociemba moves
    moves =["U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", "L", "L'", "L2", "R", "R'", "R2"]
    
    # Generate a random 20-move scramble sequence
    scramble_seq = " ".join(random.choices(moves, k=20))
    
    try:
        # solve_from_kociemba just executes strings, so we can use it to scramble too!
        cube_solver.device.solve_from_kociemba(scramble_seq)
        return {"message": "Cube scrambling initiated.", "sequence": scramble_seq}
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

@app.get("/prepare/pull")
def prepare_pull():
    try:
        pull_instructions =[
            (Servos.FrontLinear, LinearServoInstr.RETRACT),
            (Servos.BackLinear, LinearServoInstr.RETRACT),
            (Servos.LeftLinear, LinearServoInstr.RETRACT),
            (Servos.RightLinear, LinearServoInstr.RETRACT),
            Timing.HorizontalTime
        ]
        cube_solver.device.execute_instructions(pull_instructions)
        return {"status": "Pulled all motors. Ready for cube insertion."}
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

@app.get("/prepare/push")
def prepare_push():
    try:
        push_instructions =[
            # Extend Front and Back first
            (Servos.FrontLinear, LinearServoInstr.EXTEND),
            (Servos.BackLinear, LinearServoInstr.EXTEND),
            Timing.HorizontalTime,
            
            # Extend Left and Right second
            (Servos.LeftLinear, LinearServoInstr.EXTEND),
            (Servos.RightLinear, LinearServoInstr.EXTEND),
            Timing.HorizontalTime
        ]
        cube_solver.device.execute_instructions(push_instructions)
        return {"status": "Pushed front/back motors, then left/right motors."}
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}