# Performance Evaluation of Reinforcement Learning and Genetic Algorithms

__Premise__:

In this project, we seek to compare the results of an agent trained using reinforcement learning versus an agent trained using a genetic algorithm. Specifically, we seek to see which agent can more quickly learn to effectively play a game in a controlled environment. The game board is a rectangular grid, where two agents are placed at opposite corners of the grid. The agents attempt to win by shooting the other a single time; the agents can move up, down, left, right, move their gun in any of these directions, and shoot. The board contains impassable and indestructible walls; all other tiles can be passed and shot through.

__File Structure__:

* `images/`: Contains images used throughout the game
* `pkl_files/`: Contains files that contain the weights for trained models
* `Action.py`: Enumeration of possible actions agents can take
* `ActionFunction.py`: Abstract class defining how an agent acts (e.g., what action it takes in a given state)
* `Board.py`: Defines the board on which agents play the game
* `Character.py`: Represents an agent in the game, including its associated functionality and fields
* `Direction.py`: Enumeration of possible directions agents can move or rotate to
* `GA.py`: Implementation of genetic algorithm `ActionFunction`
* `RL.py`: Implementation of reinforcement learning `ActionFunction`
* `State.py`: Represents the state of the board
* `Tile.py`: Represents a single tile on the board
* `main.py`: Entry point to run the program

__To Run__:

Run the file `main.py` with one of the following as a command line argument:

* `rlvrl`: Play a game with a trained RL agent vs. a trained RL agent
* `rlvga`: Play a game with a trained RL agent as the first player vs. a trained GA agent as the second player
* `gavrl`: Play a game with a trained GA agent as the first player vs. a trained RL agent as the second player
* `gavga`: Play a game with a trained GA agent vs. a trained GA agent
* `optvga`: Play a game with the optimal agent as the first player vs. a GA agent as the second player
* `optvrl`: Play a game with the optimal agent as the first player vs. a RL agent as the second player
* `optvrl_10`: Play 10 games with the optimal agent as the first player vs. a RL agent as the second player
* `optvga_10`: Play 10 games with the optimal agent as the first player vs. a GA agent as the second player
* `training_opt`: Train the optimal agent

If you want to view the GUI while the games are running, make sure the 'gui_flag' is set to 'True' in 'main.py'

If you want to play the game without training the agents during the game, make sure 'OPTIMAL' is set to 'True' in 'main.py'

Some of these commands can be followed by 'reset' afterwards, indicating that you are removing the existing information on the agent in 'pkl_files' and training a new one. These include:

* 'rlvrl'
* 'gavga'
* 'optvrl'
* 'optvga'
