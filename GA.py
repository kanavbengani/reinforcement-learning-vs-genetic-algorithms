from ActionFunction import ActionFunction
from Direction import Direction
from Board import Board
from Action import Action
from State import State
from typing import Tuple
import numpy as np
from ActionFunction import InvalidMove
import random
import pickle
import os

class GA(ActionFunction):
    def __init__(
            self, 
            optimal: bool = False, 
            min_population: int = 4, 
            max_population: int = 8, 
            mutation_rate: float = 0.05, 
            policies_file: str = 'policies.pkl'):
        self.policies: dict = {i: {} for i in range(max_population)}
        self.policy_explored: int = 0
        self.fitness: dict = {0: ()}
        self.cur_policy: int = 0
        self.turns: int = 0
        self.mutation_rate: float = mutation_rate
        self.min_population: int = min_population
        self.max_population: int = max_population
        self.policies_file: str = policies_file
        self.optimal: bool = optimal
        self.load_data()
        # 1. win: 1 turn
        # 2. win: 10 turns
        # 3. lost: 10 turns
        # 4. lost: 1 turns
        # win: 1, lost: 0
        # [(1, 1), (0, 10)]
        # win: 1, loss: 0
        
        # sorted(lst, key=lambda x: (-x[0], x[1] if x[0] == 1 else -1 * x[1]))

        # top 4 out of 8 original
        # new set of 4 policies + keeping the old top 4
        # run ti with this as the new "original"
        # best fitness at the end of all episodes is used for training

    def apply(self, state: State, action: Action, state_prime: State, board: Board) -> Tuple[State, Action, Board]:        
        state_prime_str = str(state_prime)
        if state_prime_str not in self.policies[self.cur_policy]:
            self.policies[self.cur_policy][state_prime_str] = np.zeros(len(Action))
            self.policies[self.cur_policy][state_prime_str][np.random.randint(0, len(Action))] = 1
            
        # Getting where current policy's action is 1
        new_action = np.where(self.policies[self.cur_policy][state_prime_str] == 1)[0][0]

        # Choosing the next action
        new_state, new_action, new_board = self.choose_action(state, new_action, board)

        # Updating the policy to remove invalid actions
        self.policies[self.cur_policy][state_prime_str] = np.zeros(len(Action))
        self.policies[self.cur_policy][state_prime_str][new_action.value] = 1

        return state_prime, new_action, new_state, new_board


    def choose_action(
        self,
        state: State,
        action: Action,
        board: Board) -> Tuple[State, Action, Board]:
        """
        Choose an action to execute.

        Parameters:
        state (State): state.
        action (Action): action.
        board (Board): The game board.

        Returns:
        tuple: Updated state-action pair after applying the action.
        """
        actions = set(Action)
        invalid_actions = set()
        while True:
            try:
                state_str = str(state)
                if state_str not in self.policies[self.cur_policy]:
                    self.policies[self.cur_policy][state_str] = np.zeros(len(Action))
                    self.policies[self.cur_policy][state_str][np.random.randint(0, len(Action))] = 1

                new_action = action
                # picking action to play
                if not self.optimal or new_action in invalid_actions:
                    # picking random action that is not invalid
                    new_action = np.random.choice(list(actions.difference(invalid_actions)))
                else:
                    # picking best action
                    new_action = Action(np.argmax(self.policies[self.cur_policy][state_str]))
                new_state, new_board = self.try_action(state, new_action, board)
                return new_state, new_action, new_board
            except InvalidMove:
                invalid_actions.add(new_action)


    def terminate(self, state: State, action: Action, state_prime: State, won: bool) -> None:
        self.fitness[self.cur_policy] = (1 if won else 0, self.turns, self.cur_policy)
        self.policy_explored += 1
        self.cur_policy += 1

        flag = False
        if self.cur_policy >= self.max_population-1: 
            best_fitnesses: dict = {
                k: v for k, v in sorted(
                    self.fitness.items(), 
                    key=lambda item: (-item[1][0], item[1][1] if item[1][0] == 1 else -1 * item[1][1]))}
            # best_fitnesses = sorted(self.fitness, key=lambda x: (-x[0], x[1] if x[0] == 1 else -1 * x[1]))
            new_policies = {}
            for i in range(self.min_population): 
                new_policies[i] = self.policies[list(best_fitnesses.keys())[i]]

            for i in range(self.min_population, self.max_population):
                new_policies[i] = {}
                #random combines and mutations here
                pair = (random.randint(0, self.min_population-1), random.randint(0, self.min_population-1))

                intersection = set(self.policies[pair[0]]) & set(self.policies[pair[1]])
                pair_0 = set(self.policies[pair[0]]) - intersection
                pair_1 = set(self.policies[pair[1]]) - intersection

                for state in intersection:
                    # random combination between the two chosen pairs
                    if random.random() > 0.5:
                        new_policies[i][state] = self.policies[pair[0]][state]
                    else:
                        new_policies[i][state] = self.policies[pair[1]][state]
                    
                    #mutation 
                    if random.random() > 1 - self.mutation_rate:
                        new_policies[i][state] = np.zeros(len(Action))
                        new_policies[i][state][np.random.randint(0, len(Action))] = 1

                # adding all states from pair[0] that was not in the intersection
                for state in pair_0:
                    new_policies[i][state] = self.policies[pair[0]][state]

                    # mutation
                    if random.random() > 1 - self.mutation_rate:
                        new_policies[i][state] = np.zeros(len(Action))
                        new_policies[i][state][np.random.randint(0, len(Action))] = 1

                # adding all states from pair[1] that was not in the intersection
                for state in pair_1:
                    new_policies[i][state] = self.policies[pair[1]][state]

                    # mutation
                    if random.random() > 1 - self.mutation_rate:
                        new_policies[i][state] = np.zeros(len(Action))
                        new_policies[i][state][np.random.randint(0, len(Action))] = 1
            
            self.policies = new_policies

            self.fitness = {0: {}}
            self.cur_policy = 0


        if type(self.policies[self.cur_policy]) == int:
            print(self.policies[self.cur_policy])
            raise Exception("IN TERMINATE" + str(flag))
        
        self.turns = 0


    def write_to_file(
        self) -> None:
        """
        Write the Q-table, number of updates, and epsilon value to files.
        """
        if len(self.policies) < self.max_population:
            raise Exception('Not enough policies to write to file.')
        with open(self.policies_file, 'wb') as f:
            pickle.dump(self.policies, f)


    def load_data(
        self) -> None:
        """
        Load the Q-table, number of updates, and epsilon value from files.
        """
        if os.path.exists(self.policies_file):
            with open(self.policies_file, 'rb') as f:
                self.policies = pickle.load(f)