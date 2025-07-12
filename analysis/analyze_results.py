import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class ResultAnalyzer:
    def __init__(self, results_file='experiment_results.json'):
        """
        Khởi tạo analyzer với file kết quả
        
        Args:
            results_file: Đường dẫn tới file JSON chứa kết quả thử nghiệm
        """
        # Xác định thư mục lưu kết quả (cùng thư mục với file này)
        self.output_dir = Path(__file__).parent
        
        # Xác định đường dẫn file kết quả
        if not Path(results_file).is_absolute():
            # Nếu là đường dẫn tương đối, tìm từ thư mục hiện tại
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
                print("Không tìm thấy file kết quả. Các đường dẫn đã thử:")
                for path in possible_paths:
                    print(f"  - {path}")
                raise FileNotFoundError(f"Không tìm thấy file kết quả experiment_results.json")
        else:
            self.results_file = Path(results_file)
        
        print(f"Sử dụng file kết quả: {self.results_file}")
        print(f"Kết quả sẽ được lưu tại: {self.output_dir}")
        self.data = None
        self.df = None
        self.df_solved = None  # Chỉ các kết quả tìm được lời giải
        
    def load_data(self):
        """Load dữ liệu từ file JSON"""
        if not self.results_file.exists():
            raise FileNotFoundError(f"File {self.results_file} không tồn tại!")
        
        with open(self.results_file, 'r') as f:
            self.data = json.load(f)
        
        # Chuyển đổi thành DataFrame
        self.df = pd.DataFrame(self.data)
        
        # Chỉ lấy các kết quả tìm được lời giải và thành công
        self.df_solved = self.df[
            (self.df['solution_found'] == True) & 
            (self.df['success'] == True)
        ].copy()
        
        print(f"Đã load {len(self.df)} kết quả thử nghiệm")
        print(f"Trong đó {len(self.df_solved)} kết quả tìm được lời giải")
        
    def analyze_success_rates(self):
        """Phân tích tỷ lệ thành công của các thuật toán"""
        print("\n" + "="*60)
        print("PHÂN TÍCH TỶ LỆ THÀNH CÔNG")
        print("="*60)
        
        # Tổng quan
        total_experiments = len(self.df)
        successful_experiments = len(self.df[self.df['success'] == True])
        solved_experiments = len(self.df_solved)
        
        print(f"Tổng số thử nghiệm: {total_experiments}")
        print(f"Thử nghiệm thành công: {successful_experiments} ({successful_experiments/total_experiments*100:.1f}%)")
        print(f"Thử nghiệm tìm được lời giải: {solved_experiments} ({solved_experiments/total_experiments*100:.1f}%)")
        
        # Phân tích theo thuật toán
        print("\nTỷ lệ thành công theo thuật toán:")
        success_stats = self.df.groupby('algorithm').agg({
            'success': ['count', 'sum'],
            'solution_found': 'sum'
        }).round(2)
        
        success_stats.columns = ['total_runs', 'successful_runs', 'solutions_found']
        success_stats['success_rate'] = (success_stats['successful_runs'] / success_stats['total_runs'] * 100).round(1)
        success_stats['solution_rate'] = (success_stats['solutions_found'] / success_stats['total_runs'] * 100).round(1)
        
        print(success_stats[['total_runs', 'successful_runs', 'solutions_found', 'success_rate', 'solution_rate']])
        
        # Phân tích theo map
        print("\nTỷ lệ thành công theo map:")
        map_stats = self.df.groupby('map').agg({
            'success': ['count', 'sum'],
            'solution_found': 'sum'
        }).round(2)
        
        map_stats.columns = ['total_runs', 'successful_runs', 'solutions_found']
        map_stats['success_rate'] = (map_stats['successful_runs'] / map_stats['total_runs'] * 100).round(1)
        map_stats['solution_rate'] = (map_stats['solutions_found'] / map_stats['total_runs'] * 100).round(1)
        
        print(map_stats[['total_runs', 'successful_runs', 'solutions_found', 'success_rate', 'solution_rate']])
        
        return success_stats, map_stats
    
    def analyze_performance_for_solved(self):
        """Phân tích hiệu suất CHỈ cho các thuật toán tìm được lời giải"""
        if self.df_solved.empty:
            print("Không có kết quả nào tìm được lời giải để phân tích!")
            return
            
        print("\n" + "="*60)
        print("PHÂN TÍCH HIỆU SUẤT (CHỈ CÁC THUẬT TOÁN TÌM ĐƯỢC LỜI GIẢI)")
        print("="*60)
        
        # Thống kê tổng quan
        performance_stats = self.df_solved.groupby('algorithm').agg({
            'search_time': ['mean', 'std', 'min', 'max'],
            'memory_usage': ['mean', 'std', 'min', 'max'],
            'nodes_expanded': ['mean', 'std', 'min', 'max'],
            'solution_length': ['mean', 'std', 'min', 'max']
        }).round(3)
        
        print("\n1. THỜI GIAN TÌM KIẾM (giây):")
        print(performance_stats['search_time'])
        
        print("\n2. SỬ DỤNG BỘ NHỚ (KB):")
        print(performance_stats['memory_usage'])
        
        print("\n3. SỐ NODE ĐƯỢC MỞ RỘNG:")
        print(performance_stats['nodes_expanded'])
        
        print("\n4. ĐỘ DÀI LỜI GIẢI:")
        print(performance_stats['solution_length'])
        
        # Ranking thuật toán
        print("\n" + "="*60)
        print("RANKING THUẬT TOÁN (CHỈ TÍNH CÁC THUẬT TOÁN TÌM ĐƯỢC LỜI GIẢI)")
        print("="*60)
        
        avg_stats = self.df_solved.groupby('algorithm').agg({
            'search_time': 'mean',
            'memory_usage': 'mean',
            'nodes_expanded': 'mean',
            'solution_length': 'mean'
        }).round(3)
        
        print("\nThuật toán NHANH NHẤT (thời gian tìm kiếm thấp nhất):")
        fastest = avg_stats.sort_values('search_time')
        for i, (alg, row) in enumerate(fastest.iterrows(), 1):
            print(f"{i}. {alg}: {row['search_time']:.3f}s")
        
        print("\nThuật toán TIẾT KIỆM BỘ NHỚ NHẤT:")
        memory_efficient = avg_stats.sort_values('memory_usage')
        for i, (alg, row) in enumerate(memory_efficient.iterrows(), 1):
            print(f"{i}. {alg}: {row['memory_usage']:.1f}KB")
        
        print("\nThuật toán HIỆU QUẢ NHẤT (ít node mở rộng nhất):")
        node_efficient = avg_stats.sort_values('nodes_expanded')
        for i, (alg, row) in enumerate(node_efficient.iterrows(), 1):
            print(f"{i}. {alg}: {row['nodes_expanded']:.0f} nodes")
        
        print("\nThuật toán TÌM LỜI GIẢI TỐI ƯU NHẤT (lời giải ngắn nhất):")
        optimal = avg_stats.sort_values('solution_length')
        for i, (alg, row) in enumerate(optimal.iterrows(), 1):
            print(f"{i}. {alg}: {row['solution_length']:.1f} moves")
        
        return performance_stats, avg_stats
    
    def analyze_map_difficulty(self):
        """Phân tích độ khó của các map"""
        print("\n" + "="*60)
        print("PHÂN TÍCH ĐỘ KHÓ CỦA CÁC MAP")
        print("="*60)
        
        # Chỉ xem xét các map có ít nhất 1 thuật toán tìm được lời giải
        map_difficulty = self.df_solved.groupby('map').agg({
            'search_time': ['mean', 'std'],
            'nodes_expanded': ['mean', 'std'],
            'solution_length': ['mean', 'min', 'max']
        }).round(2)
        
        print("\nĐộ khó theo số node trung bình cần mở rộng:")
        difficulty_ranking = map_difficulty.sort_values(('nodes_expanded', 'mean'))
        for i, (map_name, row) in enumerate(difficulty_ranking.iterrows(), 1):
            avg_nodes = row[('nodes_expanded', 'mean')]
            avg_time = row[('search_time', 'mean')]
            print(f"{i}. {map_name}: {avg_nodes:.0f} nodes, {avg_time:.3f}s")
        
        # Phân tích maps không có lời giải
        unsolved_maps = self.df[self.df['solution_found'] == False]['map'].unique()
        if len(unsolved_maps) > 0:
            print(f"\nCác map có thuật toán không tìm được lời giải:")
            for map_name in unsolved_maps:
                unsolved_algs = self.df[
                    (self.df['map'] == map_name) & 
                    (self.df['solution_found'] == False)
                ]['algorithm'].unique()
                print(f"  {map_name}: {', '.join(unsolved_algs)}")
        
        return map_difficulty
    
    def compare_algorithms_by_map(self):
        """So sánh hiệu suất thuật toán theo từng map"""
        print("\n" + "="*60)
        print("SO SÁNH THUẬT TOÁN THEO TỪNG MAP")
        print("="*60)
        
        for map_name in sorted(self.df['map'].unique()):
            map_data = self.df_solved[self.df_solved['map'] == map_name]
            
            if map_data.empty:
                print(f"\n{map_name}: Không có thuật toán nào tìm được lời giải!")
                continue
                
            print(f"\n{map_name}:")
            print("-" * 40)
            
            # Sắp xếp theo thời gian tìm kiếm
            map_stats = map_data.groupby('algorithm').agg({
                'search_time': 'mean',
                'memory_usage': 'mean',
                'nodes_expanded': 'mean',
                'solution_length': 'mean'
            }).round(3)
            
            sorted_by_time = map_stats.sort_values('search_time')
            
            print("Ranking theo thời gian:")
            for i, (alg, row) in enumerate(sorted_by_time.iterrows(), 1):
                print(f"  {i}. {alg}: {row['search_time']:.3f}s, "
                      f"{row['nodes_expanded']:.0f} nodes, "
                      f"{row['solution_length']:.0f} moves")
    
    def create_visualizations(self):
        """Tạo các biểu đồ phân tích"""
        if self.df_solved.empty:
            print("Không có dữ liệu để tạo biểu đồ!")
            return
        
        # Thiết lập style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Success Rate Comparison
        plt.figure(figsize=(12, 8))
        success_rate = self.df.groupby('algorithm')['solution_found'].mean() * 100
        bars = plt.bar(success_rate.index, success_rate.values, color='skyblue', edgecolor='navy')
        plt.title('Algorithm Success Rate Comparison', fontsize=16, fontweight='bold')
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylabel('Success Rate (%)', fontsize=12)
        plt.ylim(0, 100)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'success_rate_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Search Time Comparison
        plt.figure(figsize=(12, 8))
        perf_data = self.df_solved.groupby('algorithm')['search_time'].mean()
        bars = plt.bar(perf_data.index, perf_data.values, color='lightcoral', edgecolor='darkred')
        plt.title('Search Time Comparison (Only Solved Cases)', fontsize=16, fontweight='bold')
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylabel('Average Search Time (seconds)', fontsize=12)
        plt.yscale('log')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'search_time_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Memory Usage Comparison
        plt.figure(figsize=(12, 8))
        memory_data = self.df_solved.groupby('algorithm')['memory_usage'].mean()
        bars = plt.bar(memory_data.index, memory_data.values, color='lightgreen', edgecolor='darkgreen')
        plt.title('Memory Usage Comparison (Only Solved Cases)', fontsize=16, fontweight='bold')
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylabel('Average Memory Usage (KB)', fontsize=12)
        plt.yscale('log')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'memory_usage_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Nodes Expanded Comparison
        plt.figure(figsize=(12, 8))
        nodes_data = self.df_solved.groupby('algorithm')['nodes_expanded'].mean()
        bars = plt.bar(nodes_data.index, nodes_data.values, color='gold', edgecolor='orange')
        plt.title('Nodes Expanded Comparison (Only Solved Cases)', fontsize=16, fontweight='bold')
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylabel('Average Nodes Expanded', fontsize=12)
        plt.yscale('log')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'nodes_expanded_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 5. Solution Quality Comparison
        plt.figure(figsize=(12, 8))
        quality_data = self.df_solved.groupby('algorithm')['solution_length'].mean()
        bars = plt.bar(quality_data.index, quality_data.values, color='mediumpurple', edgecolor='purple')
        plt.title('Solution Quality Comparison (Only Solved Cases)', fontsize=16, fontweight='bold')
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylabel('Average Solution Length (moves)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'solution_quality_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 6. Performance Heatmap
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        metrics = ['search_time', 'memory_usage', 'nodes_expanded', 'solution_length']
        titles = ['Search Time', 'Memory Usage', 'Nodes Expanded', 'Solution Length']
        
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            row, col = i // 2, i % 2
            
            pivot = self.df_solved.pivot_table(
                index='algorithm', 
                columns='map', 
                values=metric, 
                aggfunc='mean'
            )
            
            sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlOrRd', 
                       ax=axes[row, col], cbar_kws={'label': title})
            axes[row, col].set_title(f'{title} Heatmap', fontsize=14, fontweight='bold')
            axes[row, col].set_xlabel('Map', fontsize=12)
            axes[row, col].set_ylabel('Algorithm', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'performance_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 7. Performance Dashboard
        fig = plt.figure(figsize=(20, 15))
        
        # Create subplots
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Average performance by algorithm
        ax1 = fig.add_subplot(gs[0, :])
        avg_metrics = self.df_solved.groupby('algorithm')[['search_time', 'memory_usage', 'nodes_expanded']].mean()
        avg_metrics.plot(kind='bar', ax=ax1, log=True)
        ax1.set_title('Average Performance Metrics by Algorithm', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Value (log scale)')
        ax1.legend(['Search Time (s)', 'Memory Usage (KB)', 'Nodes Expanded'])
        
        # 2. Performance vs Map Difficulty
        ax2 = fig.add_subplot(gs[1, 0])
        map_difficulty = self.df_solved.groupby('map')['nodes_expanded'].mean().sort_values()
        ax2.plot(range(len(map_difficulty)), map_difficulty.values, 'o-')
        ax2.set_title('Map Difficulty\n(by avg nodes expanded)', fontsize=12)
        ax2.set_xlabel('Map (sorted by difficulty)')
        ax2.set_ylabel('Avg Nodes Expanded')
        ax2.set_xticks(range(len(map_difficulty)))
        ax2.set_xticklabels(map_difficulty.index, rotation=45)
        
        # 3. Algorithm efficiency (Time vs Nodes)
        ax3 = fig.add_subplot(gs[1, 1])
        for alg in self.df_solved['algorithm'].unique():
            alg_data = self.df_solved[self.df_solved['algorithm'] == alg]
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
        for alg in self.df_solved['algorithm'].unique():
            alg_data = self.df_solved[self.df_solved['algorithm'] == alg]
            ax4.scatter(alg_data['nodes_expanded'], alg_data['memory_usage'], 
                       label=alg, alpha=0.7, s=50)
        ax4.set_xlabel('Nodes Expanded')
        ax4.set_ylabel('Memory Usage (KB)')
        ax4.set_title('Memory Efficiency', fontsize=12)
        ax4.legend()
        ax4.set_xscale('log')
        
        # 5. Solution quality distribution
        ax5 = fig.add_subplot(gs[2, :])
        self.df_solved.boxplot(column='solution_length', by='algorithm', ax=ax5)
        ax5.set_title('Solution Quality Distribution by Algorithm', fontsize=14)
        ax5.set_xlabel('Algorithm')
        ax5.set_ylabel('Solution Length (moves)')
        
        plt.suptitle('AI Rush Hour - Algorithm Performance Dashboard', fontsize=20, fontweight='bold')
        plt.savefig(self.output_dir / 'performance_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Đã tạo các file biểu đồ:")
        print(f"  - {self.output_dir / 'success_rate_comparison.png'}")
        print(f"  - {self.output_dir / 'search_time_comparison.png'}")
        print(f"  - {self.output_dir / 'memory_usage_comparison.png'}")
        print(f"  - {self.output_dir / 'nodes_expanded_comparison.png'}")
        print(f"  - {self.output_dir / 'solution_quality_comparison.png'}")
        print(f"  - {self.output_dir / 'performance_heatmap.png'}")
        print(f"  - {self.output_dir / 'performance_dashboard.png'}")
    
    def generate_summary_report(self):
        """Tạo báo cáo tổng kết"""
        print("\n" + "="*80)
        print("BÁO CÁO TỔNG KẾT - PHÂN TÍCH CHÍNH XÁC")
        print("="*80)
        
        # Tổng quan
        total_maps = self.df['map'].nunique()
        total_algorithms = self.df['algorithm'].nunique()
        
        print(f"Tổng số map được test: {total_maps}")
        print(f"Tổng số thuật toán: {total_algorithms}")
        print(f"Tổng số thử nghiệm: {len(self.df)}")
        print(f"Số thử nghiệm tìm được lời giải: {len(self.df_solved)}")
        
        # Thuật toán tốt nhất
        if not self.df_solved.empty:
            avg_stats = self.df_solved.groupby('algorithm').agg({
                'search_time': 'mean',
                'memory_usage': 'mean',
                'nodes_expanded': 'mean',
                'solution_length': 'mean'
            })
            
            print("\nTHUẬT TOÁN TỐT NHẤT (dựa trên các thuật toán tìm được lời giải):")
            print(f"  Nhanh nhất: {avg_stats['search_time'].idxmin()}")
            print(f"  Tiết kiệm bộ nhớ nhất: {avg_stats['memory_usage'].idxmin()}")
            print(f"  Hiệu quả nhất (ít node nhất): {avg_stats['nodes_expanded'].idxmin()}")
            print(f"  Tối ưu nhất (lời giải ngắn nhất): {avg_stats['solution_length'].idxmin()}")
        
        # Tỷ lệ thành công
        success_rate = self.df.groupby('algorithm')['solution_found'].mean() * 100
        print(f"\nThuật toán đáng tin cậy nhất: {success_rate.idxmax()} ({success_rate.max():.1f}%)")
        
        # Map khó nhất
        if not self.df_solved.empty:
            map_difficulty = self.df_solved.groupby('map')['nodes_expanded'].mean()
            print(f"\nMap dễ nhất: {map_difficulty.idxmin()} ({map_difficulty.min():.0f} nodes)")
            print(f"Map khó nhất: {map_difficulty.idxmax()} ({map_difficulty.max():.0f} nodes)")
        
        print("\n" + "="*80)
        print("KẾT LUẬN:")
        print("- Phân tích này chỉ xem xét hiệu suất của các thuật toán KHI TÌM ĐƯỢC LỜI GIẢI")
        print("- Các thuật toán không tìm được lời giải được xem xét riêng trong tỷ lệ thành công")
        print("- Điều này đảm bảo tính chính xác trong việc đánh giá hiệu suất thuật toán")
        print("="*80)
    
    def get_common_solved_maps(self):
        """Tìm các map mà TẤT CẢ thuật toán đều tìm được lời giải"""
        all_algorithms = self.df['algorithm'].unique()
        common_maps = set()
        
        for map_name in self.df['map'].unique():
            map_data = self.df[self.df['map'] == map_name]
            solved_algorithms = set(map_data[map_data['solution_found'] == True]['algorithm'].unique())
            
            if len(solved_algorithms) == len(all_algorithms):
                common_maps.add(map_name)
        
        return common_maps

    def analyze_fair_comparison(self):
        """Phân tích so sánh công bằng giữa các thuật toán"""
        print("\n" + "="*80)
        print("PHÂN TÍCH SO SÁNH CÔNG BẰNG")
        print("="*80)
        
        all_algorithms = self.df['algorithm'].unique()
        total_maps = self.df['map'].nunique()
        
        # 1. Tìm maps mà tất cả thuật toán đều tìm được lời giải
        common_solved_maps = self.get_common_solved_maps()
        
        print(f"Tổng số maps: {total_maps}")
        print(f"Maps mà TẤT CẢ thuật toán đều tìm được lời giải: {len(common_solved_maps)}")
        
        if common_solved_maps:
            print(f"Danh sách maps chung: {sorted(common_solved_maps)}")
            
            # Phân tích trên tập dữ liệu công bằng
            fair_data = self.df[
                (self.df['map'].isin(common_solved_maps)) & 
                (self.df['solution_found'] == True)
            ]
            
            print("\n1. SO SÁNH HIỆU SUẤT CÔNG BẰNG (chỉ maps mà tất cả thuật toán đều giải được):")
            print("-" * 70)
            
            fair_stats = fair_data.groupby('algorithm').agg({
                'search_time': ['mean', 'std'],
                'memory_usage': ['mean', 'std'],
                'nodes_expanded': ['mean', 'std'],
                'solution_length': ['mean', 'std']
            }).round(3)
            
            print("\nThời gian tìm kiếm (giây):")
            time_ranking = fair_stats['search_time'].sort_values('mean')
            for i, (alg, row) in enumerate(time_ranking.iterrows(), 1):
                print(f"  {i}. {alg}: {row['mean']:.3f}s (±{row['std']:.3f})")
            
            print("\nSử dụng bộ nhớ (KB):")
            memory_ranking = fair_stats['memory_usage'].sort_values('mean')
            for i, (alg, row) in enumerate(memory_ranking.iterrows(), 1):
                print(f"  {i}. {alg}: {row['mean']:.1f}KB (±{row['std']:.1f})")
            
            print("\nSố node mở rộng:")
            nodes_ranking = fair_stats['nodes_expanded'].sort_values('mean')
            for i, (alg, row) in enumerate(nodes_ranking.iterrows(), 1):
                print(f"  {i}. {alg}: {row['mean']:.0f} nodes (±{row['std']:.0f})")
            
            print("\nĐộ dài lời giải:")
            solution_ranking = fair_stats['solution_length'].sort_values('mean')
            for i, (alg, row) in enumerate(solution_ranking.iterrows(), 1):
                print(f"  {i}. {alg}: {row['mean']:.1f} moves (±{row['std']:.1f})")
        
        # 2. Phân tích overlap giữa các thuật toán
        print("\n2. PHÂN TÍCH OVERLAP - Maps mà từng cặp thuật toán cùng giải được:")
        print("-" * 70)
        self.analyze_pairwise_overlap()
        
        # 3. Ma trận thành công
        print("\n3. MA TRẬN THÀNH CÔNG:")
        print("-" * 70)
        self.create_success_matrix()
        
        # 4. Điểm số công bằng
        print("\n4. HỆ THỐNG CHẤM ĐIỂM CÔNG BẰNG:")
        print("-" * 70)
        self.calculate_fair_scores()
        
        return fair_data if common_solved_maps else None

    def analyze_pairwise_overlap(self):
        """Phân tích overlap giữa từng cặp thuật toán"""
        import itertools
        
        algorithms = self.df['algorithm'].unique()
        
        for alg1, alg2 in itertools.combinations(algorithms, 2):
            # Tìm maps mà cả hai thuật toán đều giải được
            alg1_solved = set(self.df[
                (self.df['algorithm'] == alg1) & 
                (self.df['solution_found'] == True)
            ]['map'].unique())
            
            alg2_solved = set(self.df[
                (self.df['algorithm'] == alg2) & 
                (self.df['solution_found'] == True)
            ]['map'].unique())
            
            common_maps = alg1_solved.intersection(alg2_solved)
            
            if common_maps:
                print(f"\n{alg1} vs {alg2}:")
                print(f"  - {alg1} giải được: {len(alg1_solved)} maps")
                print(f"  - {alg2} giải được: {len(alg2_solved)} maps")
                print(f"  - Cùng giải được: {len(common_maps)} maps")
                
                # So sánh hiệu suất trên maps chung
                if len(common_maps) > 0:
                    common_data = self.df[
                        (self.df['map'].isin(common_maps)) & 
                        (self.df['algorithm'].isin([alg1, alg2])) &
                        (self.df['solution_found'] == True)
                    ]
                    
                    if not common_data.empty:
                        comparison = common_data.groupby('algorithm').agg({
                            'search_time': 'mean',
                            'nodes_expanded': 'mean',
                            'solution_length': 'mean'
                        }).round(3)
                        
                        print(f"  - Hiệu suất trên {len(common_maps)} maps chung:")
                        print(f"    {alg1}: {comparison.loc[alg1, 'search_time']:.3f}s, {comparison.loc[alg1, 'nodes_expanded']:.0f} nodes")
                        print(f"    {alg2}: {comparison.loc[alg2, 'search_time']:.3f}s, {comparison.loc[alg2, 'nodes_expanded']:.0f} nodes")

    def create_success_matrix(self):
        """Tạo ma trận thành công algorithm vs map"""
        # Tạo ma trận success
        success_matrix = pd.crosstab(
            self.df['algorithm'], 
            self.df['map'], 
            self.df['solution_found'], 
            aggfunc='max'  # Nếu có multiple runs, lấy max
        ).fillna(0).astype(int)
        
        print("\nMa trận thành công (1=tìm được lời giải, 0=không tìm được):")
        print(success_matrix.to_string())
        
        # Thống kê tổng kết
        print(f"\nTổng kết:")
        for alg in success_matrix.index:
            solved_count = success_matrix.loc[alg].sum()
            total_maps = len(success_matrix.columns)
            success_rate = solved_count / total_maps * 100
            print(f"  {alg}: {solved_count}/{total_maps} maps ({success_rate:.1f}%)")
        
        return success_matrix

    def calculate_fair_scores(self):
        """Tính điểm số công bằng cho các thuật toán"""
        algorithms = self.df['algorithm'].unique()
        maps = self.df['map'].unique()
        
        # Tạo ma trận điểm
        scores = pd.DataFrame(index=algorithms, columns=maps, dtype=float)
        
        for map_name in maps:
            map_data = self.df[self.df['map'] == map_name]
            
            # Chỉ tính điểm cho các thuật toán tìm được lời giải
            solved_data = map_data[map_data['solution_found'] == True]
            
            if not solved_data.empty:
                # Ranking theo thời gian (thuật toán nhanh nhất = điểm cao nhất)
                time_ranking = solved_data.set_index('algorithm')['search_time'].rank(ascending=True)
                max_rank = len(time_ranking)
                
                # Chuyển đổi rank thành điểm (rank 1 = điểm cao nhất)
                for alg in time_ranking.index:
                    scores.loc[alg, map_name] = max_rank - time_ranking[alg] + 1
            
            # Thuật toán không tìm được lời giải = 0 điểm
            unsolved_algs = map_data[map_data['solution_found'] == False]['algorithm'].unique()
            for alg in unsolved_algs:
                scores.loc[alg, map_name] = 0
        
        # Tính tổng điểm
        total_scores = scores.sum(axis=1, skipna=True).sort_values(ascending=False)
        
        print("Bảng xếp hạng tổng thể (dựa trên điểm ranking):")
        for i, (alg, score) in enumerate(total_scores.items(), 1):
            solved_count = (scores.loc[alg] > 0).sum()
            total_maps = len(maps)
            avg_score = score / total_maps if total_maps > 0 else 0
            print(f"  {i}. {alg}: {score:.1f} điểm ({solved_count}/{total_maps} maps, avg: {avg_score:.2f})")
        
        return scores, total_scores

    def create_fair_comparison_plots(self):
        """Tạo biểu đồ so sánh công bằng"""
        # 1. Success rate matrix heatmap
        plt.figure(figsize=(14, 8))
        
        # Tạo ma trận success rate
        success_matrix = pd.crosstab(
            self.df['algorithm'], 
            self.df['map'], 
            self.df['solution_found'], 
            aggfunc='max'
        ).fillna(0)
        
        sns.heatmap(success_matrix, annot=True, fmt='d', cmap='RdYlGn', 
                    center=0.5, vmin=0, vmax=1, cbar_kws={'label': 'Solution Found'})
        plt.title('Success Matrix: Algorithm vs Map', fontsize=16, fontweight='bold')
        plt.ylabel('Algorithm', fontsize=12)
        plt.xlabel('Map', fontsize=12)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'success_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Fair comparison nếu có common maps
        common_maps = self.get_common_solved_maps()
        if common_maps:
            fair_data = self.df[
                (self.df['map'].isin(common_maps)) & 
                (self.df['solution_found'] == True)
            ]
            
            if not fair_data.empty:
                fig, axes = plt.subplots(2, 2, figsize=(16, 12))
                
                metrics = ['search_time', 'memory_usage', 'nodes_expanded', 'solution_length']
                titles = ['Search Time (s)', 'Memory Usage (KB)', 'Nodes Expanded', 'Solution Length']
                colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral']
                
                for i, (metric, title, color) in enumerate(zip(metrics, titles, colors)):
                    ax = axes[i//2, i%2]
                    
                    # Box plot cho fair comparison
                    fair_data.boxplot(column=metric, by='algorithm', ax=ax)
                    ax.set_title(f'{title} - Fair Comparison\n({len(common_maps)} common maps)', fontsize=12)
                    ax.set_xlabel('Algorithm')
                    ax.set_ylabel(title)
                    
                    # Thêm mean values
                    means = fair_data.groupby('algorithm')[metric].mean()
                    for j, (alg, mean_val) in enumerate(means.items()):
                        ax.text(j+1, mean_val, f'{mean_val:.2f}', 
                               ha='center', va='bottom', fontweight='bold', color='red')
                
                plt.suptitle('Fair Performance Comparison\n(Only maps solved by ALL algorithms)', 
                            fontsize=16, fontweight='bold')
                plt.tight_layout()
                plt.savefig(self.output_dir / 'fair_comparison.png', dpi=300, bbox_inches='tight')
                plt.close()
        
        # 3. Success rate comparison
        plt.figure(figsize=(12, 6))
        
        success_rates = self.df.groupby('algorithm')['solution_found'].mean() * 100
        bars = plt.bar(success_rates.index, success_rates.values, 
                       color='skyblue', edgecolor='navy', alpha=0.7)
        
        plt.title('Algorithm Success Rate Comparison', fontsize=16, fontweight='bold')
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylabel('Success Rate (%)', fontsize=12)
        plt.ylim(0, 100)
        
        # Add value labels
        for bar, rate in zip(bars, success_rates.values):
            plt.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                    f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'success_rate_detailed.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Đã tạo biểu đồ so sánh công bằng:")
        print(f"  - {self.output_dir / 'success_matrix.png'}")
        print(f"  - {self.output_dir / 'success_rate_detailed.png'}")
        if common_maps:
            print(f"  - {self.output_dir / 'fair_comparison.png'}")
    
    def create_per_map_visualization(self):
        """Tạo biểu đồ so sánh hiệu suất từng map"""
        print(f"\nĐang tạo biểu đồ phân tích từng map...")
        
        maps = sorted(self.df['map'].unique())
        
        # 1. Heatmap performance matrix cho từng metric
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        metrics = ['search_time', 'memory_usage', 'nodes_expanded', 'solution_length']
        titles = ['Search Time (s)', 'Memory Usage (KB)', 'Nodes Expanded', 'Solution Length']
        
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[i//2, i%2]
            
            # Tạo pivot table
            pivot = self.df_solved.pivot_table(
                index='algorithm', 
                columns='map', 
                values=metric, 
                aggfunc='mean'
            )
            
            # Tạo heatmap
            sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlOrRd', 
                       ax=ax, cbar_kws={'label': title})
            ax.set_title(f'{title} by Algorithm and Map', fontsize=14, fontweight='bold')
            ax.set_xlabel('Map', fontsize=12)
            ax.set_ylabel('Algorithm', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'per_map_performance_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Theoretical compliance visualization
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        
        # Tạo matrix thành công cho mỗi map
        success_matrix = pd.crosstab(
            self.df['map'], 
            self.df['algorithm'], 
            self.df['solution_found'], 
            aggfunc='max'
        ).fillna(0)
        
        sns.heatmap(success_matrix, annot=True, fmt='d', cmap='RdYlGn', 
                   center=0.5, vmin=0, vmax=1, ax=ax)
        ax.set_title('Algorithm Success by Map\n(1=Success, 0=Failure)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Algorithm', fontsize=12)
        ax.set_ylabel('Map', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'algorithm_success_by_map.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Performance comparison radar chart cho từng map
        if len(maps) <= 6:  # Chỉ tạo nếu không quá nhiều maps
            fig, axes = plt.subplots(2, 3, figsize=(18, 12), subplot_kw=dict(projection='polar'))
            axes = axes.flatten()
            
            for i, map_name in enumerate(maps):
                if i >= 6:  # Giới hạn 6 maps
                    break
                    
                ax = axes[i]
                map_data = self.df_solved[self.df_solved['map'] == map_name]
                
                if not map_data.empty:
                    # Chuẩn bị dữ liệu cho radar chart
                    algorithms = map_data['algorithm'].unique()
                    angles = np.linspace(0, 2*np.pi, len(algorithms), endpoint=False)
                    
                    # Metrics để so sánh (normalize về 0-1)
                    metrics = ['search_time', 'memory_usage', 'nodes_expanded', 'solution_length']
                    
                    for metric in metrics:
                        values = []
                        for alg in algorithms:
                            alg_data = map_data[map_data['algorithm'] == alg]
                            values.append(alg_data[metric].mean())
                        
                        # Normalize (inverse cho performance metrics)
                        max_val = max(values)
                        if max_val > 0:
                            normalized = [(max_val - v) / max_val for v in values]
                        else:
                            normalized = values
                        
                        ax.plot(angles, normalized, 'o-', linewidth=2, label=metric)
                    
                    ax.set_xticks(angles)
                    ax.set_xticklabels(algorithms)
                    ax.set_title(f'{map_name}', fontsize=12, fontweight='bold')
                    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
            
            plt.tight_layout()
            plt.savefig(self.output_dir / 'per_map_radar_charts.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Time complexity analysis
        fig, ax = plt.subplots(1, 1, figsize=(14, 8))
        
        # So sánh thời gian vs số nodes cho mỗi thuật toán
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.df_solved['algorithm'].unique())))
        
        for i, alg in enumerate(sorted(self.df_solved['algorithm'].unique())):
            alg_data = self.df_solved[self.df_solved['algorithm'] == alg]
            
            ax.scatter(alg_data['nodes_expanded'], alg_data['search_time'], 
                      label=alg, alpha=0.7, s=60, color=colors[i])
        
        ax.set_xlabel('Nodes Expanded', fontsize=12)
        ax.set_ylabel('Search Time (s)', fontsize=12)
        ax.set_title('Time Complexity Analysis\n(Time vs Nodes Expanded)', fontsize=14, fontweight='bold')
        ax.legend()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'time_complexity_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Đã tạo biểu đồ phân tích từng map:")
        print(f"  - {self.output_dir / 'per_map_performance_heatmap.png'}")
        print(f"  - {self.output_dir / 'algorithm_success_by_map.png'}")
        print(f"  - {self.output_dir / 'time_complexity_analysis.png'}")
        if len(maps) <= 6:
            print(f"  - {self.output_dir / 'per_map_radar_charts.png'}")
    
    def generate_comprehensive_report(self):
        """Tạo báo cáo tổng hợp"""
        print("\n" + "="*80)
        print("BÁO CÁO TỔNG HỢP")
        print("="*80)
        
        # 1. Executive Summary
        print("\n1. TÓM TẮT ĐIỀU HÀNH:")
        print("-" * 40)
        
        total_experiments = len(self.df)
        total_maps = self.df['map'].nunique()
        total_algorithms = self.df['algorithm'].nunique()
        
        print(f"  - Tổng số thử nghiệm: {total_experiments}")
        print(f"  - Số maps: {total_maps}")
        print(f"  - Số thuật toán: {total_algorithms}")
        
        # Overall success rate
        overall_success = self.df['solution_found'].mean() * 100
        print(f"  - Tỷ lệ thành công tổng thể: {overall_success:.1f}%")
        
        # 2. Algorithm Ranking
        print("\n2. XẾP HẠNG THUẬT TOÁN:")
        print("-" * 40)
        
        # Tính composite score
        algorithm_scores = self.calculate_composite_scores()
        
        for i, (alg, score) in enumerate(algorithm_scores.items(), 1):
            print(f"  {i}. {alg}: {score:.2f} điểm")
        
        # 3. Recommendations
        print("\n3. KHUYẾN NGHỊ:")
        print("-" * 40)
        
        self.generate_recommendations(algorithm_scores)

    def calculate_composite_scores(self):
        """Tính điểm tổng hợp cho từng thuật toán"""
        algorithms = self.df['algorithm'].unique()
        composite_scores = {}
        
        for alg in algorithms:
            alg_data = self.df[self.df['algorithm'] == alg]
            
            # Các metric chính
            coverage_rate = alg_data['solution_found'].mean() * 100
            
            # Chỉ tính performance cho các cases đã giải được
            solved_data = alg_data[alg_data['solution_found'] == True]
            
            if not solved_data.empty:
                avg_time = solved_data['search_time'].mean()
                avg_memory = solved_data['memory_usage'].mean()
                avg_nodes = solved_data['nodes_expanded'].mean()
                avg_solution = solved_data['solution_length'].mean()
                
                # Normalize scores (0-100)
                # Coverage: trực tiếp là %
                coverage_score = coverage_rate
                
                # Time: inverse normalized
                max_time = self.df_solved['search_time'].max()
                time_score = (1 - avg_time / max_time) * 100 if max_time > 0 else 0
                
                # Memory: inverse normalized
                max_memory = self.df_solved['memory_usage'].max()
                memory_score = (1 - avg_memory / max_memory) * 100 if max_memory > 0 else 0
                
                # Nodes: inverse normalized
                max_nodes = self.df_solved['nodes_expanded'].max()
                nodes_score = (1 - avg_nodes / max_nodes) * 100 if max_nodes > 0 else 0
                
                # Solution quality: inverse normalized
                max_solution = self.df_solved['solution_length'].max()
                solution_score = (1 - avg_solution / max_solution) * 100 if max_solution > 0 else 0
                
                # Weighted composite score
                composite_score = (
                    coverage_score * 0.4 +  # Coverage quan trọng nhất
                    time_score * 0.25 +     # Thời gian
                    memory_score * 0.15 +   # Bộ nhớ
                    nodes_score * 0.1 +     # Nodes
                    solution_score * 0.1    # Chất lượng lời giải
                )
            else:
                composite_score = 0  # Không giải được gì
            
            composite_scores[alg] = composite_score
        
        # Sắp xếp theo điểm
        return dict(sorted(composite_scores.items(), key=lambda x: x[1], reverse=True))

    def generate_recommendations(self, algorithm_scores):
        """Tạo khuyến nghị dựa trên kết quả phân tích"""
        sorted_algorithms = list(algorithm_scores.keys())
        
        print("Dựa trên kết quả phân tích:")
        print()
        
        if len(sorted_algorithms) >= 1:
            best_alg = sorted_algorithms[0]
            print(f"🏆 THUẬT TOÁN TỐT NHẤT: {best_alg}")
            print(f"   - Điểm tổng hợp cao nhất: {algorithm_scores[best_alg]:.2f}")
            print(f"   - Khuyến nghị: Sử dụng cho hầu hết các bài toán")
        
        if len(sorted_algorithms) >= 2:
            second_alg = sorted_algorithms[1]
            print(f"🥈 THUẬT TOÁN THỨ HAI: {second_alg}")
            print(f"   - Điểm tổng hợp: {algorithm_scores[second_alg]:.2f}")
            print(f"   - Khuyến nghị: Lựa chọn thay thế tốt")
        
        if len(sorted_algorithms) >= 3:
            worst_alg = sorted_algorithms[-1]
            print(f"⚠️  THUẬT TOÁN CẦN CẢI THIỆN: {worst_alg}")
            print(f"   - Điểm tổng hợp thấp nhất: {algorithm_scores[worst_alg]:.2f}")
            print(f"   - Khuyến nghị: Cần tối ưu hóa hoặc hạn chế sử dụng")
        
        print()
        print("💡 KHUYẾN NGHỊ CHUNG:")
        print("   - Ưu tiên thuật toán có coverage rate cao")
        print("   - Cân nhắc trade-off giữa thời gian và chất lượng lời giải")
        print("   - Kiểm tra hiệu suất trên các loại bài toán khác nhau")
    
    def analyze_per_map_performance(self):
        """Phân tích hiệu suất từng map và so sánh với lý thuyết"""
        print("\n" + "="*80)
        print("PHÂN TÍCH HIỆU SUẤT TỪNG MAP - SO SÁNH VỚI LÝ THUYẾT")
        print("="*80)
        
        maps = sorted(self.df['map'].unique())
        algorithm_theoretical_properties = {
            'BFS': {'optimal': True, 'complete': True, 'memory_efficient': False},
            'DFS': {'optimal': False, 'complete': True, 'memory_efficient': True},
            'UCS': {'optimal': True, 'complete': True, 'memory_efficient': False},
            'A*': {'optimal': True, 'complete': True, 'memory_efficient': False, 'efficient': True},
            'IDS': {'optimal': True, 'complete': True, 'memory_efficient': True}
        }
        
        total_insights = []
        
        for map_name in maps:
            print(f"\n{'='*60}")
            print(f"MAP: {map_name}")
            print(f"{'='*60}")
            
            # Lấy dữ liệu cho map này
            map_data = self.df[self.df['map'] == map_name]
            map_solved = map_data[map_data['solution_found'] == True]
            
            # Tổng quan
            total_tested = len(map_data)
            total_solved = len(map_solved)
            success_rate = (total_solved / total_tested * 100) if total_tested > 0 else 0
            
            print(f"📊 TỔNG QUAN:")
            print(f"  - Số thuật toán test: {total_tested}")
            print(f"  - Số thuật toán giải được: {total_solved}")
            print(f"  - Tỷ lệ thành công: {success_rate:.1f}%")
            
            if map_solved.empty:
                print("  ⚠️  KHÔNG CÓ THUẬT TOÁN NÀO TÌM ĐƯỢC LỜI GIẢI!")
                continue
            
            # Phân tích hiệu suất của từng thuật toán
            print(f"\n📈 HIỆU SUẤT CỦA TỪNG THUẬT TOÁN:")
            algorithms_stats = {}
            
            for alg in sorted(map_solved['algorithm'].unique()):
                alg_data = map_solved[map_solved['algorithm'] == alg].iloc[0]
                
                stats = {
                    'search_time': alg_data['search_time'],
                    'memory_usage': alg_data['memory_usage'],
                    'nodes_expanded': alg_data['nodes_expanded'],
                    'solution_length': alg_data['solution_length']
                }
                algorithms_stats[alg] = stats
                
                print(f"  {alg}:")
                print(f"    ⏱️  Thời gian: {stats['search_time']:.3f}s")
                print(f"    💾 Bộ nhớ: {stats['memory_usage']:.1f}KB")
                print(f"    🔍 Nodes mở rộng: {stats['nodes_expanded']:.0f}")
                print(f"    📏 Độ dài lời giải: {stats['solution_length']:.0f}")
            
            # So sánh với lý thuyết
            print(f"\n🔬 SO SÁNH VỚI LÝ THUYẾT:")
            map_insights = self.analyze_theoretical_compliance(algorithms_stats, map_name)
            total_insights.extend(map_insights)
            
            # Rankings
            print(f"\n🏆 RANKINGS:")
            
            # Ranking theo thời gian
            time_ranking = sorted(algorithms_stats.items(), key=lambda x: x[1]['search_time'])
            print(f"  ⏱️  Nhanh nhất:")
            for i, (alg, stats) in enumerate(time_ranking[:3], 1):
                print(f"    {i}. {alg}: {stats['search_time']:.3f}s")
            
            # Ranking theo bộ nhớ
            memory_ranking = sorted(algorithms_stats.items(), key=lambda x: x[1]['memory_usage'])
            print(f"  💾 Tiết kiệm bộ nhớ nhất:")
            for i, (alg, stats) in enumerate(memory_ranking[:3], 1):
                print(f"    {i}. {alg}: {stats['memory_usage']:.1f}KB")
            
            # Ranking theo nodes
            nodes_ranking = sorted(algorithms_stats.items(), key=lambda x: x[1]['nodes_expanded'])
            print(f"  🔍 Hiệu quả nhất (ít nodes):")
            for i, (alg, stats) in enumerate(nodes_ranking[:3], 1):
                print(f"    {i}. {alg}: {stats['nodes_expanded']:.0f} nodes")
            
            # Ranking theo độ dài lời giải
            solution_ranking = sorted(algorithms_stats.items(), key=lambda x: x[1]['solution_length'])
            print(f"  📏 Lời giải tối ưu nhất:")
            for i, (alg, stats) in enumerate(solution_ranking[:3], 1):
                print(f"    {i}. {alg}: {stats['solution_length']:.0f} moves")
        
        # Tổng kết insights
        print(f"\n" + "="*80)
        print("TỔNG KẾT INSIGHTS TỪ PHÂN TÍCH")
        print("="*80)
        
        self.summarize_insights(total_insights)
        
        return total_insights
    
    def analyze_theoretical_compliance(self, algorithms_stats, map_name):
        """Phân tích tuân thủ lý thuyết cho một map"""
        insights = []
        
        print(f"  🔍 PHÂN TÍCH TUÂN THỦ LÝ THUYẾT:")
        
        # 1. Kiểm tra tính tối ưu
        optimal_algorithms = ['BFS', 'UCS', 'A*', 'IDS']
        optimal_present = [alg for alg in optimal_algorithms if alg in algorithms_stats]
        
        if len(optimal_present) > 1:
            solution_lengths = [algorithms_stats[alg]['solution_length'] for alg in optimal_present]
            min_length = min(solution_lengths)
            max_length = max(solution_lengths)
            
            if max_length - min_length <= 1:  # Cho phép sai số nhỏ
                print(f"    ✅ Tính tối ưu: ĐÚNG - Các thuật toán tối ưu đều tìm lời giải ~{min_length:.0f} moves")
                insights.append(f"{map_name}: Tính tối ưu được đảm bảo")
            else:
                print(f"    ❌ Tính tối ưu: SAI - Sự khác biệt lớn: {min_length:.0f} - {max_length:.0f} moves")
                insights.append(f"{map_name}: Có vấn đề về tính tối ưu")
        
        # 2. So sánh A* vs BFS (A* nên hiệu quả hơn)
        if 'A*' in algorithms_stats and 'BFS' in algorithms_stats:
            astar_nodes = algorithms_stats['A*']['nodes_expanded']
            bfs_nodes = algorithms_stats['BFS']['nodes_expanded']
            
            if astar_nodes < bfs_nodes:
                efficiency_gain = (bfs_nodes - astar_nodes) / bfs_nodes * 100
                print(f"    ✅ A* vs BFS: ĐÚNG - A* tiết kiệm {efficiency_gain:.1f}% nodes")
                insights.append(f"{map_name}: A* hiệu quả hơn BFS ({efficiency_gain:.1f}%)")
            else:
                print(f"    ❌ A* vs BFS: SAI - A* không hiệu quả hơn BFS")
                insights.append(f"{map_name}: A* không hiệu quả hơn BFS (có vấn đề)")
        
        # 3. Kiểm tra DFS tiết kiệm bộ nhớ
        if 'DFS' in algorithms_stats:
            dfs_memory = algorithms_stats['DFS']['memory_usage']
            other_memories = [stats['memory_usage'] for alg, stats in algorithms_stats.items() if alg != 'DFS']
            
            if other_memories and dfs_memory <= min(other_memories):
                print(f"    ✅ DFS memory: ĐÚNG - Tiết kiệm nhất ({dfs_memory:.1f}KB)")
                insights.append(f"{map_name}: DFS tiết kiệm bộ nhớ như lý thuyết")
            else:
                print(f"    ❌ DFS memory: SAI - Không tiết kiệm nhất")
                insights.append(f"{map_name}: DFS không tiết kiệm bộ nhớ như mong đợi")
        
        # 4. So sánh UCS vs BFS (khi cost = 1, nên tương đương)
        if 'UCS' in algorithms_stats and 'BFS' in algorithms_stats:
            ucs_solution = algorithms_stats['UCS']['solution_length']
            bfs_solution = algorithms_stats['BFS']['solution_length']
            
            if abs(ucs_solution - bfs_solution) <= 1:
                print(f"    ✅ UCS vs BFS: ĐÚNG - Tương đương về lời giải")
                insights.append(f"{map_name}: UCS và BFS tương đương như lý thuyết")
            else:
                print(f"    ❌ UCS vs BFS: SAI - Khác biệt lớn về lời giải")
                insights.append(f"{map_name}: UCS và BFS không tương đương")
        
        # 5. Phân tích thời gian chạy
        if len(algorithms_stats) > 1:
            times = [(alg, stats['search_time']) for alg, stats in algorithms_stats.items()]
            times.sort(key=lambda x: x[1])
            
            fastest = times[0]
            slowest = times[-1]
            
            print(f"    📊 Thời gian: {fastest[0]} nhanh nhất ({fastest[1]:.3f}s), {slowest[0]} chậm nhất ({slowest[1]:.3f}s)")
            
            # Kiểm tra xem DFS có thể nhanh hơn BFS trong trường hợp may mắn
            if 'DFS' in algorithms_stats and 'BFS' in algorithms_stats:
                dfs_time = algorithms_stats['DFS']['search_time']
                bfs_time = algorithms_stats['BFS']['search_time']
                
                if dfs_time < bfs_time:
                    insights.append(f"{map_name}: DFS may mắn - nhanh hơn BFS")
                else:
                    insights.append(f"{map_name}: BFS ổn định hơn DFS về thời gian")
        
        return insights
    
    def summarize_insights(self, insights):
        """Tổng kết insights từ tất cả các maps"""
        print("🔍 INSIGHTS TỔNG QUÁT:")
        
        # Phân loại insights
        optimal_issues = [i for i in insights if 'tối ưu' in i.lower()]
        efficiency_insights = [i for i in insights if 'hiệu quả' in i.lower()]
        memory_insights = [i for i in insights if 'bộ nhớ' in i.lower()]
        stability_insights = [i for i in insights if 'ổn định' in i.lower() or 'may mắn' in i.lower()]
        
        if optimal_issues:
            print(f"\n  🎯 VỀ TÍNH TỐI ƯU:")
            for insight in optimal_issues[:5]:  # Hiển thị top 5
                print(f"    - {insight}")
        
        if efficiency_insights:
            print(f"\n  ⚡ VỀ HIỆU SUẤT:")
            for insight in efficiency_insights[:5]:
                print(f"    - {insight}")
        
        if memory_insights:
            print(f"\n  💾 VỀ BỘ NHỚ:")
            for insight in memory_insights[:5]:
                print(f"    - {insight}")
        
        if stability_insights:
            print(f"\n  🎲 VỀ TÍNH ỔN ĐỊNH:")
            for insight in stability_insights[:5]:
                print(f"    - {insight}")
        
        # Thống kê tổng quan
        print(f"\n📈 THỐNG KÊ:")
        print(f"  - Tổng số insights: {len(insights)}")
        print(f"  - Insights về tối ưu: {len(optimal_issues)}")
        print(f"  - Insights về hiệu suất: {len(efficiency_insights)}")
        print(f"  - Insights về bộ nhớ: {len(memory_insights)}")
        print(f"  - Insights về tính ổn định: {len(stability_insights)}")
        
        # Khuyến nghị
        print(f"\n💡 KHUYẾN NGHỊ:")
        
        # Dựa trên insights để đưa ra khuyến nghị
        astar_good = len([i for i in insights if 'A*' in i and 'hiệu quả' in i])
        dfs_memory_good = len([i for i in insights if 'DFS' in i and 'tiết kiệm bộ nhớ' in i])
        
        if astar_good > len(insights) * 0.3:
            print("  ✅ A* thể hiện hiệu quả như lý thuyết - Khuyến nghị sử dụng")
        
        if dfs_memory_good > len(insights) * 0.3:
            print("  ✅ DFS tiết kiệm bộ nhớ như lý thuyết - Tốt cho môi trường hạn chế")
        
        print("  📊 Kết quả cho thấy các thuật toán hoạt động khá phù hợp với lý thuyết")

def main():
    """Chương trình chính"""
    analyzer = ResultAnalyzer()
    
    try:
        # Load dữ liệu
        analyzer.load_data()
        
        # Thực hiện các phân tích
        analyzer.analyze_success_rates()
        analyzer.analyze_performance_for_solved()
        
        # PHÂN TÍCH HIỆU SUẤT TỪNG MAP - SO SÁNH VỚI LÝ THUYẾT
        analyzer.analyze_per_map_performance()
        
        # PHÂN TÍCH CÔNG BẰNG MỚI
        analyzer.analyze_fair_comparison()
        
        analyzer.analyze_map_difficulty()
        analyzer.compare_algorithms_by_map()
        
        # Tạo biểu đồ
        print(f"\nĐang tạo biểu đồ...")
        analyzer.create_visualizations()
        
        # Tạo biểu đồ so sánh công bằng
        print(f"\nĐang tạo biểu đồ so sánh công bằng...")
        analyzer.create_fair_comparison_plots()
        
        # Tạo biểu đồ phân tích từng map
        print(f"\nĐang tạo biểu đồ phân tích từng map...")
        analyzer.create_per_map_visualization()
        
        # Báo cáo tổng kết
        analyzer.generate_summary_report()
        
        # Biểu đồ phân tích từng map
        analyzer.create_per_map_visualization()
        
        print(f"\nHoàn thành phân tích! Các file đã được lưu tại: {analyzer.output_dir}")
        
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
