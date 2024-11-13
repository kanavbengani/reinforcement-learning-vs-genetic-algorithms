from ActionFunction import ActionFunction, InvalidMove, NoAmmo
from Action import Action
from Direction import Direction
from Board import Board
import numpy as np
import pickle
import os
from typing import Tuple, List

Q_TABLE_FILE = 'q_table.pkl'
NUM_UPDATES_FILE = 'num_updates.pkl'
EPSILON_FILE = 'epsilon.pkl'

class RL(ActionFunction):
    def __init__(
        self, 
        decay: float=0.99999, 
        optimal: bool=False):
        """
        Initialize the RL class.

        Parameters:
        decay (float): Decay rate for epsilon.
        optimal (bool): Flag to indicate if the agent should act optimally.
        """
        self.q_table: dict = {}
        self.num_updates: dict = {}
        self.epsilon: float = 1
        self.decay: float = decay
        self.gamma: float = 0.9
        self.optimal: bool = optimal
        self.load_data()


    def decay_epsilon(
        self) -> None:
        """
        Decay the epsilon value by the decay rate.
        """
        self.epsilon *= self.decay


    def hash_state(
        self, 
        row: int, 
        col: int, 
        direction: Direction, 
        ammo: int, 
        turns_left: int, 
        fuel: int, 
        opp_row: int, 
        opp_col: int) -> str:
        """
        Hash the state into a string.

        Parameters:
        row (int): Row position.
        col (int): Column position.
        direction (Direction): Direction of the agent.
        ammo (int): Amount of ammo.
        turns_left (int): Turns left.
        fuel (int): Amount of fuel.
        opp_row (int): Opponent's row position.
        opp_col (int): Opponent's column position.

        Returns:
        str: Hashed state.
        """
        return (
            str(row).zfill(2) + 
            str(col).zfill(2) + 
            str(direction.value).zfill(2) + 
            str(ammo).zfill(2) + 
            str(turns_left).zfill(2) + 
            str(fuel).zfill(2) + 
            str(opp_row).zfill(2) + 
            str(opp_col).zfill(2))


    def apply(
        self, 
        row: int,
        col: int, 
        direction: Direction, 
        max_ammo: int,
        ammo: int, 
        speed: int, 
        max_fuel: int, 
        fuel: int, 
        board: Board) -> Tuple[int, int, Direction, int, int, int, int, int, Board]:
        """
        Apply the RL algorithm to choose and execute an action.

        Parameters:
        row (int): Row position.
        col (int): Column position.
        direction (Direction): Direction of the agent.
        max_ammo (int): Maximum ammo.
        ammo (int): Current ammo.
        speed (int): Speed of the agent.
        max_fuel (int): Maximum fuel.
        fuel (int): Current fuel.
        board (Board): The game board.

        Returns:
        tuple: Updated state after applying the action.
        """
        if (fuel > 0):
            for turn in range(1, speed + 1):
                # Getting opponent's position
                character_positions: List[Tuple[int, int]] = board.getCharacters()
                opp_row, opp_col = None, None
                if character_positions[0] == (row, col):
                    opp_row = character_positions[1][0]
                    opp_col = character_positions[1][1]
                else: 
                    opp_row = character_positions[0][0]
                    opp_col = character_positions[0][1]
                
                while True:
                    # getting current state's hash
                    old_state = self.hash_state(row, col, direction, ammo, speed - turn + 1, fuel, opp_row, opp_col)
                    if old_state not in self.q_table:
                        self.q_table[old_state] = np.zeros(len(Action))
                        self.num_updates[old_state] = np.zeros(len(Action))
                    
                    # picking action to play
                    if not self.optimal and (np.random.random() <= self.epsilon):
                        # picking random action that is not invalid
                        action = Action(np.random.choice(np.where(self.q_table[old_state] != -1000000.)[0]))
                    else:
                        # picking best action
                        action = Action(np.argmax(self.q_table[old_state]))

                    try:
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
                    except (InvalidMove, NoAmmo)  as e:
                        self.q_table[old_state][action.value] = -1000000.
                        self.num_updates[old_state][action.value] += 1
                        continue

                    # updating eta using the number of updates associated with given state-action pair
                    eta = 1/(1 + self.num_updates[old_state][action.value])
                    
                    # getting new state's hash
                    new_state = self.hash_state(new_row, new_col, new_direction, new_ammo, speed - turn, new_fuel, opp_row, opp_col)
                    if new_state not in self.q_table:
                        self.q_table[new_state] = np.zeros(len(Action))
                        self.num_updates[new_state] = np.zeros(len(Action))

                    # updating num_updates table for given state-action pair
                    self.num_updates[old_state][action.value] += 1

                    reward = 0

                    # if character has run out of fuel, notifying the board
                    if new_fuel == 0:
                        reward += -500000.
                        board.runOutOfFuel()

                    # Rewards
                    # Game over
                    if board.done:
                        self.q_table[old_state][action.value] = (1 - eta) * self.q_table[old_state][action.value] + eta * (1000000. + (self.gamma * np.max(self.q_table[new_state])))
                        return new_row, new_col, new_direction, new_max_ammo, new_ammo, new_speed, new_max_fuel, new_fuel, new_board
                    
                    if board.tied:
                        self.q_table[old_state][action.value] = (1 - eta) * self.q_table[old_state][action.value] + eta * (reward + (self.gamma * np.max(self.q_table[new_state])))
                        return new_row, new_col, new_direction, new_max_ammo, new_ammo, new_speed, new_max_fuel, new_fuel, new_board
                   
                    flag = False
                        
                    # Shot does not hit opponent
                    if action == Action.SHOOT:
                        flag = True
                        reward += -500
                        
                    # Closer to opponent
                    pos = (row, col)
                    new_pos = (new_row, new_col)
                    opp_pos = (opp_row, opp_col)
                    if board.getManhattanDistance(new_pos, opp_pos) < board.getManhattanDistance(pos, opp_pos) and ammo > 0:
                        flag = True
                        reward += 100
                    
                    # Further from opponent when we have no ammo
                    if board.getManhattanDistance(new_pos, opp_pos) > board.getManhattanDistance(pos, opp_pos) and ammo == 0:
                        flag = True
                        reward += 100

                    # Facing opponent
                    if board.getFacing(new_pos, new_direction, opp_pos) > board.getFacing(pos, direction, opp_pos):
                        flag = True
                        reward += 100

                    # None of the above were accomplished, so negative reward
                    if not flag:
                        reward += -10

                    self.q_table[old_state][action.value] = (1 - eta) * self.q_table[old_state][action.value] + eta * (reward + (self.gamma * np.max(self.q_table[new_state])))
                    break

                if board.done: # prevent moves from happening after game ends
                    break

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


    def write_to_file(
        self) -> None:
        """
        Write the Q-table, number of updates, and epsilon value to files.
        """
        with open(Q_TABLE_FILE, 'wb') as f:
            pickle.dump(self.q_table, f)
        with open(NUM_UPDATES_FILE, 'wb') as f:
            pickle.dump(self.num_updates, f)
        with open(EPSILON_FILE, 'wb') as f:
            pickle.dump(self.epsilon, f)


    def load_data(
        self) -> None:
        """
        Load the Q-table, number of updates, and epsilon value from files.
        """
        if os.path.exists(Q_TABLE_FILE) and os.path.exists(NUM_UPDATES_FILE) and os.path.exists(EPSILON_FILE):
            with open(Q_TABLE_FILE, 'rb') as f:
                self.q_table = pickle.load(f)
            with open(NUM_UPDATES_FILE, 'rb') as f:
                self.num_updates = pickle.load(f)
            with open(EPSILON_FILE, 'rb') as f:
                self.epsilon = pickle.load(f)
                self.epsilon *= self.decay