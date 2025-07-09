# ids.py

import time
import tracemalloc

from ..base import Solver

class IDSSolver(Solver):
    def _search(self, max_depth: int, timeout: float, profile_memory: bool):
        """
        Internal search function containing the core IDS logic.
        Now includes a timeout mechanism.
        """
        nodes_expanded_this_run = 0
        solution_path = None
        timed_out = False

        if profile_memory:
            tracemalloc.start()
            tracemalloc.clear_traces()

        start_time = time.time()
        
        # Outer loop iterates through depth limits
        for depth_limit in range(max_depth + 1):
            
            # --- Timeout Check 1: Before starting a new depth iteration ---
            # This is efficient as it checks between major work cycles.
            if time.time() - start_time > timeout:
                timed_out = True
                print("Timeout reached before finding a solution.")
                break

            # For IDS, the visited set must be reset for each iteration (DLS)
            visited_at_depth = {repr(self.board)}
            stack = [(self.board, [], 0)]
            
            # Inner loop performs Depth-Limited Search (DLS)
            while stack:
                
                # --- Timeout Check 2: Inside the most frequent loop ---
                # This makes the timeout more responsive but adds a small overhead.
                # Check every 1000 expanded nodes to balance responsiveness and performance.
                if nodes_expanded_this_run % 1000 == 0:
                    if time.time() - start_time > timeout:
                        timed_out = True
                        break # Break from the inner 'while' loop

                board, path, depth = stack.pop()
                nodes_expanded_this_run += 1

                if board.is_solved():
                    solution_path = path
                    break # Break from the inner 'while' loop

                if depth >= depth_limit:
                    continue
                
                for move in reversed(board.get_possible_moves()):
                    new_board = board.apply_move(move)
                    new_board_repr = repr(new_board)
                    if new_board_repr not in visited_at_depth:
                        visited_at_depth.add(new_board_repr)
                        stack.append((new_board, path + [move], depth + 1))
            
            # If a solution was found or timeout occurred, break the outer loop
            if solution_path is not None or timed_out:
                break
        
        # Ensure search_time reflects the actual time spent, up to the timeout
        search_time = time.time() - start_time
        
        peak_memory_kb = 0.0
        if profile_memory:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_memory_kb = peak / 1024
        
        # If timed out, the solution is None
        if timed_out:
            solution_path = None

        return solution_path, search_time, peak_memory_kb, nodes_expanded_this_run

    def solve(self, max_depth: int = 500, timeout: float = 60.0):
        """
        Solves the puzzle using IDS with a specified maximum depth and timeout.
        
        Args:
            max_depth (int): The maximum depth to search.
            timeout (float): The maximum time in seconds allowed for the search.
        """
        # --- Run 1: The "clean" run for accurate Time and Nodes Expanded stats ---
        solution, search_time, _, nodes_expanded = self._search(max_depth, timeout, profile_memory=False)
        
        self.solution = solution
        self.search_time = search_time
        self.nodes_expanded = nodes_expanded
        self.memory_usage = 0.0

        # --- Run 2: The "profiled" run for memory usage ---
        # Note: This second run might also time out. The memory usage will be
        # the peak usage up to that point.
        _, _, peak_memory, _ = self._search(max_depth, timeout, profile_memory=True)
        self.memory_usage = peak_memory
        
        return self.solution