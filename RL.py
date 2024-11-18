from ActionFunction import ActionFunction, InvalidMove, NoAmmo
from Action import Action
from Direction import Direction
from Board import Board
from State import State
import numpy as np
import pickle
import os
from typing import Tuple, List

class RL(ActionFunction):
    def __init__(
        self, 
        decay: float = 0.99999, 
        optimal: bool = False,
        q_table_file: str = 'q_table.pkl',
        num_updates_file: str = 'num_updates.pkl',
        epsilon_file: str = 'epsilon.pkl'):
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
        self.q_table_file: str = q_table_file
        self.num_updates_file: str = num_updates_file
        self.epsilon_file: str = epsilon_file
        self.load_data()


    def decay_epsilon(
        self) -> None:
        """
        Decay the epsilon value by the decay rate.
        """
        self.epsilon *= self.decay


    def apply(
        self, 
        state: State,
        action: Action,
        state_prime: State,
        board: Board) -> Tuple[State, Action, Board]:
        """
        Apply the RL algorithm to choose and execute an action.

        Parameters:
        state (State): state.
        action (Action): action.
        state_prime (State): state prime.
        board (Board): The game board.

        Returns:
        tuple: Updated state-action pair after applying the action.
        """
        # if non-start state, then update q_table for state-action pair using state_prime
        if not state.isStart():
            state_str = str(state)
            state_prime_str = str(state_prime)
            if state_str not in self.q_table:
                self.q_table[state_str] = np.zeros(len(Action))
                self.num_updates[state_str] = np.zeros(len(Action))
            
            if state_prime_str not in self.q_table:
                self.q_table[state_prime_str] = np.zeros(len(Action))
                self.num_updates[state_prime_str] = np.zeros(len(Action))

            # calculating eta using the number of updates associated with given state-action pair
            eta = 1/(1 + self.num_updates[state_str][action.value])

            # updating num_updates table for given state-action pair
            self.num_updates[state_str][action.value] += 1
            
            # getting reward for the given state-action pair    
            reward = self.computeReward(state, action, state_prime, board)

            # updating q_table with reward
            self.q_table[state_str][action.value] = (
                (1 - eta) * self.q_table[state_str][action.value]
                + (eta) * (reward + (self.gamma * np.max(self.q_table[state_prime_str]))))

        new_state, new_action, new_board = self.choose_action(state_prime, board)

        return state_prime, new_action, new_state, new_board


    def choose_action(
        self,
        state: State,
        board: Board) -> Tuple[State, Action, Board]:
        """
        Choose an action to execute.

        Parameters:
        state (State): state.
        board (Board): The game board.

        Returns:
        tuple: Updated state-action pair after applying the action.
        """
        while True:
            try:
                state_str = str(state)
                if state_str not in self.q_table:
                    self.q_table[state_str] = np.zeros(len(Action))
                    self.num_updates[state_str] = np.zeros(len(Action))

                new_action = None
                # picking action to play
                if not self.optimal and (np.random.random() <= self.epsilon):
                    # picking random action that is not invalid
                    new_action = Action(np.random.choice(np.where(self.q_table[state_str] != -1.e+10)[0]))
                else:
                    # picking best action
                    new_action = Action(np.argmax(self.q_table[state_str]))
                new_state, new_board = self.try_action(state, new_action, board)
                return new_state, new_action, new_board
            except InvalidMove:
                if state_str not in self.q_table:
                    self.q_table[state_str] = np.zeros(len(Action))
                    self.num_updates[state_str] = np.zeros(len(Action))
                    
                self.q_table[state_str][new_action.value] = -1.e+10
                continue

        
    def computeReward(
        self,
        state: State,
        action: Action,
        state_prime: State,
        board: Board) -> float:
        """
        Compute the reward for the given state-action pair.

        Parameters:
        state (State): state.
        state_prime (State): state prime.
        board (Board): The game board.

        Returns:
        float: Reward for the given state-action pair.
        """
        # default reward
        reward = -10


        # if agent missed a shot
        if action == Action.SHOOT:
            reward += -490
        # if closer to the opponent
        elif (
            board.getManhattanDistance((state.row, state.col), (state.opp_row, state.opp_col)) 
            > board.getManhattanDistance((state_prime.row, state_prime.col), (state_prime.opp_row, state_prime.opp_col))):
            reward += 110

        # if facing towards the opponent more
        elif (
            board.getFacing((state.row, state.col), state.direction, (state.opp_row, state.opp_col)) 
            < board.getFacing((state_prime.row, state_prime.col), state_prime.direction, (state_prime.opp_row, state_prime.opp_col))):
            reward += 110
            
        return reward

    def terminate(
        self,
        state: State,
        action: Action,
        state_prime: State,
        won: bool) -> None:
        """
        Notify the agent that the opponent has won.

        Parameters:
        state (State): state.
        action (Action): action.
        state_prime (State): state prime.
        won (bool): Flag to indicate if the agent has won.
        """
        state_str = str(state)
        state_prime_str = str(state_prime)
        if state_str not in self.q_table:
            self.q_table[state_str] = np.zeros(len(Action))
            self.num_updates[state_str] = np.zeros(len(Action))
        
        if state_prime_str not in self.q_table:
            self.q_table[state_prime_str] = np.zeros(len(Action))
            self.num_updates[state_prime_str] = np.zeros(len(Action))

        # calculating eta using the number of updates associated with given state-action pair
        eta = 1/(1 + self.num_updates[state_str][action.value])

        # updating num_updates table for given state-action pair
        self.num_updates[state_str][action.value] += 1

        # updating q_table with reward
        self.q_table[state_str][action.value] = (
                (1 - eta) * self.q_table[state_str][action.value]
                + (eta) * ((1.e+06 if won else -1.e+06) + (self.gamma * np.max(self.q_table[state_prime_str]))))


    def write_to_file(
        self) -> None:
        """
        Write the Q-table, number of updates, and epsilon value to files.
        """
        with open(self.q_table_file, 'wb') as f:
            pickle.dump(self.q_table, f)
        with open(self.num_updates_file, 'wb') as f:
            pickle.dump(self.num_updates, f)
        with open(self.epsilon_file, 'wb') as f:
            pickle.dump(self.epsilon, f)


    def load_data(
        self) -> None:
        """
        Load the Q-table, number of updates, and epsilon value from files.
        """
        if os.path.exists(self.q_table_file) and os.path.exists(self.num_updates_file) and os.path.exists(self.epsilon_file):
            with open(self.q_table_file, 'rb') as f:
                self.q_table = pickle.load(f)
            with open(self.num_updates_file, 'rb') as f:
                self.num_updates = pickle.load(f)
            with open(self.epsilon_file, 'rb') as f:
                self.epsilon = pickle.load(f)
                self.epsilon *= self.decay