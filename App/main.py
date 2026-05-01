from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .logic import *

IMAGE_PATH = "images/current.jpg"

# Initialize the architecture
device = DeviceInterface(image_path=IMAGE_PATH)
image_processor = ImageProc(image_path=IMAGE_PATH)
cube_solver = CubeLogic(device=device, image_proc=image_processor)
    
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount
@app.startup_event("startup")
def startup():
    print("Starting up...")


@app.get("/solve")
def solve_cube():
    cube_solver.solve()
    return {"message": "Cube solving initiated."}

@app.get("/scramble")
def scramble_cube():
    # Placeholder for cube scrambling logic
    return {"message": "Cube scrambling initiated."}

@app.get("/status")
def status():
    return {"status": "Cube Detected, Ready to Solve."}