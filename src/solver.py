from abc import ABC, abstractmethod
from board import Board

#import library for UCS
import time
import heapq
import resource
from move import Move


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
        # algorithms will be implemented later in subclasses
        pass

    def get_stats(self):
        # return the stats of the solver as a dictionary
        return {
            "solution": self.solution,
            "search_time": self.search_time,
            "memory_usage": self.memory_usage,
            "nodes_expanded": self.nodes_expanded,
        }
