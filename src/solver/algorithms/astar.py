import time
import heapq
import resource

from ..base import Solver
from board import Board
from move import Move


class AStarSolver(Solver):
    """
    - The cost of a move, g(n), is the length of the vehicle being moved.
    - The heuristic, h(n), is the sum of the lengths of vehicles blocking the exit path.
    """

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
        
        # Sum the lengths of the unique blocking vehicles.
        h_cost = sum(vehicle_map[vid] for vid in blocking_vehicle_ids)
        return h_cost

    def solve(self):
        self.nodes_expanded = 0
        self.solution = None
        self.memory_usage = 0
        start_time = time.time()
        initial_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        initial_board = self.board
        initial_board_repr = repr(initial_board)
        vehicle_map = self._get_vehicle_map(initial_board)

        # Priority queue: (f_cost, g_cost, counter, board)
        counter = 0
        h_cost = self._heuristic(initial_board, vehicle_map)
        frontier = [(h_cost, 0, counter, initial_board)]
        heapq.heapify(frontier)

        came_from = {initial_board_repr: (None, None)}
        g_cost_so_far = {initial_board_repr: 0}

        while frontier:
            _, g_cost, _, current_board = heapq.heappop(frontier)
            current_board_repr = repr(current_board)

            if g_cost > g_cost_so_far[current_board_repr]:
                continue

            self.nodes_expanded += 1

            if current_board.is_solved():
                self.solution = self._path_construct(came_from, current_board_repr)
                self.search_time = time.time() - start_time
                final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                self.memory_usage = (final_memory - initial_memory) / 1024  
                return self.solution

            # We need a map for the current board's vehicles for quick length lookups.
            current_vehicle_map = self._get_vehicle_map(current_board)

            for move in current_board.get_possible_moves():
                # The cost of this move is the length of the vehicle being moved.
                move_cost = current_vehicle_map[move.vehicle_id]
                new_g_cost = g_cost + move_cost
                
                new_board = current_board.apply_move(move)
                new_board_repr = repr(new_board)
                
                if new_board_repr not in g_cost_so_far or new_g_cost < g_cost_so_far[new_board_repr]:
                    g_cost_so_far[new_board_repr] = new_g_cost
                    came_from[new_board_repr] = (current_board_repr, move)
                    
                    # Calculate the new f_cost using the weighted g_cost and new heuristic.
                    h_cost = self._heuristic(new_board, vehicle_map)
                    f_cost = new_g_cost + h_cost
                    
                    counter += 1
                    heapq.heappush(frontier, (f_cost, new_g_cost, counter, new_board))

        # If no solution is found
        self.search_time = time.time() - start_time
        final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.memory_usage = (final_memory - initial_memory) / 1024  # in KB
        self.solution = None
        return None

    def _path_construct(self, came_from: dict, current_board_repr: str):
        path = []
        while current_board_repr is not None:
            parent_repr, move = came_from.get(current_board_repr)
            if move:
                path.append(move)
            current_board_repr = parent_repr
        # The path is constructed backward, so we reverse it to get start -> end.
        return path[::-1]