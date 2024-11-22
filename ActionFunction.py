from Direction import Direction
from Board import Board
from State import State
from Action import Action
from Tile import Tile
from abc import abstractmethod
from typing import Tuple

class ActionFunction():
    def __init__(self):
        pass

    def try_action(
        self, 
        state: State,
        action: Action, 
        board: Board) -> Tuple[State, Board]:
        """
        Try to apply the action to the given state and board.

        Parameters:
        state (State): The current state.
        action (Action): The action to apply.
        board (Board): The game board.

        Returns:
        tuple: Updated state and board after applying the action.
        """
        grid = board.getGrid()
        width = len(grid[0])
        height = len(grid)

        row, col, direction = state.row, state.col, state.direction
        if action in Action.move_delta: # moving
            change = Action.move_delta[action]
            new_row = row + change[0]
            new_col = col + change[1]
            
            if not (
                0 <= new_row < height
                and 0 <= new_col < width):
                raise InvalidMove("Not in bounds")
            elif not (grid[new_row][new_col] not in [Tile.WALL, Tile.CHARACTER]):
                raise InvalidMove("Location taken")
            else:
                board.setGrid(row, col, Tile.EMPTY)
                row, col = new_row, new_col
                board.setGrid(row, col, Tile.CHARACTER)

        elif action in Action.rotate_actions: # rotating
            change = Action.rotate_actions[action]
            direction = Direction((direction.value + change) % 4)

        else: # shooting
            cur_row = row + Direction.dir_delta[direction][0]
            cur_col = col + Direction.dir_delta[direction][1]

            while 0 <= cur_row < height and 0 <= cur_col < width:
                # if grid[cur_row][cur_col] == Tile.WALL:
                #     board.setGrid(cur_row, cur_col, Tile.EMPTY)
                #     break
                if grid[cur_row][cur_col] in [Tile.CHARACTER]:
                    board.endGame()
                    break
                cur_row += Direction.dir_delta[direction][0]
                cur_col += Direction.dir_delta[direction][1]
        return state.getStateWithDifferent(row=row, col=col, direction=direction), board

    @abstractmethod
    def apply(self, state: State,action: Action, state_prime: State, board: Board) -> Tuple[State, Action, Board]:        
        pass

    @abstractmethod
    def terminate(state: State, action: Action, state_prime: State, won: bool) -> None:
        pass

class InvalidMove(Exception):
    pass

class NoFuel(Exception):
    pass

class NoAmmo(Exception):
    pass