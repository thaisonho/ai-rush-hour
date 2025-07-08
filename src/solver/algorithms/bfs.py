import time
import tracemalloc
from collections import deque

from ..base import Solver
from move import Move

class BFSSolver(Solver):
    def _search(self, profile_memory: bool):
        """
        Internal search function containing the core BFS logic.
        This allows it to be called twice with different profiling settings.
        """
        nodes_expanded_this_run = 0

        # Start memory profiling only if requested
        if profile_memory:
            tracemalloc.start()
            tracemalloc.clear_traces()

        start_time = time.time()

        queue = deque([(self.board, [])])
        visited = {repr(self.board)}
        
        solution_path = None

        while queue:
            current_board, path = queue.popleft()
            nodes_expanded_this_run += 1

            # Early exit if a solution was already found in a different branch
            # This is a safety check for complex graph structures, though less common in BFS
            if solution_path is not None:
                break

            for move in current_board.get_possible_moves():
                new_board = current_board.apply_move(move)
                board_repr = repr(new_board)

                if board_repr not in visited:
                    new_path = path + [move]
                    if new_board.is_solved():
                        solution_path = new_path
                        # Break from the inner loop to stop exploring this node's children
                        break
                    visited.add(board_repr)
                    queue.append((new_board, new_path))
        
        search_time = time.time() - start_time
        
        peak_memory_kb = 0.0
        if profile_memory:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_memory_kb = peak / 1024

        # Return all metrics from this specific run
        return solution_path, search_time, peak_memory_kb, nodes_expanded_this_run

    def solve(self):
        # --- Run 1: The "clean" run for accurate Time and Nodes Expanded stats ---
        solution, search_time, _, nodes_expanded = self._search(profile_memory=False)

        # Store the definitive results from the clean run
        self.solution = solution
        self.search_time = search_time
        self.nodes_expanded = nodes_expanded
        self.memory_usage = 0.0 # Default memory usage

        # --- Run 2: The "profiled" run ---
        _, _, peak_memory, _ = self._search(profile_memory=True)
        self.memory_usage = peak_memory
        
        return self.solution