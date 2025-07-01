from board import Board
from vehicle import Vehicle
from move import Move

def main():
    # The first vehicle (for now) is always the red car
    vehicles = [
        Vehicle('R', 1, 2, 2, 'H'),
        Vehicle('A', 0, 0, 2, 'V'),
        Vehicle('B', 0, 4, 2, 'H'),
        Vehicle('C', 3, 0, 3, 'V'),
        Vehicle('D', 4, 3, 2, 'H'),
    ]

    # Create the game board
    board = Board(6, 6, vehicles)

    # Print the initial state of the board
    print("Initial Board:")
    print(board)

    # Check if the puzzle is solved
    print(f"\nIs solved? {board.is_solved()}")

    # Get and print possible moves
    possible_moves = board.get_possible_moves()
    print("\nPossible moves:")
    for move in possible_moves:
        print(move)

    # Apply the first possible move and print the new board
    if possible_moves:
        print("\nApplying the first possible move...")
        new_board = board.apply_move(possible_moves[0])
        print("\nNew Board State:")
        print(new_board)
    else:
        print("\nNo possible moves found.")

if __name__ == "__main__":
    main()
