from board import Board
from vehicle import Vehicle
from solver import UCSSolver, BFSSolver, DFSSolver, IDSSolver, AStarSolver

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

     # --- Solve with DFS ---
    print("Solving with Depth-First Search (DFS)...")
    dfs_solver = DFSSolver(board)
    solution = dfs_solver.solve()
    stats = dfs_solver.get_stats()

    if solution:
        print("\nSolution found!")
        print(f"Path: {solution}")
        
        # To visualize the solution, we can apply the moves
        final_board = board.apply_moves(solution)
        print("\nFinal Board State:")
        print(final_board)

    else:
        print("\nNo solution found.")

    print("\n--- DFS Solver Stats ---")
    print(f"Search Time: {stats['search_time']:.4f} seconds")
    print(f"Memory Usage: {stats['memory_usage']:.2f} KB")
    print(f"Nodes Expanded: {stats['nodes_expanded']}")
    print("-" * 20)

    # --- Solve with IDS ---
    print("Solving with Iterative Deepening Search (IDS)...")
    ids_solver = IDSSolver(board)
    solution = ids_solver.solve()
    stats = ids_solver.get_stats()

    if solution:
        print("\nSolution found!")
        print(f"Path: {solution}")
        
        # To visualize the solution, we can apply the moves
        final_board = board.apply_moves(solution)
        print("\nFinal Board State:")
        print(final_board)

    else:
        print("\nNo solution found.")

    print("\n--- IDS Solver Stats ---")
    print(f"Search Time: {stats['search_time']:.4f} seconds")
    print(f"Memory Usage: {stats['memory_usage']:.2f} KB")
    print(f"Nodes Expanded: {stats['nodes_expanded']}")
    print("-" * 20)

    # --- Solve with BFS ---
    print("Solving with BFS Search ...")
    bfs_solver = BFSSolver(board)
    solution = bfs_solver.solve()
    stats = bfs_solver.get_stats()

    if solution:
        print("\nSolution found!")
        print(f"Path: {solution}")
        
        # To visualize the solution, we can apply the moves
        final_board = board.apply_moves(solution)
        print("\nFinal Board State:")
        print(final_board)

    else:
        print("\nNo solution found.")

    print("\n--- BFS Solver Stats ---")
    print(f"Search Time: {stats['search_time']:.4f} seconds")
    print(f"Memory Usage: {stats['memory_usage']:.2f} KB")
    print(f"Nodes Expanded: {stats['nodes_expanded']}")
    print("-" * 20)

    # --- Solve with A* ---
    print("Solving with A* Search ...")
    a_star_solver = AStarSolver(board)
    solution = a_star_solver.solve()
    stats = a_star_solver.get_stats()

    if solution:
        print("\nSolution found!")
        print(f"Path: {solution}")
        
        # To visualize the solution, we can apply the moves
        final_board = board.apply_moves(solution)
        print("\nFinal Board State:")
        print(final_board)

    else:
        print("\nNo solution found.")

    print("\n--- A* Solver Stats ---")
    print(f"Search Time: {stats['search_time']:.4f} seconds")
    print(f"Memory Usage: {stats['memory_usage']:.2f} KB")
    print(f"Nodes Expanded: {stats['nodes_expanded']}")
    print("-" * 20)

if __name__ == "__main__":
    main()
