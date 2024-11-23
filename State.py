from Direction import Direction

class State():
    def __init__(
        self, 
        row: int, 
        col: int, 
        direction: Direction, 
        opp_row: int, 
        opp_col: int):
        """
        Initializes state with given parameters.
        
        Parameters:
        row (int): Row position.
        col (int): Column position.
        direction (Direction): Direction of the agent.
        opp_row (int): Opponent's row position.
        opp_col (int): Opponent's column position.
        """
        self.row: int = row
        self.col: int = col
        self.direction: Direction = direction
        self.opp_row: int = opp_row
        self.opp_col: int = opp_col
        self.state: State = str(self)


    def __str__(self):
        return (
            str(self.row).zfill(2) + 
            str(self.col).zfill(2) + 
            str(self.direction.value).zfill(2) + 
            str(self.opp_row).zfill(2) + 
            str(self.opp_col).zfill(2))


    def __eq__(self, other):
        return self.state == other.state


    def getStateWithDifferent(
        self, 
        row: int = None, 
        col: int = None, 
        direction: Direction = None,
        opp_row: int = None, 
        opp_col: int = None):
        """
        Get state with different parameters.
        
        Parameters:
        row (int): Row position.
        col (int): Column position.
        direction (Direction): Direction of the agent.
        opp_row (int): Opponent's row position.
        opp_col (int): Opponent's column position.
        
        Returns: 
        state: State with different parameters.
        """
        return State(
            row = row if row is not None else self.row,
            col = col if col is not None else self.col,
            direction = direction if direction is not None else self.direction,
            opp_row = opp_row if opp_row is not None else self.opp_row, 
            opp_col = opp_col if opp_col is not None else self.opp_col)


    def isStart(self) -> bool:
        """
        Check if state is the start state.
        
        Returns:
        bool: True if state is the start state, False otherwise.
        """
        return self.opp_row == -1 and self.opp_col == -1