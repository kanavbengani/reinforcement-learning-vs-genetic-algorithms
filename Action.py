from enum import Enum

#space
class Action(Enum):
    MOVE_UP = 0
    MOVE_LEFT = 1
    MOVE_DOWN = 2
    MOVE_RIGHT = 3
    ROTATE_GUN_LEFT = 4
    ROTATE_GUN_RIGHT = 5
    SHOOT = 6