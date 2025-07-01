from abc import ABC, abstractmethod
from board import Board

class Solver(ABC):
    """
    An abstract class for implementing Search Algorithms.
    """

    def __init__(self, board: Board):
        self.board = board
        self.solution = None
        self.nodes_expanded = 0
        self.search_time = 0
        self.memory_usage = 0

    @abstractmethod
    def solve(self):
        """
        Solves the Rush Hour puzzle.

        This method must be implemented by subclasses. It should return a list
        of moves representing the solution path, or None if no solution is found.
        """
        pass

    def get_stats(self):
        """
        Returns the performance statistics of the solver.
        """
        return {
            "search_time": self.search_time,
            "memory_usage": self.memory_usage,
            "nodes_expanded": self.nodes_expanded,
        }
