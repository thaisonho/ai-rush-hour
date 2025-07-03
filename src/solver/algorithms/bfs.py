import time
import psutil
import os
from collections import deque

from ..base import Solver
from move import Move

class BFSSolver(Solver):
    def solve(self):
        self.nodes_expanded = 0
        self.solution = None
        self.memory_usage = 0

        process = psutil.Process(os.getpid())
        start_time = time.time()
        initial_memory = process.memory_info().rss
        peak_memory = initial_memory

        queue = deque([(self.board, [])])
        visited = {repr(self.board)}

        while queue:
            current_board, path = queue.popleft()
            self.nodes_expanded += 1

            current_memory = process.memory_info().rss
            if current_memory > peak_memory:
                peak_memory = current_memory

            for move in current_board.get_possible_moves():
                new_board = current_board.apply_move(move)

                # Early goal testing
                if new_board.is_solved():
                    path.append(move)
                    self.solution = path
                    self.search_time = time.time() - start_time
                    final_memory = process.memory_info().rss
                    if final_memory > peak_memory:
                        peak_memory = final_memory
                    self.memory_usage = (peak_memory - initial_memory) / (1024 * 1024)  # in MB
                    return path

                board_repr = repr(new_board)

                if board_repr not in visited:
                    visited.add(board_repr)
                    queue.append((new_board, path + [move]))

        self.search_time = time.time() - start_time
        final_memory = process.memory_info().rss
        if final_memory > peak_memory:
            peak_memory = final_memory
        self.memory_usage = (peak_memory - initial_memory) / (1024 * 1024)  # in MB
        self.solution = None
        return None