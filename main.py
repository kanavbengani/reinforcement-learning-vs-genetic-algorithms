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

NUM_TILES = 9
TILE_SIZE = 50
DECAY = 0.999999
NUM_EPISODES = 1_000_000
SAVE_EVERY = 10_000
OPTIMAL = True # if you want to use policy as-is (no-randomness)
gui_flag = True

if gui_flag:
    global canvas
    canvas: pygame.Surface = pygame.display.set_mode((NUM_TILES * TILE_SIZE, NUM_TILES * TILE_SIZE))

# pygame main method
def run_game(player1: Character, player2: Character):
    board: Board = Board(NUM_TILES, (player1.state.row, player1.state.col), (player2.state.row, player2.state.col))

    if gui_flag:
        pygame.init()
        refresh(board, player1, player2)

    i = 0
    while i < 100: 
        board = player1.next_action(board)
        if board.done:
            player1.terminate(board, True)
            player2.terminate(board, False)
            break
        refresh(board, player1, player2)
        
        board = player2.next_action(board)
        if board.done:
            player1.terminate(board, False)
            player2.terminate(board, True)
            break
        refresh(board, player1, player2)

        i += 1
        if i == 100:
            player1.terminate(board, False)
            player2.terminate(board, False)
            break
    refresh(board, player1, player2)

def refresh(board: Board, player1: Character, player2:Character):
    if gui_flag:
        board.drawGrid(canvas, TILE_SIZE)
        player1.draw(canvas, TILE_SIZE)
        player2.draw(canvas, TILE_SIZE)
        pygame.display.flip()
        time.sleep(.1)

def rlvrl():
    player1, player2 = None, None

    RL_agent1 = RL(
        optimal=OPTIMAL,
        decay=DECAY,
        q_table_file="pkl_files/q_table_1rlvrl.pkl",
        num_updates_file="pkl_files/num_updates_1rlvrl.pkl",
        epsilon_file="pkl_files/epsilon_1rlvrl.pkl")
    
    RL_agent2 = RL(
        optimal=OPTIMAL, 
        decay=DECAY, 
        q_table_file="pkl_files/q_table_2rlvrl.pkl", 
        num_updates_file="pkl_files/num_updates_2rlvrl.pkl", 
        epsilon_file="pkl_files/epsilon_2rlvrl.pkl")
    
    for ep in tqdm(range(NUM_EPISODES), unit="episode"):
        if ep % 4 == 0:
            player1 = Character(RL_agent1, 0, 0, Direction.DOWN)
            player2 = Character(RL_agent2, NUM_TILES - 1, NUM_TILES - 1, Direction.UP)
        elif ep % 4 == 1:
            player1 = Character(RL_agent1, 0, NUM_TILES - 1, Direction.LEFT)
            player2 = Character(RL_agent2, NUM_TILES - 1, 0, Direction.RIGHT)
        elif ep % 4 == 2:
            player1 = Character(RL_agent1, NUM_TILES - 1, NUM_TILES - 1, Direction.UP)
            player2 = Character(RL_agent2, 0, 0, Direction.DOWN)
        else: 
            player1 = Character(RL_agent1, NUM_TILES - 1, 0, Direction.RIGHT)
            player2 = Character(RL_agent2, 0, NUM_TILES - 1, Direction.LEFT)

        run_game(player1, player2)
        if ep % SAVE_EVERY == 0 and not OPTIMAL:
            RL_agent1.write_to_file()
            RL_agent2.write_to_file()
        RL_agent1.decay_epsilon()
        RL_agent2.decay_epsilon()

    if not OPTIMAL:
        RL_agent1.write_to_file()
        RL_agent2.write_to_file()

def rlvga():
    player1, player2 = None, None

    RL_agent = RL(
        optimal=OPTIMAL,
        decay=DECAY,
        q_table_file="pkl_files/q_table_1rlvrl.pkl",
        num_updates_file="pkl_files/num_updates_1rlvrl.pkl",
        epsilon_file="pkl_files/epsilon_1rlvrl.pkl")
    
    GA_agent = GA(
        optimal=OPTIMAL, 
        min_population = 4, 
        max_population = 8, 
        mutation_rate = 0.05, 
        policies_file = 'pkl_files/policies_1gavga.pkl')
    
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


def gavga():
    player1, player2 = None, None

    GA_agent1 = GA(
        optimal=OPTIMAL, 
        min_population = 4, 
        max_population = 8, 
        mutation_rate = 0.05, 
        policies_file = 'pkl_files/policies_1gavga.pkl')
    
    GA_agent2 = GA(
        optimal=OPTIMAL, 
        min_population = 4, 
        max_population = 8, 
        mutation_rate = 0.05, 
        policies_file = 'pkl_files/policies_2gavga.pkl')
    
    for ep in tqdm(range(NUM_EPISODES), unit="episode"):
        if ep % 4 == 0:
            player1 = Character(GA_agent1, 0, 0, Direction.DOWN)
            player2 = Character(GA_agent2, NUM_TILES - 1, NUM_TILES - 1, Direction.UP)
        elif ep % 4 == 1:
            player1 = Character(GA_agent1, 0, NUM_TILES - 1, Direction.LEFT)
            player2 = Character(GA_agent2, NUM_TILES - 1, 0, Direction.RIGHT)
        elif ep % 4 == 2:
            player1 = Character(GA_agent1, NUM_TILES - 1, NUM_TILES - 1, Direction.UP)
            player2 = Character(GA_agent2, 0, 0, Direction.DOWN)
        else: 
            player1 = Character(GA_agent1, NUM_TILES - 1, 0, Direction.RIGHT)
            player2 = Character(GA_agent2, 0, NUM_TILES - 1, Direction.LEFT)

        run_game(player1, player2)
        if ep % SAVE_EVERY == 0 and not OPTIMAL:
            GA_agent1.write_to_file()
            GA_agent2.write_to_file()

    if not OPTIMAL:
        GA_agent1.write_to_file()
        GA_agent2.write_to_file()


if __name__ == "__main__":
    # if reset argument is passed, delete all .pkl files
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            if sys.argv[2] == "reset":
                for item in os.listdir("pkl_files/"):
                    if item.__contains__(f"{sys.argv[1]}.pkl"):
                        os.remove(os.path.join("pkl_files/", item))
            else:
                raise Exception("Invalid argument. Please use 'reset' as 2nd argument.")

        if sys.argv[1] == "rlvrl":
            rlvrl()
        elif sys.argv[1] == "rlvga": 
            rlvga()
        elif sys.argv[1] == "gavga":
            gavga()
        else: 
            raise Exception("Invalid argument. Please use 'rlvrl', 'rlvga', or 'gavga' as 1st argument.")
        