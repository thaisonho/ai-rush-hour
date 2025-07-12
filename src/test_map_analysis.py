import os
import sys
import time
import tracemalloc
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

# Add the src directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from board import Board
from vehicle import Vehicle
from solver import UCSSolver, BFSSolver, DFSSolver, IDSSolver, AStarSolver

class ExperimentRunner:
    def __init__(self, map_directory='map', results_directory='experiment_results', selected_maps=None):
        # Get the script's directory
        script_dir = Path(__file__).parent
        
        # Set paths relative to script directory
        self.map_directory = script_dir / map_directory
        self.base_results_directory = script_dir / results_directory
        self.base_results_directory.mkdir(exist_ok=True)
        
        # Create run-specific directory
        self.results_directory = self._create_run_directory()
        
        # Algorithm configurations
        self.algorithms = {
            'BFS': BFSSolver,
            'UCS': UCSSolver,
            'DFS': DFSSolver,
            'IDS': IDSSolver,
            'A*': AStarSolver
        }
        
        # Experiment configuration
        self.max_time = 300  # 5 minutes timeout per algorithm
        self.results = []
        
        # Map selection - if None, run all maps except excluded ones
        self.selected_maps = selected_maps  # List of map names (e.g., ['map01', 'map02']) or None for all
        
    def _create_run_directory(self):
        """Create a new run directory (run1, run2, run3, etc.)"""
        run_counter = 1
        while True:
            run_dir = self.base_results_directory / f"run{run_counter}"
            if not run_dir.exists():
                run_dir.mkdir(exist_ok=True)
                print(f"Created results directory: {run_dir}")
                return run_dir
            run_counter += 1
        
    def load_map(self, map_file):
        """Load a map file and return board configuration"""
        vehicles = []
        
        # Read the map file and extract vehicles
        with open(map_file, 'r') as f:
            content = f.read()
            
        # Execute the content to get vehicles list
        local_vars = {'Vehicle': Vehicle}
        exec(content, {}, local_vars)
        vehicles = local_vars['vehicles']
        
        # Create board (assuming 6x6 grid for Rush Hour)
        board = Board(6, 6, vehicles)
        return board
    
    def run_algorithm(self, algorithm_name, algorithm_class, board):
        """Run a single algorithm and return performance metrics"""
        print(f"  Running {algorithm_name}...")
        
        try:
            # Initialize solver
            solver = algorithm_class(board)
            
            # Start timing and memory tracking
            start_time = time.time()
            tracemalloc.start()
            
            # Run the algorithm with timeout handling
            if algorithm_name == 'IDS':
                solution = solver.solve(max_depth=50, timeout=self.max_time)
            elif algorithm_name == 'DFS':
                solution = solver.solve(depth_limit=50)
            else:
                solution = solver.solve()
                
            # Get stats
            stats = solver.get_stats()
            
            # Stop memory tracking
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Calculate actual runtime
            actual_time = time.time() - start_time
            
            return {
                'algorithm': algorithm_name,
                'solution_found': solution is not None,
                'solution_length': len(solution) if solution else None,
                'search_time': stats['search_time'],
                'actual_time': actual_time,
                'memory_usage': stats['memory_usage'],
                'peak_memory': peak / 1024,  # Convert to KB
                'nodes_expanded': stats['nodes_expanded'],
                'success': True,
                'error': None
            }
            
        except Exception as e:
            print(f"    Error in {algorithm_name}: {str(e)}")
            return {
                'algorithm': algorithm_name,
                'solution_found': False,
                'solution_length': None,
                'search_time': float('inf'),
                'actual_time': float('inf'),
                'memory_usage': float('inf'),
                'peak_memory': float('inf'),
                'nodes_expanded': float('inf'),
                'success': False,
                'error': str(e)
            }
    
    def run_experiments(self):
        """Run experiments on selected maps"""
        print("Starting experiments...")
        
        # Get all available map files
        all_map_files = sorted([f for f in self.map_directory.glob('*.txt') 
                               if f.name.startswith('map') and f.name != 'map-descriptions.txt'])
        
        # Filter maps based on selection
        if self.selected_maps is not None:
            # Only run selected maps
            map_files = []
            for map_name in self.selected_maps:
                # Handle both 'map01' and 'map01.txt' formats
                if not map_name.endswith('.txt'):
                    map_name_with_ext = map_name + '.txt'
                else:
                    map_name_with_ext = map_name
                    
                map_path = self.map_directory / map_name_with_ext
                if map_path.exists():
                    map_files.append(map_path)
                else:
                    print(f"Warning: Map '{map_name}' not found, skipping...")
            
            print(f"Selected maps: {[f.stem for f in map_files]}")
        else:
            # Run all maps (default behavior)
            map_files = all_map_files
            print(f"Running all available maps")
        
        if not map_files:
            print("No valid map files found!")
            return
        
        print(f"Found {len(map_files)} map files to process")
        
        # Run experiments for each map
        for map_file in map_files:
            map_name = map_file.stem
            print(f"\nProcessing {map_name}...")
            
            try:
                # Load the map
                board = self.load_map(map_file)
                print(f"  Board loaded: {board.width}x{board.height} with {len(board.vehicles)} vehicles")
                
                # Test each algorithm
                for alg_name, alg_class in self.algorithms.items():
                    result = self.run_algorithm(alg_name, alg_class, board)
                    result['map'] = map_name
                    result['map_file'] = str(map_file)
                    result['timestamp'] = datetime.now().isoformat()
                    
                    self.results.append(result)
                    
                    # Print quick summary
                    if result['success'] and result['solution_found']:
                        print(f"    ✓ {alg_name}: {result['solution_length']} moves, "
                              f"{result['search_time']:.3f}s, {result['nodes_expanded']} nodes")
                    elif result['success']:
                        print(f"    ✗ {alg_name}: No solution found")
                    else:
                        print(f"    ✗ {alg_name}: Failed - {result['error']}")
                        
            except Exception as e:
                print(f"  Error loading {map_name}: {str(e)}")
                continue
    
    def save_results(self):
        """Save results to CSV and JSON files"""
        if not self.results:
            print("No results to save!")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(self.results)
        
        # Save to CSV
        csv_file = self.results_directory / 'experiment_results.csv'
        df.to_csv(csv_file, index=False)
        print(f"Results saved to {csv_file}")
        
        # Save to JSON
        json_file = self.results_directory / 'experiment_results.json'
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to {json_file}")
        
        # Save experiment metadata
        metadata = {
            'run_directory': str(self.results_directory),
            'selected_maps': self.selected_maps,
            'total_maps': len(set(result['map'] for result in self.results)),
            'total_experiments': len(self.results),
            'algorithms_tested': list(self.algorithms.keys()),
            'experiment_date': datetime.now().isoformat(),
            'max_time_per_algorithm': self.max_time
        }
        
        metadata_file = self.results_directory / 'experiment_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to {metadata_file}")
        
        return df
    
    def generate_visualizations(self, df):
        """Generate comprehensive visualizations"""
        print("Generating visualizations...")
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Filter successful results
        df_success = df[df['success'] == True].copy()
        
        if df_success.empty:
            print("No successful results to visualize!")
            return
        
        # Replace infinite values with NaN for better visualization
        df_success = df_success.replace([float('inf'), -float('inf')], float('nan'))
        
        # 1. Search Time Comparison
        self._plot_search_time(df_success)
        
        # 2. Memory Usage Comparison
        self._plot_memory_usage(df_success)
        
        # 3. Nodes Expanded Comparison
        self._plot_nodes_expanded(df_success)
        
        # 4. Solution Quality Comparison
        self._plot_solution_quality(df_success)
        
        # 5. Success Rate Analysis
        self._plot_success_rate(df)
        
        # 6. Performance Heatmap
        self._plot_performance_heatmap(df_success)
        
        # 7. Comprehensive Dashboard
        self._create_dashboard(df_success)
        
        print(f"All visualizations saved to {self.results_directory}")
    
    def _plot_search_time(self, df):
        """Plot search time comparison"""
        plt.figure(figsize=(14, 8))
        
        # Create pivot table for better visualization
        pivot_df = df.pivot(index='map', columns='algorithm', values='search_time')
        
        # Create bar plot
        ax = pivot_df.plot(kind='bar', figsize=(14, 8), log=True)
        plt.title('Search Time Comparison Across Maps and Algorithms', fontsize=16, fontweight='bold')
        plt.xlabel('Map', fontsize=12)
        plt.ylabel('Search Time (seconds, log scale)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Algorithm', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(self.results_directory / 'search_time_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_memory_usage(self, df):
        """Plot memory usage comparison"""
        plt.figure(figsize=(14, 8))
        
        pivot_df = df.pivot(index='map', columns='algorithm', values='memory_usage')
        
        ax = pivot_df.plot(kind='bar', figsize=(14, 8))
        plt.title('Memory Usage Comparison Across Maps and Algorithms', fontsize=16, fontweight='bold')
        plt.xlabel('Map', fontsize=12)
        plt.ylabel('Memory Usage (KB)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Algorithm', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(self.results_directory / 'memory_usage_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_nodes_expanded(self, df):
        """Plot nodes expanded comparison"""
        plt.figure(figsize=(14, 8))
        
        pivot_df = df.pivot(index='map', columns='algorithm', values='nodes_expanded')
        
        ax = pivot_df.plot(kind='bar', figsize=(14, 8), log=True)
        plt.title('Nodes Expanded Comparison Across Maps and Algorithms', fontsize=16, fontweight='bold')
        plt.xlabel('Map', fontsize=12)
        plt.ylabel('Nodes Expanded (log scale)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Algorithm', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(self.results_directory / 'nodes_expanded_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_solution_quality(self, df):
        """Plot solution quality (length) comparison"""
        df_solved = df[df['solution_found'] == True].copy()
        
        if df_solved.empty:
            return
        
        plt.figure(figsize=(14, 8))
        
        pivot_df = df_solved.pivot(index='map', columns='algorithm', values='solution_length')
        
        ax = pivot_df.plot(kind='bar', figsize=(14, 8))
        plt.title('Solution Quality Comparison (Number of Moves)', fontsize=16, fontweight='bold')
        plt.xlabel('Map', fontsize=12)
        plt.ylabel('Solution Length (moves)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Algorithm', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(self.results_directory / 'solution_quality_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_success_rate(self, df):
        """Plot success rate by algorithm"""
        success_rates = df.groupby('algorithm')['solution_found'].mean() * 100
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(success_rates.index, success_rates.values, color='skyblue', edgecolor='navy')
        plt.title('Algorithm Success Rate', fontsize=16, fontweight='bold')
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylabel('Success Rate (%)', fontsize=12)
        plt.ylim(0, 100)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(self.results_directory / 'success_rate_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_performance_heatmap(self, df):
        """Create performance heatmap"""
        # Create performance metrics heatmap
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        metrics = ['search_time', 'memory_usage', 'nodes_expanded', 'solution_length']
        titles = ['Search Time', 'Memory Usage', 'Nodes Expanded', 'Solution Length']
        
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            row, col = i // 2, i % 2
            
            if metric == 'solution_length':
                data = df[df['solution_found'] == True]
            else:
                data = df[df['success'] == True]
            
            if data.empty:
                continue
                
            pivot = data.pivot(index='algorithm', columns='map', values=metric)
            
            sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlOrRd', 
                       ax=axes[row, col], cbar_kws={'label': title})
            axes[row, col].set_title(f'{title} Heatmap', fontsize=14, fontweight='bold')
            axes[row, col].set_xlabel('Map', fontsize=12)
            axes[row, col].set_ylabel('Algorithm', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(self.results_directory / 'performance_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_dashboard(self, df):
        """Create comprehensive dashboard"""
        fig = plt.figure(figsize=(20, 15))
        
        # Create subplots
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Average performance by algorithm
        ax1 = fig.add_subplot(gs[0, :])
        avg_metrics = df.groupby('algorithm')[['search_time', 'memory_usage', 'nodes_expanded']].mean()
        avg_metrics.plot(kind='bar', ax=ax1, log=True)
        ax1.set_title('Average Performance Metrics by Algorithm', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Value (log scale)')
        ax1.legend(['Search Time (s)', 'Memory Usage (KB)', 'Nodes Expanded'])
        
        # 2. Performance vs Map Difficulty
        ax2 = fig.add_subplot(gs[1, 0])
        map_difficulty = df.groupby('map')['nodes_expanded'].mean().sort_values()
        ax2.plot(range(len(map_difficulty)), map_difficulty.values, 'o-')
        ax2.set_title('Map Difficulty\n(by avg nodes expanded)', fontsize=12)
        ax2.set_xlabel('Map (sorted by difficulty)')
        ax2.set_ylabel('Avg Nodes Expanded')
        ax2.set_xticks(range(len(map_difficulty)))
        ax2.set_xticklabels(map_difficulty.index, rotation=45)
        
        # 3. Algorithm efficiency (Time vs Nodes)
        ax3 = fig.add_subplot(gs[1, 1])
        for alg in df['algorithm'].unique():
            alg_data = df[df['algorithm'] == alg]
            ax3.scatter(alg_data['nodes_expanded'], alg_data['search_time'], 
                       label=alg, alpha=0.7, s=50)
        ax3.set_xlabel('Nodes Expanded')
        ax3.set_ylabel('Search Time (s)')
        ax3.set_title('Algorithm Efficiency\n(Time vs Nodes)', fontsize=12)
        ax3.legend()
        ax3.set_xscale('log')
        ax3.set_yscale('log')
        
        # 4. Memory efficiency
        ax4 = fig.add_subplot(gs[1, 2])
        for alg in df['algorithm'].unique():
            alg_data = df[df['algorithm'] == alg]
            ax4.scatter(alg_data['nodes_expanded'], alg_data['memory_usage'], 
                       label=alg, alpha=0.7, s=50)
        ax4.set_xlabel('Nodes Expanded')
        ax4.set_ylabel('Memory Usage (KB)')
        ax4.set_title('Memory Efficiency', fontsize=12)
        ax4.legend()
        ax4.set_xscale('log')
        
        # 5. Solution quality distribution
        ax5 = fig.add_subplot(gs[2, :])
        solved_df = df[df['solution_found'] == True]
        if not solved_df.empty:
            solved_df.boxplot(column='solution_length', by='algorithm', ax=ax5)
            ax5.set_title('Solution Quality Distribution by Algorithm', fontsize=14)
            ax5.set_xlabel('Algorithm')
            ax5.set_ylabel('Solution Length (moves)')
        
        plt.suptitle('AI Rush Hour - Algorithm Performance Dashboard', fontsize=20, fontweight='bold')
        plt.savefig(self.results_directory / 'performance_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_insights(self, df):
        """Generate insights from the experimental results"""
        print("\nGenerating insights...")
        
        insights = []
        
        # Overall performance summary
        insights.append("# AI Rush Hour - Experimental Results Analysis\n")
        insights.append(f"**Experiment Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        insights.append(f"**Total Maps Tested:** {df['map'].nunique()}")
        insights.append(f"**Total Algorithm Runs:** {len(df)}")
        insights.append(f"**Successful Runs:** {df['success'].sum()}")
        insights.append(f"**Overall Success Rate:** {df['success'].mean()*100:.1f}%\n")
        
        # Algorithm performance summary
        insights.append("## Algorithm Performance Summary\n")
        for alg in df['algorithm'].unique():
            alg_data = df[df['algorithm'] == alg]
            success_rate = alg_data['success'].mean() * 100
            solve_rate = alg_data['solution_found'].mean() * 100
            
            if alg_data['success'].any():
                avg_time = alg_data[alg_data['success']]['search_time'].mean()
                avg_memory = alg_data[alg_data['success']]['memory_usage'].mean()
                avg_nodes = alg_data[alg_data['success']]['nodes_expanded'].mean()
                
                insights.append(f"### {alg}")
                insights.append(f"- **Success Rate:** {success_rate:.1f}%")
                insights.append(f"- **Solution Rate:** {solve_rate:.1f}%")
                insights.append(f"- **Average Search Time:** {avg_time:.3f}s")
                insights.append(f"- **Average Memory Usage:** {avg_memory:.2f}KB")
                insights.append(f"- **Average Nodes Expanded:** {avg_nodes:.0f}")
                insights.append("")
        
        # Map difficulty analysis
        insights.append("## Map Difficulty Analysis\n")
        map_stats = df[df['success']].groupby('map').agg({
            'nodes_expanded': 'mean',
            'search_time': 'mean',
            'solution_length': 'mean'
        }).round(2)
        
        easiest_map = map_stats['nodes_expanded'].idxmin()
        hardest_map = map_stats['nodes_expanded'].idxmax()
        
        insights.append(f"**Easiest Map:** {easiest_map} (avg {map_stats.loc[easiest_map, 'nodes_expanded']:.0f} nodes)")
        insights.append(f"**Hardest Map:** {hardest_map} (avg {map_stats.loc[hardest_map, 'nodes_expanded']:.0f} nodes)")
        insights.append("")
        
        # Key findings
        insights.append("## Key Findings\n")
        
        # Best algorithm for time
        best_time_alg = df[df['success']].groupby('algorithm')['search_time'].mean().idxmin()
        insights.append(f"1. **Fastest Algorithm:** {best_time_alg}")
        
        # Best algorithm for memory
        best_memory_alg = df[df['success']].groupby('algorithm')['memory_usage'].mean().idxmin()
        insights.append(f"2. **Most Memory Efficient:** {best_memory_alg}")
        
        # Best algorithm for nodes
        best_nodes_alg = df[df['success']].groupby('algorithm')['nodes_expanded'].mean().idxmin()
        insights.append(f"3. **Most Node Efficient:** {best_nodes_alg}")
        
        # Most reliable algorithm
        most_reliable = df.groupby('algorithm')['success'].mean().idxmax()
        insights.append(f"4. **Most Reliable:** {most_reliable}")
        
        # Save insights
        with open(self.results_directory / 'insights.md', 'w') as f:
            f.write('\n'.join(insights))
        
        print(f"Insights saved to {self.results_directory / 'insights.md'}")
        
        # Print summary to console
        print("\n" + "="*50)
        print("EXPERIMENT SUMMARY")
        print("="*50)
        for line in insights[:15]:  # Print first few insights
            print(line)
        print(f"\nFull analysis saved to {self.results_directory / 'insights.md'}")

def main():
    """Main function to run the experiments"""
    print("AI Rush Hour - Algorithm Performance Experiment")
    print("="*50)
    
    # Examples of how to use the new map selection feature:
    
    # Option 1: Run all maps (default behavior)
    runner = ExperimentRunner()
    
    # Option 2: Run only specific maps
    # runner = ExperimentRunner(selected_maps=['map01', 'map02', 'map03'])
    
    # Option 3: Run all maps except problematic ones
    # runner = ExperimentRunner(selected_maps=['map01', 'map02', 'map03', 'map04', 'map05', 'map07', 'map08', 'map09', 'map10'])
    
    # Current configuration - you can modify this as needed
    # For now, excluding map06 as requested
    # selected_maps = ['map03']
    # runner = ExperimentRunner(selected_maps=selected_maps)
    
    # Run experiments
    runner.run_experiments()
    
    # Save results
    df = runner.save_results()
    
    if df is not None and not df.empty:
        # Generate visualizations
        runner.generate_visualizations(df)
        
        # Generate insights
        runner.generate_insights(df)
        
        print("\nExperiment completed successfully!")
        print(f"Results saved to: {runner.results_directory}")
    else:
        print("No results to analyze!")

if __name__ == "__main__":
    main()
