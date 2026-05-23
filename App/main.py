import logic
import random

# Initialize the architecture
cube_solver = logic.CubeLogic()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# @app.startup_event("startup")
# def startup():
#     print("Starting up...")


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
    moves = ["U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", "L", "L'", "L2", "R", "R'", "R2"]

    # Generate a random 20-move scramble sequence
    scramble_seq = " ".join(random.choices(moves, k=20))

    try:
        # solve_from_kociemba just executes strings, so we can use it to scramble too!
        cube_solver.device.solve_from_kociemba(scramble_seq)
        return {"message": "Cube scrambling initiated.", "sequence": scramble_seq}
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

if __name__ == '__main__':
    input()