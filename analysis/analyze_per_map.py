import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class PerMapAnalyzer:
    def __init__(self, results_file='experiment_results.json'):
        """
        Khởi tạo analyzer để phân tích chi tiết từng map
        
        Args:
            results_file: Đường dẫn tới file JSON chứa kết quả thử nghiệm
        """
        # Xác định thư mục lưu kết quả
        self.output_dir = Path(__file__).parent / 'per_map_analysis'
        self.output_dir.mkdir(exist_ok=True)
        
        # Xác định đường dẫn file kết quả
        if not Path(results_file).is_absolute():
            current_dir = Path.cwd()
            possible_paths = [
                current_dir / results_file,
                current_dir / 'src' / results_file,
                current_dir / 'src' / 'experiment_results' / 'experiment_results.json',
                Path(__file__).parent / results_file,
                Path(__file__).parent / 'experiment_results' / 'experiment_results.json'
            ]
            
            self.results_file = None
            for path in possible_paths:
                if path.exists():
                    self.results_file = path
                    break
            
            if self.results_file is None:
                raise FileNotFoundError(f"Không tìm thấy file kết quả experiment_results.json")
        else:
            self.results_file = Path(results_file)
        
        print(f"Sử dụng file kết quả: {self.results_file}")
        print(f"Kết quả phân tích từng map sẽ được lưu tại: {self.output_dir}")
        
        self.data = None
        self.df = None
        
    def load_data(self):
        """Load dữ liệu từ file JSON"""
        if not self.results_file.exists():
            raise FileNotFoundError(f"File {self.results_file} không tồn tại!")
        
        with open(self.results_file, 'r') as f:
            self.data = json.load(f)
        
        self.df = pd.DataFrame(self.data)
        print(f"Đã load {len(self.df)} kết quả thử nghiệm")
        
    def analyze_single_map(self, map_name):
        """Phân tích chi tiết cho một map cụ thể"""
        print(f"\n{'='*80}")
        print(f"PHÂN TÍCH CHI TIẾT MAP: {map_name.upper()}")
        print(f"{'='*80}")
        
        # Lấy dữ liệu cho map này
        map_data = self.df[self.df['map'] == map_name].copy()
        
        if map_data.empty:
            print(f"Không có dữ liệu cho map {map_name}")
            return None
        
        print(f"Tổng số thử nghiệm: {len(map_data)}")
        
        # 1. TỔNG QUAN
        print(f"\n1. TỔNG QUAN:")
        print(f"-" * 50)
        
        total_runs = len(map_data)
        successful_runs = len(map_data[map_data['success'] == True])
        solved_runs = len(map_data[map_data['solution_found'] == True])
        
        print(f"  - Tổng số lần chạy: {total_runs}")
        print(f"  - Lần chạy thành công: {successful_runs} ({successful_runs/total_runs*100:.1f}%)")
        print(f"  - Tìm được lời giải: {solved_runs} ({solved_runs/total_runs*100:.1f}%)")
        
        # 2. PHÂN TÍCH THEO THUẬT TOÁN
        print(f"\n2. PHÂN TÍCH THEO THUẬT TOÁN:")
        print(f"-" * 50)
        
        algorithm_stats = []
        for algorithm in map_data['algorithm'].unique():
            alg_data = map_data[map_data['algorithm'] == algorithm]
            solved_data = alg_data[alg_data['solution_found'] == True]
            
            stats = {
                'algorithm': algorithm,
                'total_runs': len(alg_data),
                'success_runs': len(alg_data[alg_data['success'] == True]),
                'solved_runs': len(solved_data),
                'success_rate': len(alg_data[alg_data['success'] == True]) / len(alg_data) * 100,
                'solve_rate': len(solved_data) / len(alg_data) * 100
            }
            
            if not solved_data.empty:
                stats.update({
                    'avg_time': solved_data['search_time'].mean(),
                    'std_time': solved_data['search_time'].std(),
                    'min_time': solved_data['search_time'].min(),
                    'max_time': solved_data['search_time'].max(),
                    'avg_memory': solved_data['memory_usage'].mean(),
                    'avg_nodes': solved_data['nodes_expanded'].mean(),
                    'avg_solution_length': solved_data['solution_length'].mean(),
                    'min_solution_length': solved_data['solution_length'].min(),
                    'max_solution_length': solved_data['solution_length'].max(),
                })
            else:
                stats.update({
                    'avg_time': None, 'std_time': None, 'min_time': None, 'max_time': None,
                    'avg_memory': None, 'avg_nodes': None, 'avg_solution_length': None,
                    'min_solution_length': None, 'max_solution_length': None
                })
            
            algorithm_stats.append(stats)
        
        stats_df = pd.DataFrame(algorithm_stats)
        
        # In kết quả
        print("Tỷ lệ thành công:")
        for _, row in stats_df.iterrows():
            print(f"  {row['algorithm']}: {row['solved_runs']}/{row['total_runs']} ({row['solve_rate']:.1f}%)")
        
        # 3. HIỆU SUẤT CHI TIẾT (chỉ các thuật toán tìm được lời giải)
        solved_stats = stats_df[stats_df['solved_runs'] > 0].copy()
        
        if not solved_stats.empty:
            print(f"\n3. HIỆU SUẤT CHI TIẾT (các thuật toán tìm được lời giải):")
            print(f"-" * 50)
            
            print("\nThời gian tìm kiếm:")
            sorted_by_time = solved_stats.sort_values('avg_time')
            for i, (_, row) in enumerate(sorted_by_time.iterrows(), 1):
                print(f"  {i}. {row['algorithm']}: {row['avg_time']:.3f}s "
                      f"(±{row['std_time']:.3f}s, min: {row['min_time']:.3f}s, max: {row['max_time']:.3f}s)")
            
            print("\nSử dụng bộ nhớ:")
            sorted_by_memory = solved_stats.sort_values('avg_memory')
            for i, (_, row) in enumerate(sorted_by_memory.iterrows(), 1):
                print(f"  {i}. {row['algorithm']}: {row['avg_memory']:.1f}KB")
            
            print("\nSố node mở rộng:")
            sorted_by_nodes = solved_stats.sort_values('avg_nodes')
            for i, (_, row) in enumerate(sorted_by_nodes.iterrows(), 1):
                print(f"  {i}. {row['algorithm']}: {row['avg_nodes']:.0f} nodes")
            
            print("\nĐộ dài lời giải:")
            sorted_by_solution = solved_stats.sort_values('avg_solution_length')
            for i, (_, row) in enumerate(sorted_by_solution.iterrows(), 1):
                print(f"  {i}. {row['algorithm']}: {row['avg_solution_length']:.1f} moves "
                      f"(min: {row['min_solution_length']:.0f}, max: {row['max_solution_length']:.0f})")
        
        # 4. PHÂN TÍCH ĐỘ KHUYẾN NGHỊ
        print(f"\n4. KHUYẾN NGHỊ CHO MAP {map_name.upper()}:")
        print(f"-" * 50)
        
        if not solved_stats.empty:
            # Thuật toán tốt nhất cho map này
            best_overall = self.calculate_map_score(solved_stats)
            print(f"Thuật toán được khuyến nghị: {best_overall}")
            
            # Phân tích độ khó
            if solved_stats['avg_nodes'].max() > 10000:
                difficulty = "RẤT KHÓ"
            elif solved_stats['avg_nodes'].max() > 1000:
                difficulty = "KHÓ"
            elif solved_stats['avg_nodes'].max() > 100:
                difficulty = "VỪA"
            else:
                difficulty = "DỄ"
            
            print(f"Độ khó map: {difficulty}")
            print(f"Số node trung bình: {solved_stats['avg_nodes'].mean():.0f}")
            
            # Khuyến nghị cụ thể
            if difficulty == "DỄ":
                print("→ Tất cả thuật toán đều có thể sử dụng hiệu quả")
            elif difficulty == "VỪA":
                print("→ Ưu tiên A*, BFS, UCS. Tránh DFS cho bài toán phức tạp")
            elif difficulty == "KHÓ":
                print("→ Khuyến nghị A* hoặc UCS. BFS có thể chậm. Tránh DFS, IDS")
            else:  # RẤT KHÓ
                print("→ Chỉ nên sử dụng A* với heuristic tốt. Các thuật toán khác có thể không khả thi")
        else:
            print("MAP RẤT KHÓ - Không có thuật toán nào tìm được lời giải!")
            print("→ Cần cải thiện thuật toán hoặc tăng giới hạn thời gian/bộ nhớ")
        
        # 5. LƯU KẾT QUẢ CHI TIẾT
        map_output_dir = self.output_dir / map_name
        map_output_dir.mkdir(exist_ok=True)
        
        # Lưu thống kê dạng CSV
        stats_df.to_csv(map_output_dir / f"{map_name}_statistics.csv", index=False)
        
        # Lưu dữ liệu raw cho map này
        map_data.to_csv(map_output_dir / f"{map_name}_raw_data.csv", index=False)
        
        # Tạo biểu đồ cho map này
        self.create_map_visualizations(map_name, map_data, solved_stats)
        
        print(f"\nĐã lưu kết quả chi tiết tại: {map_output_dir}")
        
        return stats_df
    
    def calculate_map_score(self, solved_stats):
        """Tính điểm tổng hợp cho các thuật toán trên map cụ thể"""
        if solved_stats.empty:
            return "Không có"
        
        scores = {}
        
        for _, row in solved_stats.iterrows():
            alg = row['algorithm']
            
            # Điểm theo các tiêu chí (normalize về 0-100)
            time_score = 100 - (row['avg_time'] / solved_stats['avg_time'].max()) * 100
            memory_score = 100 - (row['avg_memory'] / solved_stats['avg_memory'].max()) * 100
            nodes_score = 100 - (row['avg_nodes'] / solved_stats['avg_nodes'].max()) * 100
            solution_score = 100 - (row['avg_solution_length'] / solved_stats['avg_solution_length'].max()) * 100
            
            # Điểm tổng hợp (weighted)
            composite_score = (
                time_score * 0.3 +      # Thời gian quan trọng
                memory_score * 0.2 +    # Bộ nhớ
                nodes_score * 0.3 +     # Hiệu quả
                solution_score * 0.2    # Chất lượng lời giải
            )
            
            scores[alg] = composite_score
        
        return max(scores, key=scores.get)
    
    def create_map_visualizations(self, map_name, map_data, solved_stats):
        """Tạo biểu đồ cho map cụ thể"""
        map_output_dir = self.output_dir / map_name
        
        # Chỉ tạo biểu đồ nếu có dữ liệu solved
        solved_data = map_data[map_data['solution_found'] == True]
        
        if solved_data.empty:
            print(f"Không có dữ liệu để tạo biểu đồ cho {map_name}")
            return
        
        plt.style.use('seaborn-v0_8')
        
        # 1. Success Rate
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Success rate by algorithm
        success_rate = map_data.groupby('algorithm')['solution_found'].mean() * 100
        axes[0, 0].bar(success_rate.index, success_rate.values, color='skyblue', edgecolor='navy')
        axes[0, 0].set_title(f'{map_name} - Success Rate by Algorithm')
        axes[0, 0].set_ylabel('Success Rate (%)')
        axes[0, 0].set_ylim(0, 100)
        for i, v in enumerate(success_rate.values):
            axes[0, 0].text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
        
        # Time comparison
        if not solved_data.empty:
            time_data = solved_data.groupby('algorithm')['search_time'].mean()
            axes[0, 1].bar(time_data.index, time_data.values, color='lightcoral', edgecolor='darkred')
            axes[0, 1].set_title(f'{map_name} - Average Search Time')
            axes[0, 1].set_ylabel('Search Time (s)')
            axes[0, 1].set_yscale('log')
        
        # Memory usage
        if not solved_data.empty:
            memory_data = solved_data.groupby('algorithm')['memory_usage'].mean()
            axes[1, 0].bar(memory_data.index, memory_data.values, color='lightgreen', edgecolor='darkgreen')
            axes[1, 0].set_title(f'{map_name} - Average Memory Usage')
            axes[1, 0].set_ylabel('Memory Usage (KB)')
            axes[1, 0].set_yscale('log')
        
        # Nodes expanded
        if not solved_data.empty:
            nodes_data = solved_data.groupby('algorithm')['nodes_expanded'].mean()
            axes[1, 1].bar(nodes_data.index, nodes_data.values, color='gold', edgecolor='orange')
            axes[1, 1].set_title(f'{map_name} - Average Nodes Expanded')
            axes[1, 1].set_ylabel('Nodes Expanded')
            axes[1, 1].set_yscale('log')
        
        plt.tight_layout()
        plt.savefig(map_output_dir / f'{map_name}_performance_overview.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Detailed performance comparison
        if len(solved_data) > 0:
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            
            # Scatter plot: time vs nodes
            algorithms = solved_data['algorithm'].unique()
            colors = plt.cm.tab10(np.linspace(0, 1, len(algorithms)))
            
            for i, alg in enumerate(algorithms):
                alg_data = solved_data[solved_data['algorithm'] == alg]
                ax.scatter(alg_data['nodes_expanded'], alg_data['search_time'], 
                          label=alg, alpha=0.7, s=100, color=colors[i])
            
            ax.set_xlabel('Nodes Expanded')
            ax.set_ylabel('Search Time (s)')
            ax.set_title(f'{map_name} - Time vs Nodes Expanded')
            ax.legend()
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(map_output_dir / f'{map_name}_time_vs_nodes.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Solution quality distribution
        if len(solved_data) > 0:
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            
            solved_data.boxplot(column='solution_length', by='algorithm', ax=ax)
            ax.set_title(f'{map_name} - Solution Length Distribution')
            ax.set_xlabel('Algorithm')
            ax.set_ylabel('Solution Length (moves)')
            
            plt.tight_layout()
            plt.savefig(map_output_dir / f'{map_name}_solution_quality.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"Đã tạo biểu đồ cho {map_name}:")
        print(f"  - {map_output_dir / f'{map_name}_performance_overview.png'}")
        if len(solved_data) > 0:
            print(f"  - {map_output_dir / f'{map_name}_time_vs_nodes.png'}")
            print(f"  - {map_output_dir / f'{map_name}_solution_quality.png'}")
    
    def analyze_all_maps(self):
        """Phân tích tất cả các map"""
        print(f"\n{'='*80}")
        print("PHÂN TÍCH CHI TIẾT TẤT CẢ CÁC MAP")
        print(f"{'='*80}")
        
        maps = sorted(self.df['map'].unique())
        all_stats = {}
        
        for map_name in maps:
            stats = self.analyze_single_map(map_name)
            if stats is not None:
                all_stats[map_name] = stats
        
        # Tạo báo cáo tổng hợp
        self.create_summary_report(all_stats)
        
        return all_stats
    
    def create_summary_report(self, all_stats):
        """Tạo báo cáo tổng hợp so sánh các map"""
        print(f"\n{'='*80}")
        print("BÁO CÁO TỔNG HỢP SO SÁNH CÁC MAP")
        print(f"{'='*80}")
        
        summary_data = []
        
        for map_name, stats_df in all_stats.items():
            solved_stats = stats_df[stats_df['solved_runs'] > 0]
            
            if not solved_stats.empty:
                summary = {
                    'map': map_name,
                    'algorithms_solved': len(solved_stats),
                    'total_algorithms': len(stats_df),
                    'avg_time': solved_stats['avg_time'].mean(),
                    'min_time': solved_stats['avg_time'].min(),
                    'max_time': solved_stats['avg_time'].max(),
                    'avg_nodes': solved_stats['avg_nodes'].mean(),
                    'min_nodes': solved_stats['avg_nodes'].min(),
                    'max_nodes': solved_stats['avg_nodes'].max(),
                    'avg_solution_length': solved_stats['avg_solution_length'].mean(),
                    'best_algorithm': self.calculate_map_score(solved_stats)
                }
            else:
                summary = {
                    'map': map_name,
                    'algorithms_solved': 0,
                    'total_algorithms': len(stats_df),
                    'avg_time': None, 'min_time': None, 'max_time': None,
                    'avg_nodes': None, 'min_nodes': None, 'max_nodes': None,
                    'avg_solution_length': None,
                    'best_algorithm': 'Không có'
                }
            
            summary_data.append(summary)
        
        summary_df = pd.DataFrame(summary_data)
        
        # In báo cáo
        print("\n1. TỔNG QUAN TỪNG MAP:")
        print("-" * 60)
        for _, row in summary_df.iterrows():
            print(f"{row['map']}:")
            print(f"  - Thuật toán giải được: {row['algorithms_solved']}/{row['total_algorithms']}")
            if row['avg_time'] is not None:
                print(f"  - Thời gian trung bình: {row['avg_time']:.3f}s")
                print(f"  - Nodes trung bình: {row['avg_nodes']:.0f}")
                print(f"  - Thuật toán tốt nhất: {row['best_algorithm']}")
            else:
                print(f"  - KHÔNG CÓ THUẬT TOÁN NÀO GIẢI ĐƯỢC!")
            print()
        
        # Xếp hạng độ khó
        solvable_maps = summary_df[summary_df['avg_nodes'].notna()].copy()
        if not solvable_maps.empty:
            print("\n2. XẾP HẠNG ĐỘ KHÓ (theo số nodes trung bình):")
            print("-" * 60)
            difficulty_ranking = solvable_maps.sort_values('avg_nodes')
            for i, (_, row) in enumerate(difficulty_ranking.iterrows(), 1):
                print(f"  {i}. {row['map']}: {row['avg_nodes']:.0f} nodes (thuật toán tốt nhất: {row['best_algorithm']})")
        
        # Maps không giải được
        unsolvable_maps = summary_df[summary_df['algorithms_solved'] == 0]
        if not unsolvable_maps.empty:
            print("\n3. CÁC MAP KHÔNG GIẢI ĐƯỢC:")
            print("-" * 60)
            for _, row in unsolvable_maps.iterrows():
                print(f"  - {row['map']}: Cần cải thiện thuật toán hoặc tăng giới hạn")
        
        # Lưu báo cáo tổng hợp
        summary_df.to_csv(self.output_dir / 'maps_summary_report.csv', index=False)
        
        # Tạo biểu đồ so sánh maps
        self.create_maps_comparison_chart(summary_df)
        
        print(f"\nĐã lưu báo cáo tổng hợp tại: {self.output_dir / 'maps_summary_report.csv'}")
    
    def create_maps_comparison_chart(self, summary_df):
        """Tạo biểu đồ so sánh các map"""
        solvable_maps = summary_df[summary_df['avg_nodes'].notna()].copy()
        
        if solvable_maps.empty:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Số thuật toán giải được
        axes[0, 0].bar(summary_df['map'], summary_df['algorithms_solved'], color='lightblue', edgecolor='navy')
        axes[0, 0].set_title('Number of Algorithms that Solved Each Map')
        axes[0, 0].set_ylabel('Number of Algorithms')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Độ khó (nodes)
        axes[0, 1].bar(solvable_maps['map'], solvable_maps['avg_nodes'], color='orange', edgecolor='darkorange')
        axes[0, 1].set_title('Map Difficulty (Average Nodes Expanded)')
        axes[0, 1].set_ylabel('Average Nodes Expanded')
        axes[0, 1].set_yscale('log')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Thời gian giải
        axes[1, 0].bar(solvable_maps['map'], solvable_maps['avg_time'], color='lightgreen', edgecolor='darkgreen')
        axes[1, 0].set_title('Average Solving Time by Map')
        axes[1, 0].set_ylabel('Average Time (s)')
        axes[1, 0].set_yscale('log')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Độ dài lời giải
        axes[1, 1].bar(solvable_maps['map'], solvable_maps['avg_solution_length'], color='coral', edgecolor='darkred')
        axes[1, 1].set_title('Average Solution Length by Map')
        axes[1, 1].set_ylabel('Average Solution Length (moves)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'maps_comparison_overview.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Đã tạo biểu đồ so sánh maps: {self.output_dir / 'maps_comparison_overview.png'}")

def main():
    """Chương trình chính"""
    analyzer = PerMapAnalyzer()
    
    try:
        # Load dữ liệu
        analyzer.load_data()
        
        # Phân tích tất cả các map
        all_stats = analyzer.analyze_all_maps()
        
        print(f"\n{'='*80}")
        print("HOÀN THÀNH PHÂN TÍCH CHI TIẾT TỪNG MAP!")
        print(f"{'='*80}")
        print(f"Kết quả được lưu tại: {analyzer.output_dir}")
        print("Cấu trúc thư mục:")
        print(f"  {analyzer.output_dir}/")
        print("  ├── maps_summary_report.csv")
        print("  ├── maps_comparison_overview.png")
        for map_name in sorted(analyzer.df['map'].unique()):
            print(f"  ├── {map_name}/")
            print(f"  │   ├── {map_name}_statistics.csv")
            print(f"  │   ├── {map_name}_raw_data.csv")
            print(f"  │   ├── {map_name}_performance_overview.png")
            print(f"  │   ├── {map_name}_time_vs_nodes.png")
            print(f"  │   └── {map_name}_solution_quality.png")
        
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
