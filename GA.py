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
        self.num_episodes: int = 0

        # self.fitness: dict = {}

        self.policy_fitness: dict = {}
        self.fitness: dict = {i: {} for i in range(max_population)}

        self.cur_policy: int = 0
        self.turns: int = 0
        self.mutation_rate: float = mutation_rate
        self.min_population: int = min_population
        self.max_population: int = max_population
        self.policies_file: str = policies_file
        self.optimal: bool = optimal
        self.load_data()


    def apply(self, state: State, action: Action, state_prime: State, board: Board) -> Tuple[State, Action, Board]:        
        state_prime_str = str(state_prime)
        if self.cur_policy not in self.policies:
            self.policies[self.cur_policy] = {}

        if state_prime_str not in self.policies[self.cur_policy]:
            self.policies[self.cur_policy][state_prime_str] = np.zeros(len(Action))
            self.policies[self.cur_policy][state_prime_str][np.random.randint(0, len(Action))] = 1
            

        # if non-start state, then update fitness for state-action pair using state_prime
        if (not self.optimal) and (not state.isStart()):
            # getting reward for the given state-action pair
            reward = self.computeReward(state, action, state_prime, board)

            # updating fitness with reward
            if self.cur_policy in self.policy_fitness:
                self.policy_fitness[self.cur_policy] += reward
            else:
                self.policy_fitness[self.cur_policy] = reward

            if self.cur_policy not in self.fitness:
                self.fitness[self.cur_policy] = {}

            if str(state) not in self.fitness[self.cur_policy]:
                self.fitness[self.cur_policy][str(state)] = 0

            self.fitness[self.cur_policy][str(state)] += reward


        # Getting where current policy's action is 1
        new_action = np.where(self.policies[self.cur_policy][state_prime_str] == 1)[0][0]

        # Choosing above action if valid, else choosing another random action
        new_state, new_action, new_board = self.choose_action(state_prime, new_action, board)

        # If random action chosen, updating the policy to reflect the new action
        self.policies[self.cur_policy][state_prime_str] = np.zeros(len(Action))
        self.policies[self.cur_policy][state_prime_str][new_action.value] = 1

        # increment turns
        self.turns += 1
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
        new_action = action

        while True:
            try:
                state_str = str(state)
                if state_str not in self.policies[self.cur_policy]:
                    self.policies[self.cur_policy][state_str] = np.zeros(len(Action))
                    self.policies[self.cur_policy][state_str][np.random.randint(0, len(Action))] = 1

                # picking action to play
                if new_action in invalid_actions:
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
        if not self.optimal:
            if str(state) not in self.fitness[self.cur_policy]:
                self.fitness[self.cur_policy][str(state)] = 0

            self.policy_fitness[self.cur_policy] += (1.e+06 if won else -1.e+06)
            self.fitness[self.cur_policy][str(state)] += (1.e+06 if won else -1.e+06)
            if self.num_episodes % 4 == 3:
                self.cur_policy += 1
            self.num_episodes += 1
            self.turns = 0


            # if self.cur_policy in self.fitness:
            #     self.fitness[self.cur_policy] += 1 if won else 0
            # else:
            #     self.fitness[self.cur_policy] = 1 if won else 0
            # # self.fitness[self.cur_policy] = (1 if won else 0, self.turns)
            # self.num_episodes += 1
            # if self.num_episodes % 4 == 3:    
            #     self.cur_policy += 1
            # self.turns = 0

            if self.cur_policy >= self.max_population: 
                best_fitnesses: dict = {
                    k: v for k, v in sorted(
                        self.policy_fitness.items(), 
                        # self.fitness.items(), 
                        key=lambda item: -item[1])}
                        # key=lambda item: (-item[1][0], item[1][1] if item[1][0] == 1 else -1 * item[1][1]))}

                new_policies = {}
                for i in range(self.min_population): 
                    new_policies[i] = self.policies[list(best_fitnesses.keys())[i]]

                for i in range(self.min_population, self.max_population):
                    new_policies[i] = {}
                    #random combines and mutations here
                    pair = (random.randint(0, self.min_population-1), random.randint(0, self.min_population-1))

                    intersection = set(self.fitness[pair[0]]) & set(self.fitness[pair[1]])
                    pair_0 = set(self.fitness[pair[0]]) - intersection
                    pair_1 = set(self.fitness[pair[1]]) - intersection

                    
                    # intersection = set(self.policies[pair[0]]) & set(self.policies[pair[1]])
                    # pair_0 = set(self.policies[pair[0]]) - intersection
                    # pair_1 = set(self.policies[pair[1]]) - intersection

                    for state in intersection:

                        # combination between the two chosen pairs (chooses better pair)
                        if self.fitness[pair[0]][state] > self.fitness[pair[1]][state]:
                            new_policies[i][state] = self.policies[pair[0]][state]
                        else:
                            new_policies[i][state] = self.policies[pair[1]][state]

                        # random combination between the two chosen pairs
                        # if random.random() > 0.5:
                        #     new_policies[i][state] = self.policies[pair[0]][state]
                        # else:
                        #     new_policies[i][state] = self.policies[pair[1]][state]
                        
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
                l = list(self.policies.items())
                np.random.shuffle(l)
                self.policies = dict(l)

                self.policy_fitness = {}
                self.fitness = {i: {} for i in range(self.max_population)}

                # self.fitness = {}


                self.cur_policy = 0
        
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
        reward = -100

        # if agent missed a shot
        if action == Action.SHOOT:
            reward += -400
            
        # if closer to the opponent
        elif (
            board.getManhattanDistance((state.row, state.col), (state.opp_row, state.opp_col)) 
            > board.getManhattanDistance((state_prime.row, state_prime.col), (state_prime.opp_row, state_prime.opp_col))):
            reward += 200

        # if facing towards the opponent more
        elif (
            board.getFacing((state.row, state.col), state.direction, (state.opp_row, state.opp_col)) 
            < board.getFacing((state_prime.row, state_prime.col), state_prime.direction, (state_prime.opp_row, state_prime.opp_col))):
            reward += 200

        return reward


    def write_to_file(
        self) -> None:
        """
        Write the Q-table, number of updates, and epsilon value to files.
        """
        if not self.optimal:
            with open(self.policies_file, 'wb') as f:
                pickle.dump({k: self.policies[k] for k in range(self.min_population)}, f)


    def load_data(
        self) -> None:
        """
        Load the Q-table, number of updates, and epsilon value from files.
        """
        if os.path.exists(self.policies_file):
            with open(self.policies_file, 'rb') as f:
                self.policies = pickle.load(f)