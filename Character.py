from typing import List
from Direction import Direction
from Board import Board
from ActionFunction import ActionFunction

import pygame

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
    def __init__(self, action_fn: ActionFunction, row: int, col: int, direction: Direction, max_ammo: int, ammo: int, speed: int, max_fuel: int, fuel: int):
        self.action_fn = action_fn
        self.row = row
        self.col = col
        self.direction = direction
        self.max_ammo = max_ammo
        self.ammo = ammo
        self.speed = speed
        self.max_fuel = max_fuel
        self.fuel = fuel

    
    def next_action(self, board: Board) -> Board:
        self.row, self.col, self.direction, self.max_ammo, self.ammo, self.speed, self.max_fuel, self.fuel, board = self.action_fn.apply(
            row=self.row, 
            col=self.col, 
            direction=self.direction, 
            max_ammo=self.max_ammo, 
            ammo=self.ammo, 
            speed=self.speed, 
            max_fuel=self.max_fuel, 
            fuel=self.fuel, 
            board=board)
        return board

    def draw(self, canvas, tile_size):
        image = pygame.image.load("tank.png").convert_alpha()
        image = pygame.transform.scale(image, (tile_size * .9, tile_size * .9))
        image = pygame.transform.rotate(image, self.direction.value * -90)
            
        canvas.blit(image, (tile_size * 0.05 + self.col * tile_size, tile_size * 0.05 + self.row * tile_size))
        