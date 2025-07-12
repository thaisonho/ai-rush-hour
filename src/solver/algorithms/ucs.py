import time
import heapq
import tracemalloc

from ..base import Solver


class UCSSolver(Solver):
    def _search(self, profile_memory: bool):
        """Internal search function containing the core UCS logic."""
        nodes_expanded_this_run = 0

        if profile_memory:
            tracemalloc.start()
            tracemalloc.clear_traces()

        start_time = time.time()

        # vehicle mapping for quick access
        vehicle_map = {v.id: v for v in self.board.vehicles}
        initial_board_repr = repr(self.board)
        counter = 0
        frontier = [(0, counter, self.board)]  # (cost, counter, board)

        came_from = {initial_board_repr: (None, None)}
        total_cost = {initial_board_repr: 0}

        solution_path = None

        while frontier:
            cost, _, current_board = heapq.heappop(frontier)
            current_board_repr = repr(current_board)

            if cost > total_cost[current_board_repr]:
                continue

            nodes_expanded_this_run += 1

            if current_board.is_solved():
                solution_path = self._path_construct(came_from, current_board_repr)
                break

            for move in current_board.get_possible_moves():
                new_board = current_board.apply_move(move)
                board_repr = repr(new_board)

                moved_vehicle = vehicle_map.get(move.vehicle_id)
                if moved_vehicle is None:
                    continue

                new_cost = cost + (moved_vehicle.length * abs(move.amount))

                if board_repr not in total_cost or new_cost < total_cost[board_repr]:
                    total_cost[board_repr] = new_cost
                    came_from[board_repr] = (current_board_repr, move)
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, new_board))

        search_time = time.time() - start_time

        peak_memory_kb = 0.0
        if profile_memory:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_memory_kb = peak / 1024

        return solution_path, search_time, peak_memory_kb, nodes_expanded_this_run

    def solve(self):
        # this run measure search time
        solution, search_time, _, nodes_expanded = self._search(profile_memory=False)

        self.solution = solution
        self.search_time = search_time
        self.nodes_expanded = nodes_expanded
        self.memory_usage = 0.0

        # this run measure memory usage
        _, _, peak_memory, _ = self._search(profile_memory=True)
        self.memory_usage = peak_memory

        return self.solution

    def _path_construct(self, came_from: dict, current_board_repr: str):
        path = []
        while current_board_repr is not None:
            parent_repr, move = came_from.get(current_board_repr)
            if move:
                path.append(move)
            current_board_repr = parent_repr
        return path[::-1]
