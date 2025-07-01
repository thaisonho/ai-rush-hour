from vehicle import Vehicle
from move import Move
import copy

class Board:
    def __init__(self, width, height, vehicles):
        if not isinstance(width, int) or width <= 0:
            raise ValueError("Width must be a positive integer.")
        self.width = width

        if not isinstance(height, int) or height <= 0:
            raise ValueError("Height must be a positive integer.")
        self.height = height

        if not isinstance(vehicles, list) or not all(isinstance(v, Vehicle) for v in vehicles):
            raise TypeError("Vehicles must be a list of Vehicle objects.")
        self.vehicles = vehicles

        self._validate_vehicles()

    def _validate_vehicles(self):
        grid = [['.' for _ in range(self.width)] for _ in range(self.height)]
        for v in self.vehicles:
            # Check if vehicle is within board boundaries
            if v.orientation == 'H':
                if v.x < 0 or v.x + v.length > self.width or v.y < 0 or v.y >= self.height:
                    raise ValueError(f"Vehicle {v.id} is out of bounds.")
            else:  # 'V'
                if v.x < 0 or v.x >= self.width or v.y < 0 or v.y + v.length > self.height:
                    raise ValueError(f"Vehicle {v.id} is out of bounds.")

            # Check for vehicle collisions
            for i in range(v.length):
                if v.orientation == 'H':
                    if grid[v.y][v.x + i] != '.':
                        raise ValueError(f"Vehicle collision at ({v.x + i}, {v.y})")
                    grid[v.y][v.x + i] = v.id
                else:  # 'V'
                    if grid[v.y + i][v.x] != '.':
                        raise ValueError(f"Vehicle collision at ({v.x}, {v.y + i})")
                    grid[v.y + i][v.x] = v.id

    def is_solved(self):
        # check for the winning codition
        # e.g., the red car must be at the right edge of the board
        red_car = self.vehicles[0]
        return red_car.x + red_car.length >= self.width

    def get_possible_moves(self):
        moves = []
        grid = self._get_grid()

        for vehicle in self.vehicles:
            if vehicle.orientation == 'H':
                # Move right
                for i in range(1, self.width):
                    if vehicle.x + vehicle.length + i - 1 < self.width and grid[vehicle.y][vehicle.x + vehicle.length + i - 1] == '.':
                        moves.append(Move(vehicle.id, i))
                    else:
                        break
                # Move left
                for i in range(1, self.width):
                    if vehicle.x - i >= 0 and grid[vehicle.y][vehicle.x - i] == '.':
                        moves.append(Move(vehicle.id, -i))
                    else:
                        break
            else:  # 'V'
                # Move down
                for i in range(1, self.height):
                    if vehicle.y + vehicle.length + i - 1 < self.height and grid[vehicle.y + vehicle.length + i - 1][vehicle.x] == '.':
                        moves.append(Move(vehicle.id, i))
                    else:
                        break
                # Move up
                for i in range(1, self.height):
                    if vehicle.y - i >= 0 and grid[vehicle.y - i][vehicle.x] == '.':
                        moves.append(Move(vehicle.id, -i))
                    else:
                        break
        return moves

    def apply_move(self, move: Move):
        # deep copying the vehicles.
        new_vehicles = copy.deepcopy(self.vehicles)
        for vehicle in new_vehicles:
            if vehicle.id == move.vehicle_id:
                if vehicle.orientation == 'H':
                    vehicle.x += move.amount
                else:
                    vehicle.y += move.amount
                break
        return Board(self.width, self.height, new_vehicles)

    def apply_moves(self, moves: list[Move]):
        board = self
        for move in moves:
            board = board.apply_move(move)
        return board

    def _get_grid(self):
        grid = [['.' for _ in range(self.width)] for _ in range(self.height)]
        for vehicle in self.vehicles:
            if vehicle.orientation == 'H':
                for i in range(vehicle.length):
                    grid[vehicle.y][vehicle.x + i] = vehicle.id
            else:  # 'V'
                for i in range(vehicle.length):
                    grid[vehicle.y + i][vehicle.x] = vehicle.id
        return grid

    def __repr__(self):
        # dots represent empty spaces, vehicle IDs represent occupied spaces
        grid = self._get_grid()
        return '\n'.join([''.join(row) for row in grid])
