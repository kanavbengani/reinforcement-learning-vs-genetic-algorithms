from typing import List
from Direction import Direction
from Board import Board
from ActionFunction import ActionFunction

class Character:
    """
    Represents an agent in the game. Fields:
        - self.speed: Int: The number of tiles this agent can move in one turn
        - self.fuel: Int: The amount of fuel this agent currently has.
        - self.ammo: Int: The ammo that this agent currently has
        - self.x: Int: X coordinate of this agent
        - self.y: Int: Y coordinate of this agent
        - self.direction: Direction: The direction that this agent is facing. 
        - self.action_fn: ActionFunction: The function through which this agent selects its next action
    """
    def __init__(self, speed: int, fuel: int, ammo: int, x: int, y: int, direction: Direction, action_fn: ActionFunction):
        self.speed = speed
        self.fuel = fuel
        self.ammo = ammo
        self.x = x
        self.y = y
        self.direction = direction
        self.action_fn = action_fn
    
    def next_action(self, board: Board):
        cur_board = board
        for _ in range(self.speed):
            cur_board = self.action_fn.apply(self.speed, self.fuel, self.ammo, self.x, self.y, self.direction, cur_board)
            self.fuel -= 1
        return board