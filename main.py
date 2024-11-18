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
import shutil

NUM_TILES = 5
TILE_SIZE = 50
DECAY = 0.99995
NUM_EPISODES = 100_000
SAVE_EVERY = 10_000
OPTIMAL = True # if you want to use the optimal policy
gui_flag = True

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
        if board.done:
            winner = player1
            player1.terminate(board, True)
            player2.terminate(board, False)
            break
        refresh(board, player1, player2)
        
        board = player2.next_action(board)
        if board.done:
            winner = player2
            player1.terminate(board, False)
            player2.terminate(board, True)
            break
        refresh(board, player1, player2)

        i += 1
    refresh(board, player1, player2)

    return player1, player2, winner

def refresh(board: Board, player1: Character, player2:Character):
    if gui_flag:
        board.drawGrid(canvas, TILE_SIZE)
        player1.draw(canvas, TILE_SIZE)
        player2.draw(canvas, TILE_SIZE)
        pygame.display.flip()
        time.sleep(1)

def rlvrl():
    player1, player2 = None, None

    RL_agent = RL(
        optimal=True, 
        decay=DECAY,
        q_table_file="pkl_files/q_table.pkl",
        num_updates_file="pkl_files/num_updates.pkl",
        epsilon_file="pkl_files/epsilon.pkl")
    
    RL_agent_training = RL(
        optimal=OPTIMAL, 
        decay=DECAY, 
        q_table_file="pkl_files/q_table_better.pkl", 
        num_updates_file="pkl_files/num_updates_better.pkl", 
        epsilon_file="pkl_files/epsilon_better.pkl")
    
    for ep in tqdm(range(NUM_EPISODES), unit="episode"):
        if ep % 4 == 0:
            player1 = Character(RL_agent, 0, 0, Direction.DOWN)
            player2 = Character(RL_agent_training, NUM_TILES - 1, NUM_TILES - 1, Direction.UP)
        elif ep % 4 == 1:
            player1 = Character(RL_agent, 0, NUM_TILES - 1, Direction.LEFT)
            player2 = Character(RL_agent_training, NUM_TILES - 1, 0, Direction.RIGHT)
        elif ep % 4 == 2:
            player1 = Character(RL_agent, NUM_TILES - 1, NUM_TILES - 1, Direction.UP)
            player2 = Character(RL_agent_training, 0, 0, Direction.DOWN)
        else: 
            player1 = Character(RL_agent, NUM_TILES - 1, 0, Direction.RIGHT)
            player2 = Character(RL_agent_training, 0, NUM_TILES - 1, Direction.LEFT)

        run_game(player1, player2)
        if ep % SAVE_EVERY == 0 and not OPTIMAL:
            # RL_agent.write_to_file()
            RL_agent_training.write_to_file()
        # RL_agent.decay_epsilon()
        RL_agent_training.decay_epsilon()

    if not OPTIMAL:
        RL_agent.write_to_file()
        RL_agent_training.write_to_file()

def rlvga():
    player1, player2 = None, None

    RL_agent = RL(
        optimal=True, 
        decay=DECAY,
        q_table_file="pkl_files/q_table.pkl",
        num_updates_file="pkl_files/num_updates.pkl",
        epsilon_file="pkl_files/epsilon.pkl")
    
    GA_agent = GA(
        optimal=OPTIMAL, 
        min_population = 4, 
        max_population = 8, 
        mutation_rate = 0.05, 
        policies_file = 'pkl_files/policies.pkl')
    
    for ep in tqdm(range(NUM_EPISODES), unit="episode"):
        if ep % 4 == 0:
            player1 = Character(RL_agent, 0, 0, Direction.DOWN)
            player2 = Character(GA_agent, NUM_TILES - 1, NUM_TILES - 1, Direction.UP)
        elif ep % 4 == 1:
            player1 = Character(RL_agent, 0, NUM_TILES - 1, Direction.LEFT)
            player2 = Character(GA_agent, NUM_TILES - 1, 0, Direction.RIGHT)
        elif ep % 4 == 2:
            player1 = Character(RL_agent, NUM_TILES - 1, NUM_TILES - 1, Direction.UP)
            player2 = Character(GA_agent, 0, 0, Direction.DOWN)
        else: 
            player1 = Character(RL_agent, NUM_TILES - 1, 0, Direction.RIGHT)
            player2 = Character(GA_agent, 0, NUM_TILES - 1, Direction.LEFT)

        run_game(player1, player2)
        if ep % SAVE_EVERY == 0 and not OPTIMAL:
            RL_agent.write_to_file()
            GA_agent.write_to_file()
        RL_agent.decay_epsilon()

    if not OPTIMAL:
        RL_agent.write_to_file()
        GA_agent.write_to_file()



if __name__ == "__main__":
    # if reset argument is passed, delete all .pkl files
    if len(sys.argv) > 1:
        if sys.argv[1] == "rlvrl":
            rlvrl()
        elif sys.argv[1] == "rlvga": 
            rlvga()
        else: 
            raise Exception("Invalid argument. Please use 'rlvrl' or 'rlvga'.")
        
        if len(sys.argv) > 2:
            if sys.argv[2] == "reset":
                shutil.rmtree("pkl_files/") if os.path.exists("pkl_files") else None
                os.mkdir("pkl_files")
    