import pygame

from Board import Board
from Character import Character
from Direction import Direction
from RL import RL
from GA import GA
from tqdm import tqdm
import time
import sys
import os
import numpy as np

NUM_TILES = 5
TILE_SIZE = 50
DECAY = 0.9999995
NUM_EPISODES = 1_000_000
SAVE_EVERY = 10_000
OPTIMAL = False # if you want to use the optimal policy
gui_flag = False

if gui_flag:
    global canvas
    canvas: pygame.Surface = pygame.display.set_mode((NUM_TILES * TILE_SIZE, NUM_TILES * TILE_SIZE))

# pygame main method
def run_game(player1: Character, player2: Character):
    board: Board = Board(NUM_TILES, (player1.state.row, player1.state.col), (player2.state.row, player2.state.col))
    winner: Character = None

    if gui_flag:
        pygame.init()
        refresh(board, player1, player2)

    i = 0
    while i < 100: 
        board = player1.next_action(board)
        refresh(board, player1, player2)
        if board.done:
            winner = player1
            player1.terminate(board, True)
            player2.terminate(board, False)
            break
        
        board = player2.next_action(board)
        refresh(board, player1, player2)
        if board.done:
            winner = player2
            player1.terminate(board, False)
            player2.terminate(board, True)
            break

        i += 1

    return player1, player2, winner

def refresh(board: Board, player1: Character, player2:Character):
    if gui_flag:
        board.drawGrid(canvas, TILE_SIZE)
        player1.draw(canvas, TILE_SIZE)
        player2.draw(canvas, TILE_SIZE)
        pygame.display.flip()
        time.sleep(1)


# def main():
#     player1 = Character(RL(), 0, 0, Direction.UP, 100, 100, 1, 100, 100)
#     player2 = Character(GA(), NUM_TILES - 1, NUM_TILES - 1, Direction.DOWN, 100, 100, 2, 100, 100)
#     playerQueue = [player2]
#     queueSize = 8

#     # run all games
#     for i in range(10000):
#         newPlayerQueue = []

#         # RL player plays against each of GA players in the queue
#         for player2 in playerQueue:
#             player1Queue, player2Queue = run_game(player1, player2)
#             player1 = player1Queue[0]
#             newPlayerQueue += player2Queue
        
        
#         # GA players play against each other
#         playersToWins = {player: 0 for player in newPlayerQueue}
#         for i in range(len(newPlayerQueue)):
#             for j in range(i, len(newPlayerQueue)):
#                 _, _, winner = run_game(newPlayerQueue[i], newPlayerQueue[j])
#                 playersToWins[winner] += 1
        
#         # sort the number of wins and get top 8
#         topN = sorted(playersToWins.items(), key=lambda item: item[1], reverse=True)[:queueSize]
#         playerQueue = [i[0] for i in topN]

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

if __name__ == "__main__":
    # if reset argument is passed, delete all .pkl files
    if len(sys.argv) > 1:
        if sys.argv[1] == "reset":
            dir = os.listdir(os.getcwd())
            for item in dir:
                if item.endswith(".pkl"):
                    os.remove(item)
    player1, player2 = None, None

    RL_agent = RL(optimal=OPTIMAL, decay=DECAY)
    for ep in tqdm(range(NUM_EPISODES), unit="episode"):
        if ep % 2 == 0:
            player1 = Character(RL_agent, 0, 0, Direction.DOWN)
            player2 = Character(RL_agent, NUM_TILES - 1, NUM_TILES - 1, Direction.UP)
        else:
            player1 = Character(RL_agent, 0, NUM_TILES - 1, Direction.RIGHT)
            player2 = Character(RL_agent, NUM_TILES - 1, 0, Direction.LEFT)
        run_game(player1, player2)
        if ep % SAVE_EVERY == 0 and not OPTIMAL:
            RL_agent.write_to_file()
        RL_agent.decay_epsilon()

    if not OPTIMAL: RL_agent.write_to_file()