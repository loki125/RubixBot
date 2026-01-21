# RubixBot

## materials

* 4 x DS3218 Servo Motor with Horn: http://amzn.to/2x8ygyH  
* 1 pack (8 pcs) x 150 mm Servo Extension Lead, Male-to-Female: http://amzn.to/2yz6wVp  
* 4 x Hitec HS-311 Servo Motor: http://amzn.to/2yuRkLy  
* 1 x Pololu Mini Maestro 12-Channel USB Servo Controller (Assembled): http://amzn.to/2xRtQvq  
* 1 x USB 5 MP or 12 MP Webcam with 6 LEDs: http://amzn.to/2gnQYvp  
* 1 x 6V, 3A (3000 mA) power source, wall-plugged or rechargeable: http://amzn.to/2yAyXnp  
* 1 x Standard-Size Rubik's Cube: http://amzn.to/2xR7Pgz  
* 80 x Metric M3-12 Phillips-head Countersunk Bolts: http://amzn.to/2zmXmdP  
* 40 x Metric M3 Nuts: http://amzn.to/2yAoOW6  
* 20 x Small 2mm Wood screws or Metric M2x8 Bolts: http://amzn.to/2x8Qwb1  

## Plan
Client(User device) connects via http to raspberry server via fastAPI

FastAPI lets clients call functions on servers easily so client just needs to do call(function_name, *args, **kwags) basically.

Server has following functions:
* Root() -> bool: Sets up cube in place of the device.
* View() -> CubeData: Gets the camera data and returns the state of the cube.
* Solve() -> List[Moves]: Solves the cube until it fits on all sides.
* Scramble() -> List[Moves]: Randomly scrambles the cube
* Perform(List[Moves]): Rotates the cube by the given move set.
* Get_rotated() -> List[Moves]: Returns a list of all the moves done since last solved.
