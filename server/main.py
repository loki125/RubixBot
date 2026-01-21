from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(title="RubixBot Server", version="1.0.0")

# --- Data Models ---

class CubeState(BaseModel):
    # Represents color grid of each face
    U: List[str] 
    D: List[str]
    F: List[str]
    B: List[str]
    L: List[str]
    R: List[str]

class SolveResponse(BaseModel):
    success: bool
    moves: int
    finalState: CubeState
    message: Optional[str] = None

class MoveRequest(BaseModel):
    move: str

# --- Routes ---

@app.get("/")
async def root():
    return {"status": "RubixBot Online", "system": "ready"}

@app.post("/detect", response_model=CubeState)
async def detect_cube():
    """
    Trigger the camera hardware to scan the cube.
    Returns the detected color state.
    """
    pass

@app.post("/solve", response_model=SolveResponse)
async def solve_cube():
    """
    Trigger the Kociemba solver or similar algorithm.
    Then trigger the robot motors to execute the moves.
    """
    pass

@app.post("/scramble", response_model=CubeState)
async def scramble_cube():
    """
    Randomly scramble the cube using the robot motors.
    """
    pass

@app.post("/move")
async def perform_move(req: MoveRequest):
    """
    Execute a single move on the robot (U, U', F, F', etc.)
    """
    # logic: motors.turn(req.move)
    return {"status": "executed", "move": req.move}

@app.get("/instructions", response_model=List[str])
async def get_instructions():
    """
    Return the last solution steps in notation (e.g. R, U, R', F...)
    """
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
