# Rubik cube module

## Classes and variables:
In Rubik's Cubes each piece is unique and is meant to only go in one place.

### Piece: Simple Enum representing each piece.

### Cube: Logical class to interact with the cube:
Scans the cameras and creates a logical representation of the cube.

* Data stored as a numpy array of Pieces sized(3, 3, 3)
* Arr[x][_][_] white, middle, yellow.
* Arr[_][x][_] red, middle, orange. 
* Arr[_][_][x] green, middle, blue.
* Example: Arr[0][0][0] would be a white, red, green spot, or [2][1][2] would be the yellow blue edge.

### Move: Represents a rotation of the cube, String of "Cube notation"

* Cube notation is a standardized way to represent how to rotate a cube.
* Spin clockwise, Counterclockwise is marked by adding an apostrophe `
* (U)p, (D)own, (R)ight, (L)eft, (F)ront, (B)ack
* 2 can be Added after to signal two turns.

## Functionalities:
The logic functions should be used to control the device.

The camera and servo functions are a more "barebone" way to use it, more for debugging.

# Logic functions:
* Root() -> bool: Sets up cube in place of the device.
* View() -> CubeData: Gets the camera data and returns the state of the cube.
* Solve() -> List[Moves]: Solves the cube until it fits on all sides.
* Scramble() -> List[Moves]: Randomly scrambles the cube
* Perform(List[Moves]): Rotates the cube by the given move set.
* Get_rotated() -> List[Moves]: Returns a list of all the moves done since last solved.

# Camera functions:
- pass

# Servo functions:
- pass

