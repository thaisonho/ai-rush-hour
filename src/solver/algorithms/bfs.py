import time
import resource
from collections import deque

from ..base import Solver
from move import Move

class BFSSolver(Solver):
    def solve(self):
        self.nodes_expanded = 0
        self.solution = None
        self.memory_usage = 0

        start_time = time.time()
        initial_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        queue = deque([(self.board, [])])
        visited = {repr(self.board)}

        while queue:
            current_board, path = queue.popleft()
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
                    queue.append((new_board, path + [move]))

        self.search_time = time.time() - start_time
        final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.memory_usage = (final_memory - initial_memory) / 1024  # in KB
        self.solution = None
        return None