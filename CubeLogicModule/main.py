import numpy
import numpy as np
from enum import Enum

class Piece(Enum):
    """

    """
    MIDDLE = 0

class Cube:
    """
    pass
    """

    def __init__(self):
        self.data = numpy.zeros((3, 3, 3), dtype=Piece)

if __name__ == '__main__':
    cube = Cube()
    print(cube.data)