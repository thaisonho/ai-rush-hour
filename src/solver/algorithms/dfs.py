import time
import psutil
import os

from ..base import Solver
from move import Move

class DFSSolver(Solver):
    def solve(self, depth_limit: int = 50):
        self.nodes_expanded = 0
        self.solution = None
        self.memory_usage = 0

        process = psutil.Process(os.getpid())
        start_time = time.time()
        initial_memory = process.memory_info().rss
        peak_memory = initial_memory

        visited = set()
        stack = [(self.board, [], 0)]  # (board, path, depth)
        visited.add(repr(self.board))

        while stack:
            board, path, depth = stack.pop()

            current_memory = process.memory_info().rss
            if current_memory > peak_memory:
                peak_memory = current_memory

            if board.is_solved():
                self.solution = path
                break

            if depth >= depth_limit:
                continue

            for move in reversed(board.get_possible_moves()):
                new_board = board.apply_move(move)
                self.nodes_expanded += 1
                if repr(new_board) not in visited:
                    if new_board.is_solved():
                        self.solution = path + [move]
                        stack.clear()
                        break
                    
                    visited.add(repr(new_board))
                    stack.append((new_board, path + [move], depth + 1))

        self.search_time = time.time() - start_time
        final_memory = process.memory_info().rss
        if final_memory > peak_memory:
            peak_memory = final_memory
        self.memory_usage = (peak_memory - initial_memory) / (1024)  # in kB
        return self.solution