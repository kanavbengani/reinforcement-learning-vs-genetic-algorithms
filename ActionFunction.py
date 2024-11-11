from Direction import Direction
from Board import Board
from Action import Action
from Tile import Tile
from abc import ABC, abstractmethod

class ActionFunction():
    def __init__(self):
        pass

    def try_action(
        self, 
        action: Action, 
        row: int, 
        col: int, 
        direction: Direction, 
        max_ammo: int, 
        ammo: int, 
        speed: int, 
        max_fuel: int, 
        fuel: int, 
        board: Board):

        grid = board.getGrid()
        width = len(grid[0])
        height = len(grid)

        if fuel <= 0: 
            raise Exception("No fuel")

        new_row = row
        new_col = col
        if action in list(Action.move_delta.keys()):
            change = Action.move_delta[action]
            new_row = row + change[0]
            new_col = col + change[1]
            
            if not (
                0 <= new_row < height
                and 0 <= new_col < width):
                raise Exception("Not in bounds")
            elif not (grid[new_row][new_col] not in [Tile.WALL, Tile.CHARACTER]):
                raise Exception("Location taken")
            else:
                if grid[row][col] == Tile.CHARACTER_ON_STATION:
                    board.setGrid(row, col, Tile.STATION)
                elif grid[row][col] == Tile.CHARACTER:
                    board.setGrid(row, col, Tile.EMPTY)

                row, col = new_row, new_col

                if grid[row][col] == Tile.EMPTY:
                    board.setGrid(row, col, Tile.CHARACTER)
                elif grid[row][col] == Tile.STATION:
                    board.setGrid(row, col, Tile.CHARACTER_ON_STATION)
                    ammo = max_ammo
                    fuel = max_fuel + 1 # will be reduced later
                    

        elif action in Action.rotate_actions:
            if fuel <= 0:
                raise Exception("No fuel")
            else:
                shift = 1 if action == Action.ROTATE_GUN_RIGHT else -1
                direction = Direction((direction.value + shift) % 4)

        else: #shooting
            if ammo <= 0:
                raise Exception("No ammo")
            else:
                ammo -= 1
                cur_row = row + Direction.dir_delta[direction][0]
                cur_col = col + Direction.dir_delta[direction][1]

                while 0 <= cur_row < height and 0 <= cur_col < width:
                    if grid[cur_row][cur_col] == Tile.WALL:
                        board.setGrid(cur_row, cur_col, Tile.EMPTY)
                        break
                    if grid[cur_row][cur_col] in [Tile.CHARACTER, Tile.CHARACTER_ON_STATION]:
                        board.endGame()
                    cur_row += Direction.dir_delta[direction][0]
                    cur_col += Direction.dir_delta[direction][1]

        return new_row, new_col, direction, max_ammo, ammo, speed, max_fuel, fuel-1, board

    @abstractmethod
    def apply(self, row: int, col: int, direction: Direction, max_ammo: int, ammo: int, speed: int, max_fuel: int, fuel: int, board: Board): 
        pass