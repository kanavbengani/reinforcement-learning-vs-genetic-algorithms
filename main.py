import pygame

from Board import Board
from Character import Character

NUM_TILES = 15

# pygame main method
def run_game(player1, player2):
    pygame.init()

    tile_size = 50
    canvas = pygame.display.set_mode((NUM_TILES * tile_size, NUM_TILES * tile_size))   
    
    board: Board = Board(NUM_TILES, player1, player2)

    exit = False
    while not exit: 
        board.movePlayer1()

        # display

        board.movePlayer2()

    return player1.next_players(), player2.next_players(), winner



player1 = Character() # Character(speed: int, fuel: int, ammo: int, x: int, y: int, direction: Direction, action_fn: ActionFunction)
player2 = Character() # Character(speed: int, fuel: int, ammo: int, x: int, y: int, direction: Direction, action_fn: ActionFunction)
playerQueue = [player2]
queueSize = 8

# run all games
for i in range(10000):
    newPlayerQueue = []

    # RL player plays against each of GA players in the queue
    for player2 in playerQueue:
        player1Queue, player2Queue = run_game(player1, player2)
        player1 = player1Queue[0]
        newPlayerQueue += player2Queue
    
    
    # GA players play against each other
    playersToWins = {player: 0 for player in newPlayerQueue}
    for i in range(len(newPlayerQueue)):
        for j in range(i, len(newPlayerQueue)):
            _, _, winner = run_game(newPlayerQueue[i], newPlayerQueue[j])
            playersToWins[winner] += 1
    
    # sort the number of wins and get top 8
    topN = sorted(playersToWins.items(), key=lambda item: item[1], reverse=True)[:queueSize]
    playerQueue = [i[0] for i in topN]

    # GA TYPE 1
    # run_game gives us 8 new/old GA agents through combining and mutating
    # ends us with 64 newPlayerQueue
    # run 64(63)/2 times to find the winners
    # Pick the best 8 winners

    # GA TYPE 2
    # initially have 8 GA agents with different properties
    # Go through each GA agent fighting against the RL agent (for loop for the 8 players, for loop ends)
    #   run_game doesn't return a set of player2s, instead returns 1 GA agent and score associated
    # Pick the 4 best GA agents
    # Combine and mutate using those 4 best GA and run it again with your set of 8 GA agents
    # Go back to step 2 with this new queue of GA agents
    # Can have the RL agent learn from each of the fights (so learns 8 games, then learns from 8 games of new GA set)
        
    
    # set player queue to be the new 8 from run_game
    