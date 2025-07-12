import argparse
from board import Board
from vehicle import Vehicle
from solver import UCSSolver, BFSSolver, DFSSolver, IDSSolver, AStarSolver

def parse_map(map_file):
    vehicles = []
    with open(map_file, 'r') as f:
        lines = f.readlines()
        grid_size = tuple(map(int, lines[0].strip().split(',')))
        for line in lines[1:]:
            parts = line.strip().split(',')
            id, x, y, length, orientation = parts
            vehicles.append(Vehicle(id, int(x), int(y), int(length), orientation))
    return grid_size, vehicles

def main():
    parser = argparse.ArgumentParser(description="Solve the Rush Hour puzzle.")
    parser.add_argument("map_file", help="Path to the map file.")
    args = parser.parse_args()

    grid_size, vehicles = parse_map(args.map_file)
    
    # Create the game board
    board = Board(grid_size[0], grid_size[1], vehicles)

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
    
    
if __name__ == "__main__":
    main()
