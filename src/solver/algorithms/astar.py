import time
import heapq
import tracemalloc

from ..base import Solver
from board import Board
from move import Move

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
        vehicle_map = self._get_vehicle_map(initial_board)

        counter = 0
        h_cost = self._heuristic(initial_board, vehicle_map)
        frontier = [(h_cost, 0, counter, initial_board)] # (f_cost, g_cost, counter, board)
        
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
                
                if new_board_repr not in g_cost_so_far or new_g_cost < g_cost_so_far[new_board_repr]:
                    g_cost_so_far[new_board_repr] = new_g_cost
                    came_from[new_board_repr] = (current_board_repr, move)
                    
                    h_cost = self._heuristic(new_board, vehicle_map)
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

    def _heuristic(self, board: Board, vehicle_map: dict[str, int]) -> int:
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

    def _path_construct(self, came_from: dict, current_board_repr: str):
        path = []
        while current_board_repr is not None:
            parent_repr, move = came_from.get(current_board_repr)
            if move:
                path.append(move)
            current_board_repr = parent_repr
        return path[::-1]