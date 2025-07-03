import time
import heapq
import resource

from ..base import Solver


class UCSSolver(Solver):
    def solve(self):
        self.nodes_expanded = 0
        self.solution = None
        self.memory_usage = 0
        start_time = time.time()
        initial_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        initial_board_repr = repr(self.board)
        # Priority queue: (cost, counter, board)
        # A counter is used to break ties in the priority queue
        counter = 0
        frontier = [(0, counter, self.board)]
        heapq.heapify(frontier)

        # came_from dict to track parent pointers and moves
        # the store value is a tuple of (repr(parent_board), move)
        came_from = {initial_board_repr: (None, None)}
        total_cost = {initial_board_repr: 0}

        while frontier:
            cost, _, current_board = heapq.heappop(frontier)
            current_board_repr = repr(current_board)

            if cost > total_cost[current_board_repr]:
                continue

            self.nodes_expanded += 1

            if current_board.is_solved():
                self.solution = self._path_construct(came_from, current_board_repr)
                self.search_time = time.time() - start_time
                final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                self.memory_usage = (final_memory - initial_memory) / 1024  # in KB
                return self.solution

            for move in current_board.get_possible_moves():
                new_board = current_board.apply_move(move)
                board_repr = repr(new_board)

                moved_vehicle = None
                for vehicle in current_board.vehicles:
                    if vehicle.id == move.vehicle_id:
                        moved_vehicle = vehicle
                        break

                if moved_vehicle is None:
                    raise ValueError(f"No vehicle found with id {move.vehicle_id} in current_board.vehicles")

                new_cost = cost + moved_vehicle.length
                
                if board_repr not in total_cost or new_cost < total_cost[board_repr]:
                    total_cost[board_repr] = new_cost
                    came_from[board_repr] = (current_board_repr, move)
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, new_board))

        # If no solution is found
        self.search_time = time.time() - start_time
        final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.memory_usage = (final_memory - initial_memory) / 1024  # in KB
        self.solution = None
        return None

    # helper function to construct the path
    def _path_construct(self, came_from: dict, current_board_repr: str):
        path = []
        while current_board_repr is not None:
            parent_repr, move = came_from.get(current_board_repr)
            if move:
                path.append(move)
            current_board_repr = parent_repr
        # current path is in reverse form end -> start
        # so we reverse it to start -> end
        return path[::-1]  
