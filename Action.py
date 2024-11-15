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

Action.move_delta = {
    Action.MOVE_UP: (-1, 0),
    Action.MOVE_DOWN: (1, 0),
    Action.MOVE_LEFT: (0, -1),
    Action.MOVE_RIGHT: (0, 1)
}

Action.rotate_actions = {
    Action.ROTATE_GUN_LEFT: -1,
    Action.ROTATE_GUN_RIGHT: 1
}