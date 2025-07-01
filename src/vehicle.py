class Vehicle:
    def __init__(self, id, x, y, length, orientation):
        if not isinstance(id, str):
            raise TypeError("ID must be a string.")
        self.id = id

        if not isinstance(x, int) or x < 0:
            raise ValueError("x-coordinate must be a non-negative integer.")
        self.x = x

        if not isinstance(y, int) or y < 0:
            raise ValueError("y-coordinate must be a non-negative integer.")
        self.y = y

        if not isinstance(length, int) or length <= 0:
            raise ValueError("Length must be a positive integer.")
        self.length = length

        if orientation not in ['H', 'V']:
            raise ValueError("Orientation must be 'H' or 'V'.")
        self.orientation = orientation

    def __repr__(self):
        return f"Vehicle({self.id}, x={self.x}, y={self.y}, len={self.length}, orient={self.orientation})"
