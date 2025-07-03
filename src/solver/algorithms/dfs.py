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

        def dfs(board, path, depth):
            nonlocal peak_memory
            current_memory = process.memory_info().rss
            if current_memory > peak_memory:
                peak_memory = current_memory

            if board.is_solved():
                return path
            if depth >= depth_limit:
                return None

            visited.add(repr(board))

            for move in board.get_possible_moves():
                new_board = board.apply_move(move)
                self.nodes_expanded += 1
                if new_board.is_solved():
                    return path + [move]
                if repr(new_board) in visited:
                    continue
                result = dfs(new_board, path + [move], depth + 1)
                if result is not None:
                    return result
            return None

        self.solution = dfs(self.board, [], 0)
        self.search_time = time.time() - start_time
        final_memory = process.memory_info().rss
        if final_memory > peak_memory:
            peak_memory = final_memory
        self.memory_usage = (peak_memory - initial_memory) / (1024)  # in kB
        return self.solution