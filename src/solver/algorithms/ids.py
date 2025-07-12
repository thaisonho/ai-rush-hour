import time
import tracemalloc

from ..base import Solver


class IDSSolver(Solver):
    def _search(self, max_depth: int, timeout: float, profile_memory: bool):
        """
        Internal search function containing the core IDS logic.
        """
        nodes_expanded_this_run = 0
        solution_path = None
        timed_out = False

        if profile_memory:
            tracemalloc.start()
            tracemalloc.clear_traces()

        start_time = time.time()

        # outer loop calling DLS
        for depth_limit in range(max_depth + 1):

            # if timeout is reached
            if time.time() - start_time > timeout:
                timed_out = True
                print("Timeout reached before finding a solution.")
                break

            visited_at_depth = {repr(self.board)}
            stack = [(self.board, [], 0)]

            # performing DLS
            while stack:

                if nodes_expanded_this_run % 1000 == 0:
                    if time.time() - start_time > timeout:
                        timed_out = True
                        break 

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
                    if new_board_repr not in visited_at_depth:
                        visited_at_depth.add(new_board_repr)
                        stack.append((new_board, path + [move], depth + 1))

            # if a solution was found or timeout occurred, break the outer loop
            if solution_path is not None or timed_out:
                break

        search_time = time.time() - start_time

        peak_memory_kb = 0.0
        if profile_memory:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_memory_kb = peak / 1024

        if timed_out:
            solution_path = None

        return solution_path, search_time, peak_memory_kb, nodes_expanded_this_run

    def solve(self, max_depth: int = 500, timeout: float = 60.0):
        """
        Solves the puzzle using IDS with a specified maximum depth and timeout.
        """
        # this run measure search time
        # default timeout to 60
        solution, search_time, _, nodes_expanded = self._search(
            max_depth, timeout, profile_memory=False
        )

        self.solution = solution
        self.search_time = search_time
        self.nodes_expanded = nodes_expanded
        self.memory_usage = 0.0

        # this run measure memory usage
        # this second run might also time out. The memory usage will be
        # the peak usage up to that point.
        _, _, peak_memory, _ = self._search(max_depth, timeout, profile_memory=True)
        self.memory_usage = peak_memory

        return self.solution
