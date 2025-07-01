class Move:
    def __init__(self, vehicle_id, amount):
        if not isinstance(vehicle_id, str):
            raise TypeError("Vehicle ID must be a string.")
        self.vehicle_id = vehicle_id

        if not isinstance(amount, int) or amount == 0:
            raise ValueError("Amount must be a non-zero integer.")
        self.amount = amount

    def __repr__(self):
        return f"Move(vehicle_id='{self.vehicle_id}', amount={self.amount})"
