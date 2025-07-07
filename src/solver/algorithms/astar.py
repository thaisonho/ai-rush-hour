import time
import heapq
import psutil  
import os      

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
        """
        The heuristic value is calculated base on the total length of blocking vehicles.
        """
        red_car = board.vehicles[0]
        if board.is_solved():
            return 0

        blocking_vehicle_ids = set()
        grid = board._get_grid()

        for x in range(red_car.x + red_car.length, board.width):
            cell_content = grid[red_car.y][x]
            if cell_content != '.':
                blocking_vehicle_ids.add(cell_content)
        
        h_cost = sum(vehicle_map[vid] for vid in blocking_vehicle_ids)
        return h_cost

    def solve(self):
        self.nodes_expanded = 0
        self.solution = None
        self.memory_usage = 0
        
        process = psutil.Process(os.getpid()) 
        start_time = time.time()
        initial_memory = process.memory_info().rss 
        peak_memory = initial_memory 

        initial_board = self.board
        initial_board_repr = repr(initial_board)
        vehicle_map = self._get_vehicle_map(initial_board)

        # The frontier is a priority queue (min-heap) of states to visit.
        # Each item is a tuple: (f_cost, g_cost, counter, board_state).
        # f_cost = g_cost + h_cost (total estimated cost)
        # g_cost = cost from the start node
        # counter = a tie-breaker to ensure FIFO behavior for states with the same f_cost.
        counter = 0
        h_cost = self._heuristic(initial_board, vehicle_map)
        frontier = [(h_cost, 0, counter, initial_board)]
        heapq.heapify(frontier)

        # came_from is a dictionary that maps each board state to its parent state and the move taken to reach it. 
        # Key: board representation, Value: (parent board representation, move to get here).        
        came_from = {initial_board_repr: (None, None)}

        # g_cost_so_far keeps track of the lowest cost to reach each board state.
        g_cost_so_far = {initial_board_repr: 0}

        while frontier:
            current_memory = process.memory_info().rss 
            if current_memory > peak_memory:            
                peak_memory = current_memory            

            _, g_cost, _, current_board = heapq.heappop(frontier)
            current_board_repr = repr(current_board)

            if g_cost > g_cost_so_far[current_board_repr]:
                continue

            self.nodes_expanded += 1

            if current_board.is_solved():
                self.solution = self._path_construct(came_from, current_board_repr)
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

        self.search_time = time.time() - start_time
        final_memory = process.memory_info().rss 
        if final_memory > peak_memory:          
            peak_memory = final_memory          
        self.memory_usage = (peak_memory - initial_memory) / 1024  
        
        return self.solution

    def _path_construct(self, came_from: dict, current_board_repr: str):
        path = []
        while current_board_repr is not None:
            parent_repr, move = came_from.get(current_board_repr)
            if move:
                path.append(move)
            current_board_repr = parent_repr
        return path[::-1]