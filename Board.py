from Tile import Tile
from Direction import Direction
import numpy as np
from typing import List, Tuple
from pygame import Surface

class Board:
    def __init__(
        self, 
        num_tiles: int, 
        player1_index: Tuple[int, int], 
        player2_index: Tuple[int, int]):
        """
        Initialize the board with given number of tiles and player positions.
        
        Parameters:
        num_tiles (int): Number of tiles in one dimension of the square board.
        player1_index (Tuple[int, int]): Tuple representing the position of player 1.
        player2_index (Tuple[int, int]): Tuple representing the position of player 2.
        """
        self.tiles: List[List[Tile]] = [[Tile.EMPTY for _ in range(num_tiles)] for _ in range(num_tiles)]
        self.tiles[player1_index[0]][player1_index[1]] = Tile.CHARACTER
        self.tiles[player2_index[0]][player2_index[1]] = Tile.CHARACTER
        self.tiles[num_tiles // 2][0] = Tile.STATION
        self.tiles[num_tiles // 2][num_tiles - 1] = Tile.STATION

        for row in range(1, len(self.tiles) - 1, 2):
            for col in range(1, len(self.tiles[0]) - 1, 2):
                self.tiles[row][col] = Tile.WALL

        self.outOfFuel: int = 0
        self.tied: bool = False
        self.done: bool = False


    def getGrid(
        self) -> List[List[Tile]]:
        """
        Get the current grid of tiles.

        Returns:
        2D list representing the grid of tiles.
        """
        return self.tiles


    def setGrid(
        self, 
        row: int, 
        col: int, 
        new_tile: Tile) -> None:
        """
        Set a new tile at the specified position in the grid.

        Parameters:
        row (int): Row index of the tile.
        col (int): Column index of the tile.
        new_tile (Tile): New tile to be placed at the specified position.
        """
        self.tiles[row][col] = new_tile


    def drawGrid(
        self, 
        canvas: Surface, 
        tile_size: int) -> None:
        """
        Draw the grid on the given canvas.

        Parameters:
        canvas (Surface): Canvas to draw the grid on.
        tile_size (int): Size of each tile.
        """
        for row in range(len(self.tiles)):
            for col in range(len(self.tiles[0])):
                tile = self.tiles[row][col]
                tile.draw(canvas, (col * tile_size, row * tile_size), tile_size)


    def getCharacters(
        self) -> List[Tuple[int, int]]:
        """
        Get the positions of all characters on the board.

        Returns:
        List of tuples representing the positions of characters.
        """
        locs = []
        for row in range(len(self.tiles)):
            for col in range(len(self.tiles[0])):
                tile = self.tiles[row][col]
                if tile in [Tile.CHARACTER, Tile.CHARACTER_ON_STATION]:
                    locs.append((row, col))
        return locs


    def getManhattanDistance(
        self, 
        pos1: Tuple[int, int], 
        pos2: Tuple[int, int]) -> int:
        """
        Calculate the Manhattan distance between two positions.

        Parameters:
        pos1 (Tuple[int, int]): First position as a tuple.
        pos2 (Tuple[int, int]): Second position as a tuple.
        
        Returns:
        Manhattan distance between the two positions.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


    def getFacing(
        self, 
        pos1: Tuple[int, int], 
        dir: Direction, 
        pos2: Tuple[int, int]) -> float:
        """
        Get the facing direction from pos1 to pos2 in the given direction.

        Paramaters:
        pos1 (Tuple[int, int]): Starting position as a tuple.
        dir (Direction): Direction to face.
        pos2 (Tuple[int, int]): Target position as a tuple.
        
        Returns:
        Dot product of the normalized vector and direction delta.
        """
        vec = np.array(pos2) - np.array(pos1)
        return (vec / np.linalg.norm(vec)).dot(Direction.dir_delta[dir])


    def normalize(
        self, 
        vector: np.ndarray) -> np.ndarray:
        """
        Normalize the given vector.

        Parameters:
        vector (np.ndarray): Vector to be normalized.
        
        Returns:
        Normalized vector.
        """
        return vector / np.linalg.norm(vector)

    def endGame(
        self) -> None:
        """
        End the game by setting the done flag to True.
        """
        self.done = True

    def runOutOfFuel(
        self) -> None:
        """
        Increment the outOfFuel counter and set the tied flag if both players are out of fuel.
        """
        self.outOfFuel += 1
        if self.outOfFuel == 2:
            self.tied = True