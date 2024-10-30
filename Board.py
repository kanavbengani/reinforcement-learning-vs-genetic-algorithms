from Tile import Tile

class Board: 
    def __init__(self, num_tiles, player1_index, player2_index): 
        self.tiles = [[Tile.EMPTY for _ in range(num_tiles)] for _ in range(num_tiles)] 
        self.tiles[player1_index[0]][player1_index[1]] = Tile.CHARACTER
        self.tiles[player2_index[0]][player2_index[1]] = Tile.CHARACTER
        self.tiles[0][num_tiles//2] = Tile.STATION
        self.tiles[num_tiles-1][num_tiles//2] = Tile.STATION
        self.tiles[num_tiles//2][0] = Tile.STATION
        self.tiles[num_tiles//2][num_tiles-1] = Tile.STATION
        self.tiles[num_tiles//2][num_tiles//2] = Tile.STATION
        
        for row in range(1, len(self.tiles)-1, 2): 
            for col in range(1, len(self.tiles[0])-1, 2):
                self.tiles[row][col] = Tile.WALL

        self.done = False
                
    def getGrid(self):
        return self.tiles

    def setGrid(self, row, col, new_tile):
        self.tiles[row][col] = new_tile
    
    def drawGrid(self, canvas, tile_size):
        for row in range(len(self.tiles)):
            for col in range(len(self.tiles[0])):
                tile = self.tiles[row][col]
                tile.draw(canvas, (col*tile_size, row*tile_size), tile_size)

    def endGame(self):
        self.done = True