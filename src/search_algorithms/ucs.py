import time
import heapq
import resource

from solver import Solver


class UCSSolver(Solver):
    def solve(self):
        self.nodes_expanded = 0
        self.solution = None
        self.memory_usage = 0
        start_time = time.time()
        initial_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Priority queue: (cost, counter, path, board)
        # A counter is used to break ties in the priority queue
        counter = 0
        frontier = [(0, counter, [], self.board)]
        heapq.heapify(frontier)

        # Visited set to store board states
        visited = {repr(self.board)}

        while frontier:
            cost, _, path, current_board = heapq.heappop(frontier)

            self.nodes_expanded += 1

            if current_board.is_solved():
                self.solution = path
                self.search_time = time.time() - start_time
                final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                self.memory_usage = (final_memory - initial_memory) / 1024  # in KB
                return path

            for move in current_board.get_possible_moves():
                new_board = current_board.apply_move(move)
                board_repr = repr(new_board)

                if board_repr not in visited:
                    moved_vehicle = None
                    for vehicle in current_board.vehicles:
                        if vehicle.id == move.vehicle_id:
                            moved_vehicle = vehicle
                            break

                    if moved_vehicle is None:
                        raise ValueError(f"No vehicle found with id {move.vehicle_id} in current_board.vehicles")

                    new_cost = cost + moved_vehicle.length
                    new_path = path + [move]
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, new_path, new_board))
                    visited.add(board_repr)
        # If no solution is found
        self.search_time = time.time() - start_time
        final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.memory_usage = (final_memory - initial_memory) / 1024  # in KB
        self.solution = None
        return None
