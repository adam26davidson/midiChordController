from enum import Enum

class ChordButton(Enum):
    SOUTH = "south"
    WEST = "west"
    NORTH = "north"
    EAST = "east"

class ControlState :
    buttonQueue = []

    bassOn = False

    leftSecondaryOn = False
    rightSecondaryOn = False
     
    rightModulationOn = False
    leftModulationOn = False

    alternateOn = False
