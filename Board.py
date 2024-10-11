from Character import Character
from Tile import Tile

class Board: 
    def __init__(self, num_tiles, player1, player2): 
        self.tiles = [[Tile.EMPTY for _ in range(num_tiles)] for _ in range(num_tiles)] 

        self.tiles[0][0] = Tile.CHARACTER

        self.player2 = Character(num_tiles - 1, num_tiles - 1)
        self.tiles[num_tiles - 1][num_tiles - 1] = Tile.CHARACTER
        
    def movePlayer1(self): 
        return self.player1.next_action()
        
    def movePlayer2(self): 
        return self.player2.next_action()


    def make_image(self): 
        pass