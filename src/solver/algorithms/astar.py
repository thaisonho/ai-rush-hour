from collections import deque
import time
import heapq
import tracemalloc

from ..base import Solver
from board import Board


class AStarSolver(Solver):
    def _search(self, profile_memory: bool):
        """Internal search function containing the core A* logic."""
        nodes_expanded_this_run = 0

        if profile_memory:
            tracemalloc.start()
            tracemalloc.clear_traces()

        start_time = time.time()

        initial_board = self.board
        initial_board_repr = repr(initial_board)

        counter = 0
        h_cost = self._heuristic(initial_board)
        frontier = [
            (h_cost, 0, counter, initial_board)
        ]  # (f_cost, g_cost, counter, board)

        came_from = {initial_board_repr: (None, None)}
        g_cost_so_far = {initial_board_repr: 0}

        solution_path = None

        while frontier:
            _, g_cost, _, current_board = heapq.heappop(frontier)
            current_board_repr = repr(current_board)

            if g_cost > g_cost_so_far[current_board_repr]:
                continue

            nodes_expanded_this_run += 1

            if current_board.is_solved():
                solution_path = self._path_construct(came_from, current_board_repr)
                break

            current_vehicle_map = self._get_vehicle_map(current_board)

            for move in current_board.get_possible_moves():
                move_cost = current_vehicle_map[move.vehicle_id] * abs(move.amount)
                new_g_cost = g_cost + move_cost

                new_board = current_board.apply_move(move)
                new_board_repr = repr(new_board)

                if (
                    new_board_repr not in g_cost_so_far
                    or new_g_cost < g_cost_so_far[new_board_repr]
                ):
                    g_cost_so_far[new_board_repr] = new_g_cost
                    came_from[new_board_repr] = (current_board_repr, move)

                    h_cost = self._heuristic(new_board)
                    f_cost = new_g_cost + h_cost

                    counter += 1
                    heapq.heappush(frontier, (f_cost, new_g_cost, counter, new_board))

        search_time = time.time() - start_time

        peak_memory_kb = 0.0
        if profile_memory:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_memory_kb = peak / 1024

        return solution_path, search_time, peak_memory_kb, nodes_expanded_this_run

    def solve(self):
        # --- Run 1: The "clean" run for accurate Time and Nodes Expanded stats ---
        solution, search_time, _, nodes_expanded = self._search(profile_memory=False)

        self.solution = solution
        self.search_time = search_time
        self.nodes_expanded = nodes_expanded
        self.memory_usage = 0.0

        # --- Run 2: The "profiled" run ---
        _, _, peak_memory, _ = self._search(profile_memory=True)
        self.memory_usage = peak_memory

        return self.solution

    def _get_vehicle_map(self, board: Board) -> dict[str, int]:
        return {vehicle.id: vehicle.length for vehicle in board.vehicles}

    """""
    def _heuristic(self, board: Board, vehicle_map: dict[str, int]) -> int:
        """ """
            Heuristic: "Blocking Vehicles".
        """ """
        red_car = board.vehicles[0]
        if board.is_solved():
            return 0
        blocking_vehicle_ids = set()
        grid = board._get_grid()
        for x in range(red_car.x + red_car.length, board.width):
            cell_content = grid[red_car.y][x]
            if cell_content != '.':
                blocking_vehicle_ids.add(cell_content)
        return sum(vehicle_map[vid] for vid in blocking_vehicle_ids)
    """

    def _heuristic(self, board: Board,) -> int:
        """
        Heuristic: "Recursive Minimal Clearing Cost".
        This heuristic estimates the total minimum cost to clear a path for the red car.
        It works by recursively finding all vehicles blocking the path and summing up
        the minimum cost required to move them, assuming each move is only 1 unit.
        This heuristic is designed to be admissible and consistent (maybe?).
        """
        red_car = board.vehicles[0]
        if board.is_solved():
            return 0

        # Create a new map from vehicle ID to the vehicle object for quick access.
        vehicle_map = {v.id: v for v in board.vehicles}

        grid = board._get_grid()
        total_clearing_cost = 0

        # The queue will store tuples of (vehicle_id_to_clear, id_of_vehicle_it_blocks).
        # This helps in determining the required direction of movement.
        clearing_queue = deque()

        # A set to ensure that the cost of moving each vehicle is counted only once,
        # even if it blocks multiple paths.
        processed_vehicles = set()

        # Step 1: Find all vehicles that are directly blocking the red car's path to the exit.
        for x in range(red_car.x + red_car.length, board.width):
            cell_content = grid[red_car.y][x]
            if cell_content != "." and cell_content not in processed_vehicles:
                # This vehicle is blocking the red car ('R').
                clearing_queue.append((cell_content, "R"))
                processed_vehicles.add(cell_content)

        # Step 2: Main loop to process the dependency chain of blocking vehicles.
        # This is an iterative implementation of a recursive analysis.
        while clearing_queue:
            vehicle_id, _ = clearing_queue.popleft()

            # Access the vehicle object using the map created earlier.
            vehicle_to_clear = vehicle_map.get(vehicle_id)
            if not vehicle_to_clear:
                continue

            # Step 2a: Add the minimum cost of moving this blocking vehicle to the total.
            # The minimum cost is its length (assuming a move of amount=1).
            total_clearing_cost += vehicle_to_clear.length

            # Step 2b: Analyze which new vehicles are blocking the `vehicle_to_clear`.
            if vehicle_to_clear.orientation == "H":
                # A horizontal vehicle is blocking another vehicle.
                # This logic is necessary if a horizontal vehicle blocks a vertical one in the chain.
                # For simplicity, we can focus on the primary case (vertical blocking horizontal).
                pass
            else:  # 'V' - A vertical vehicle is blocking a horizontal one.
                # It needs to move either up or down to clear the path.

                # Check for space and blockers in the 'up' direction.
                can_move_up = vehicle_to_clear.y > 0
                new_blockers_up = set()
                if can_move_up:
                    up_cell_content = grid[vehicle_to_clear.y - 1][vehicle_to_clear.x]
                    if up_cell_content != ".":
                        can_move_up = False
                        new_blockers_up.add(up_cell_content)

                # Check for space and blockers in the 'down' direction.
                can_move_down = (
                    vehicle_to_clear.y + vehicle_to_clear.length < board.height
                )
                new_blockers_down = set()
                if can_move_down:
                    down_cell_content = grid[
                        vehicle_to_clear.y + vehicle_to_clear.length
                    ][vehicle_to_clear.x]
                    if down_cell_content != ".":
                        can_move_down = False
                        new_blockers_down.add(down_cell_content)

                # If a vehicle is trapped from both ends, it's a dead-end state.
                # Returning infinity prunes this branch of the search tree immediately.
                if not can_move_up and not can_move_down:
                    return float("inf")

                # A "heuristic within the heuristic": to get a tighter estimate,
                # we assume the vehicle will be moved in the direction that is "easier"
                # to clear (i.e., has fewer new blockers).
                final_blockers = set()
                if can_move_up and can_move_down:
                    final_blockers = (
                        new_blockers_up
                        if len(new_blockers_up) < len(new_blockers_down)
                        else new_blockers_down
                    )
                elif can_move_up:
                    final_blockers = new_blockers_up
                elif can_move_down:
                    final_blockers = new_blockers_down

                # Add the newly found blockers to the queue to be processed.
                for blocker_id in final_blockers:
                    if blocker_id not in processed_vehicles:
                        clearing_queue.append((blocker_id, vehicle_id))
                        processed_vehicles.add(blocker_id)

        # Step 3: Add the cost of moving the red car itself to the exit.
        # This is the Manhattan distance cost, assuming a clear path.
        distance_to_goal = board.width - (red_car.x + red_car.length)
        if distance_to_goal > 0:
            total_clearing_cost += red_car.length * distance_to_goal

        return total_clearing_cost

    def _path_construct(self, came_from: dict, current_board_repr: str):
        path = []
        while current_board_repr is not None:
            parent_repr, move = came_from.get(current_board_repr)
            if move:
                path.append(move)
            current_board_repr = parent_repr
        return path[::-1]
