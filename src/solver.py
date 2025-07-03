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
class UCSSolver(Solver):
    def solve(self):
        start_time = time.time()
        initial_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        # Priority queue: (cost, counter, path, board)
        # A counter is used to break ties in the priority queue
        counter = 0
        frontier = [(0, counter, [], self.board)]
        heapq.heapify(frontier)
        
        # Visited set to store board states
        visited = {repr(self.board)}

        while frontier:
            cost, _, path, current_board = heapq.heappop(frontier)

            self.nodes_expanded += 1

            if current_board.is_solved():
                self.solution = path
                self.search_time = time.time() - start_time
                final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                self.memory_usage = (final_memory - initial_memory) / 1024  # in KB
                return path

            for move in current_board.get_possible_moves():
                new_board = current_board.apply_move(move)
                board_repr = repr(new_board)

                if board_repr not in visited:
                    visited.add(board_repr)
                    
                    # Find the vehicle that moved to get its length for the cost
                    moved_vehicle = None
                    for vehicle in current_board.vehicles:
                        if vehicle.id == move.vehicle_id:
                            moved_vehicle = vehicle
                            break
                    
                    new_cost = cost + moved_vehicle.length
                    new_path = path + [move]
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, new_path, new_board))
        
        # If no solution is found
        self.search_time = time.time() - start_time
        self.solution = None
        return None
