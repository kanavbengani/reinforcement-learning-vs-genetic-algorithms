from enum import Enum
import pygame

class Tile(Enum):
    EMPTY = 0
    STATION = 1
    WALL = 2
    CHARACTER = 3
    CHARACTER_ON_STATION = 4

    def draw(self, canvas, position, tile_size): 
        colors = {
            Tile.EMPTY: (255, 255, 255), #white
            Tile.STATION: (255, 223, 0), #gold
            Tile.WALL: (0, 0, 0), #black
            Tile.CHARACTER: (255, 255, 255), #tank on white background
            Tile.CHARACTER_ON_STATION: (255, 223, 0), #tank on white background
        }

        color = colors[self]
        

        pygame.draw.rect(canvas, color, (position[0], position[1], tile_size, tile_size))
        pygame.draw.rect(canvas, (0,0,0), (position[0], position[1], tile_size, tile_size), 1)
        
        