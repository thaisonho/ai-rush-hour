import time
import resource

from ..base import Solver
from move import Move

class DFSSolver(Solver):
    def solve(self, depth_limit: int = 50):
        self.nodes_expanded = 0
        self.solution = None
        self.memory_usage = 0

        start_time = time.time()
        initial_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        visited = set()

        def dfs(board, path, depth):
            if board.is_solved():
                return path
            if depth >= depth_limit:
                return None

            visited.add(repr(board))
            self.nodes_expanded += 1

            for move in board.get_possible_moves():
                new_board = board.apply_move(move)
                if repr(new_board) in visited:
                    continue
                result = dfs(new_board, path + [move], depth + 1)
                if result is not None:
                    return result
            return None

        self.solution = dfs(self.board, [], 0)
        self.search_time = time.time() - start_time
        final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.memory_usage = (final_memory - initial_memory) / 1024  # in KB
        return self.solution