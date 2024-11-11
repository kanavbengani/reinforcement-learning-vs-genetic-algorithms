from ActionFunction import ActionFunction
from Action import Action
from Direction import Direction
from Board import Board
from Tile import Tile
import random
import numpy as np

class RL(ActionFunction):

    actions = [a.value for a in Action]

    def __init__(self, decay=0.9999999):
        self.q_table = {} # str -> np.array()
        self.q_table_num_updates = {} 
        self.epsilon = 1
        self.decay = decay
        self.gamma = 0.9 # Random number picked here

    def hash_state(self, row, col, direction, ammo, turns_left, fuel, opp_row, opp_col):
        return (
            str(row).zfill(2) + str(col).zfill(2) + str(direction).zfill(2) + 
            str(ammo).zfill(2) + str(turns_left).zfill(2) + str(fuel).zfill(2) + 
            str(opp_row).zfill(2) + str(opp_col).zfill(2))

    def apply(self, row: int, col: int, direction: Direction, max_ammo: int, ammo: int, speed: int, max_fuel: int, fuel: int, board: Board):
        if (fuel > 0):
            for turn in range(1, speed + 1):
                # Getting opponent's position
                character_positions = board.getCharacters()
                if character_positions[0] == (row, col):
                    opp_row = character_positions[1][0]
                    opp_col = character_positions[1][1]
                else:
                    opp_row = character_positions[0][0]
                    opp_col = character_positions[0][1]
                
                while True:
                    try:
                        possible_actions = np.array([Action.MOVE_UP, Action.MOVE_LEFT, Action.MOVE_DOWN, Action.MOVE_RIGHT, Action.ROTATE_GUN_LEFT, Action.ROTATE_GUN_RIGHT, Action.SHOOT])
                        if (random.random() <= self.epsilon):
                            action = np.random.choice(possible_actions)
                            print(action)
                            print(action.value)
                        else:
                            action = np.argmax(self.q_table[action.value])

                        old_state = self.hash_state(row, col, direction, ammo, speed - turn + 1, fuel, opp_row, opp_col)
                        if old_state not in self.q_table:
                            self.q_table[old_state] = np.zeros(len(possible_actions))
                            self.q_table_num_updates[old_state] = np.zeros(len(possible_actions))

                        eta = 1/(1 + self.q_table_num_updates[old_state][action.value])
                        
                        new_row, new_col, new_direction, new_max_ammo, new_ammo, new_speed, new_max_fuel, new_fuel, new_board = self.try_action(
                            action=action, 
                            row=row, 
                            col=col, 
                            direction=direction, 
                            max_ammo=max_ammo, 
                            ammo=ammo, 
                            speed=speed, 
                            max_fuel=max_fuel, 
                            fuel=fuel, 
                            board=board)

                    except Exception as e:
                        self.q_table[old_state][action.value] = -100000
                        self.q_table_num_updates[old_state][action.value] += 1
                        continue
                   
                    
                    new_state = self.hash_state(new_row, new_col, new_direction, new_ammo, speed - turn, new_fuel, opp_row, opp_col)
        
                    if new_state not in self.q_table:
                        self.q_table[new_state] = np.zeros(len(possible_actions))
                        self.q_table_num_updates[new_state] = np.zeros(len(possible_actions))

                    self.q_table_num_updates[old_state][action.value] += 1

                    if new_fuel == 0:
                        board.runOutOfFuel()

                    # Rewards
                    # Game over
                    if board.done:
                        self.q_table[old_state][action.value] = (1 - eta) * self.q_table[old_state][action.value] + eta * (1000000 + (self.gamma * np.max(self.q_table[new_state])))
                        return new_row, new_col, new_direction, new_max_ammo, new_ammo, new_speed, new_max_fuel, new_fuel, new_board
                    
                    if board.tied:
                        self.q_table[old_state][action.value] = (1 - eta) * self.q_table[old_state][action.value] + eta * (-1000000 + (self.gamma * np.max(self.q_table[new_state])))
                        return new_row, new_col, new_direction, new_max_ammo, new_ammo, new_speed, new_max_fuel, new_fuel, new_board
                   
                    flag = False
                    reward = 0
                    # Character on station
                    if board.getGrid()[row][col] == Tile.CHARACTER_ON_STATION:
                        flag = True
                        reward += 100
                        
                    # Shot does not hit opponent
                    if action == Action.SHOOT:
                        flag = True
                        reward += -100
                        
                    # Closer to opponent
                    pos = (row, col)
                    new_pos = (new_row, new_col)
                    opp_pos = (opp_row, opp_col)
                    if board.getManhattanDistance(new_pos, opp_pos) < board.getManhattanDistance(pos, opp_pos) and ammo > 0:
                        flag = True
                        reward += 10
                    
                    # Further from opponent when we have no ammo
                    if board.getManhattanDistance(new_pos, opp_pos) > board.getManhattanDistance(pos, opp_pos) and ammo == 0:
                        flag = True
                        reward += 10

                    # None of the above were accomplished, so negative reward
                    if not flag:
                        reward += -10

                    self.q_table[old_state][action.value] = (1 - eta) * self.q_table[old_state][action.value] + eta * (reward + (self.gamma * np.max(self.q_table[new_state])))
                    break

                if board.done: #prevent moves from happening after game ends
                    break

                self.epsilon *= self.decay

                row = new_row
                col = new_col
                direction = new_direction
                max_ammo = new_max_ammo
                ammo = new_ammo
                speed = new_speed
                max_fuel = new_max_fuel
                fuel = new_fuel
                board = new_board

        return row, col, direction, max_ammo, ammo, speed, max_fuel, fuel, board

# 
# YOUR position (25), YOUR direction (4)  YOUR speed (1-2), YOUR fuel (0-8), YOUR ammo (5), YOUR tile (2)
# ENEMY position, TILE ENEMY IS ON IS A STATION
# (7 * x * 7 * 4 * 3 * 2)^2
# "0707432"

#1-3 for MAX speed
#3-5 for MAX ammo
#

# for RL agent picking its stats, 

# (5 * 5 * 4 * 3 * 8 * 6 * 2) * (7 * 7) # 1 million