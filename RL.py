from ActionFunction import ActionFunction
from Action import Action
from Direction import Direction
from Board import Board

class RL(ActionFunction):
    def __init__(self):
        pass


    def apply(self, row: int, col: int, direction: Direction, max_ammo: int, ammo: int, speed: int, max_fuel: int, fuel: int, board: Board):
        for turns in range(speed):
            action = Action.MOVE_DOWN #TODO
            row, col, direction, max_ammo, ammo, speed, max_fuel, fuel, board = self.try_action(
                action=action, 
                row=row, 
                col=col, 
                direction=direction, 
                max_ammo=max_ammo, 
                ammo=ammo, 
                speed=speed, 
                max_fuel=max_fuel, 
                fuel=fuel, 
                board=board)
            if board.done: #prevent moves from happening after game ends
                break

        return row, col, direction, max_ammo, ammo, speed, max_fuel, fuel, board