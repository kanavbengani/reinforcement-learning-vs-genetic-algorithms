from typing import List
from Direction import Direction
from Board import Board
from ActionFunction import ActionFunction
from Action import Action
from State import State

import pygame

class Character:
    """
    Represents an agent in the game. Fields:
        - self.row: int: row coordinate of this agent
        - self.col: int: col coordinate of this agent
        - self.direction: Direction: The direction that this agent is facing. 
        - self.action_fn: ActionFunction: The function through which this agent selects its next action
    """
    def __init__(
        self, 
        action_fn: ActionFunction, 
        row: int, 
        col: int, 
        direction: Direction,
        tank_file: str) -> None:
        """
        Initializes the character with the given parameters.
        
        Parameters:
        action_fn (ActionFunction): The function through which this agent selects its next action
        row (int): The row position of the agent
        col (int): The column position of the agent
        direction (Direction): The direction that this agent is facing
        tank_file (str): The file path of the tank image
        """
        self.action_fn: ActionFunction = action_fn
        self.state: State = State(
            row=row, 
            col=col, 
            direction=direction, 
            opp_row=-1, 
            opp_col=-1)
        self.action: Action = None
        self.state_halfprime: State = self.state
        self.alive = True
        self.tank_file = tank_file

    def next_action(
        self, 
        board: Board) -> Board:
        """
        Selects the next action for this agent.

        Parameters:
        board (Board): The game board.

        Returns:
        Board: The updated game board.
        """
        self.state, self.action, self.state_halfprime, board = self.action_fn.apply(
            state=self.state,
            action=self.action,
            state_prime=self.computeState(board),
            board=board)
        return board

    
    def terminate(
        self, 
        board: Board,
        won: bool) -> None:
        """
        Notifies the agent if it has won or lost.

        Parameters:
        board (Board): The game board
        won (bool): Flag to indicate if the agent has won.
        """
        if won == False: self.alive = False
        self.action_fn.terminate(
            state=self.state,
            action=self.action,
            state_prime=self.computeState(board),
            won=won)


    def computeState(
        self, 
        board: Board) -> State:
        """
        Computes the state of the given board from this Character's perspective.
        
        Parameters:
        board (Board): The game board.
        
        Returns:
        State: state of the given board from this Character's perspective.
        """
        character_positions = board.getCharacters()

        opp_row, opp_col = None, None
        if character_positions[0] == (self.state_halfprime.row, self.state_halfprime.col):
            opp_row, opp_col = character_positions[1]
        else:
            opp_row, opp_col = character_positions[0]
        return self.state_halfprime.getStateWithDifferent(opp_row=opp_row, opp_col=opp_col)


    def draw(self, canvas, tile_size):
        tank = pygame.image.load(f"images/{self.tank_file}").convert_alpha()
        tank = pygame.transform.scale(tank, (tile_size * .9, tile_size * .9))
        tank = pygame.transform.rotate(tank, self.state_halfprime.direction.value * -90)
            
        canvas.blit(tank, (tile_size * 0.05 + self.state_halfprime.col * tile_size, tile_size * 0.05 + self.state_halfprime.row * tile_size))

        if self.alive == False:
            cross = pygame.image.load("images/cross.png").convert_alpha()
            cross = pygame.transform.scale(cross, (tile_size * .9, tile_size * .9))
            canvas.blit(cross, (tile_size * 0.05 + self.state_halfprime.col * tile_size, tile_size * 0.05 + self.state_halfprime.row * tile_size))
        