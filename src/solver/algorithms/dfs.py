import time
import tracemalloc

from ..base import Solver

class DFSSolver(Solver):
    def _search(self, depth_limit: int, profile_memory: bool):
        """Internal search function containing the core DFS logic."""
        nodes_expanded_this_run = 0

        if profile_memory:
            tracemalloc.start()
            tracemalloc.clear_traces()

        start_time = time.time()

        visited = set()
        stack = [(self.board, [], 0)]
        visited.add(repr(self.board))
        
        solution_path = None

        while stack:
            board, path, depth = stack.pop()
            nodes_expanded_this_run += 1

            if board.is_solved():
                solution_path = path
                break

            if depth >= depth_limit:
                continue

            for move in reversed(board.get_possible_moves()):
                new_board = board.apply_move(move)
                new_board_repr = repr(new_board)
                if new_board_repr not in visited:
                    visited.add(new_board_repr)
                    stack.append((new_board, path + [move], depth + 1))
        
        search_time = time.time() - start_time
        
        peak_memory_kb = 0.0
        if profile_memory:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_memory_kb = peak / 1024

        return solution_path, search_time, peak_memory_kb, nodes_expanded_this_run

    def solve(self, depth_limit: int = 500):
        # --- Run 1: The "clean" run for accurate Time and Nodes Expanded stats ---
        solution, search_time, _, nodes_expanded = self._search(depth_limit, profile_memory=False)
        
        self.solution = solution
        self.search_time = search_time
        self.nodes_expanded = nodes_expanded
        self.memory_usage = 0.0

        # --- Run 2: The "profiled" run ---
        _, _, peak_memory, _ = self._search(depth_limit, profile_memory=True)
        self.memory_usage = peak_memory
        
        return self.solution