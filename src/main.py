from board import Board
from vehicle import Vehicle
from move import Move
from solver import UCSSolver

def main():
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
    print("-" * 20)

    # --- Solve with UCS ---
    print("Solving with Uniform-Cost Search (UCS)...")
    ucs_solver = UCSSolver(board)
    solution = ucs_solver.solve()
    stats = ucs_solver.get_stats()

    if solution:
        print("\nSolution found!")
        print(f"Path: {solution}")
        
        # To visualize the solution, we can apply the moves
        final_board = board.apply_moves(solution)
        print("\nFinal Board State:")
        print(final_board)

    else:
        print("\nNo solution found.")

    print("\n--- UCS Solver Stats ---")
    print(f"Search Time: {stats['search_time']:.4f} seconds")
    print(f"Memory Usage: {stats['memory_usage']:.2f} KB")
    print(f"Nodes Expanded: {stats['nodes_expanded']}")
    print("-" * 20)

if __name__ == "__main__":
    main()
