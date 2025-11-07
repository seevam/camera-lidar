#!/usr/bin/env python3
"""
Comparative Analysis: Camera vs LiDAR Performance
Analyzes data from both systems under different light conditions
Generates metrics and visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import glob
import json
from datetime import datetime

class PerformanceAnalyzer:
    def __init__(self, data_dir='data/raw', output_dir='data/analysis'):
        """
        Initialize analyzer
        
        Args:
            data_dir: Directory containing raw CSV files
            output_dir: Directory to save analysis results
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Results storage
        self.results = {
            'camera': {},
            'lidar': {}
        }
        
    def load_data(self, sensor_type, light_condition):
        """
        Load data files for specific sensor and light condition
        
        Args:
            sensor_type: 'camera' or 'lidar'
            light_condition: 'bright', 'medium', or 'low'
        
        Returns:
            DataFrame with combined data
        """
        # Find matching files
        pattern = f"{sensor_type}_{light_condition}_*.csv"
        files = list(self.data_dir.glob(pattern))
        
        if not files:
            print(f"Warning: No files found for {sensor_type} - {light_condition}")
            return None
        
        print(f"Found {len(files)} file(s) for {sensor_type} - {light_condition}")
        
        # Load and combine all files
        dfs = []
        for file in files:
            try:
                df = pd.read_csv(file)
                df['file'] = file.name
                dfs.append(df)
            except Exception as e:
                print(f"Error loading {file}: {e}")
        
        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            return combined
        return None
    
    def calculate_metrics(self, df):
        """
        Calculate performance metrics from data
        
        Args:
            df: DataFrame with columns: timestamp, deviation_mm, cumulative_collisions
        
        Returns:
            Dictionary with metrics
        """
        if df is None or len(df) == 0:
            return None
        
        # Convert deviation to cm
        df['deviation_cm'] = df['deviation_mm'] / 10.0
        
        # Calculate RMSE (Root Mean Square Error)
        rmse = np.sqrt(np.mean(df['deviation_cm'] ** 2))
        
        # Mean absolute deviation
        mad = np.mean(np.abs(df['deviation_cm']))
        
        # Standard deviation
        std_dev = np.std(df['deviation_cm'])
        
        # Total collisions (max of cumulative)
        total_collisions = int(df['cumulative_collisions'].max())
        
        # Estimate displacement per collision (if available)
        # Assuming 20cm max displacement
        avg_displacement = 10.0  # Default estimate in cm
        
        # Calculate normalized scores (0-100, lower is better)
        pds = min(100, (rmse / 10) * 100)  # Path Deviation Score
        ocs = min(100, (total_collisions / 10) * 100)  # Obstacle Collision Score
        ods = min(100, (avg_displacement / 20) * 100)  # Obstacle Displacement Score
        
        # Composite Performance Score (CPS)
        cps = 0.4 * pds + 0.35 * ocs + 0.25 * ods
        
        metrics = {
            'rmse_cm': round(rmse, 2),
            'mad_cm': round(mad, 2),
            'std_dev_cm': round(std_dev, 2),
            'max_deviation_cm': round(df['deviation_cm'].abs().max(), 2),
            'total_collisions': total_collisions,
            'avg_displacement_cm': avg_displacement,
            'pds': round(pds, 2),
            'ocs': round(ocs, 2),
            'ods': round(ods, 2),
            'cps': round(cps, 2),
            'data_points': len(df)
        }
        
        return metrics
    
    def analyze_all(self):
        """Analyze all combinations of sensors and light conditions"""
        conditions = ['bright', 'medium', 'low']
        sensors = ['camera', 'lidar']
        
        print("\n" + "="*60)
        print("COMPARATIVE PERFORMANCE ANALYSIS")
        print("="*60 + "\n")
        
        for sensor in sensors:
            self.results[sensor] = {}
            
            for condition in conditions:
                print(f"Analyzing {sensor.upper()} - {condition.upper()}...")
                
                # Load data
                df = self.load_data(sensor, condition)
                
                # Calculate metrics
                metrics = self.calculate_metrics(df)
                
                if metrics:
                    self.results[sensor][condition] = metrics
                    print(f"  ✓ Complete - CPS: {metrics['cps']}")
                else:
                    print(f"  ✗ No data available")
                    self.results[sensor][condition] = None
                
                print()
        
        return self.results
    
    def create_comparison_table(self):
        """Create comparison table of all metrics"""
        conditions = ['bright', 'medium', 'low']
        
        # Create DataFrame for comparison
        rows = []
        
        for condition in conditions:
            for sensor in ['camera', 'lidar']:
                metrics = self.results[sensor].get(condition)
                if metrics:
                    row = {
                        'Sensor': sensor.upper(),
                        'Light': condition.capitalize(),
                        'RMSE (cm)': metrics['rmse_cm'],
                        'MAD (cm)': metrics['mad_cm'],
                        'Collisions': metrics['total_collisions'],
                        'PDS': metrics['pds'],
                        'OCS': metrics['ocs'],
                        'ODS': metrics['ods'],
                        'CPS': metrics['cps']
                    }
                    rows.append(row)
        
        comparison_df = pd.DataFrame(rows)
        
        # Save to CSV
        output_file = self.output_dir / 'comparison_table.csv'
        comparison_df.to_csv(output_file, index=False)
        print(f"\nComparison table saved to: {output_file}")
        
        # Print to console
        print("\n" + "="*80)
        print("COMPARISON TABLE")
        print("="*80)
        print(comparison_df.to_string(index=False))
        print("="*80 + "\n")
        
        return comparison_df
    
    def plot_results(self):
        """Generate visualizations"""
        conditions = ['bright', 'medium', 'low']
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (15, 10)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Camera vs LiDAR Performance Comparison', 
                     fontsize=16, fontweight='bold')
        
        # Prepare data for plotting
        plot_data = {
            'CPS': {'camera': [], 'lidar': []},
            'PDS': {'camera': [], 'lidar': []},
            'OCS': {'camera': [], 'lidar': []},
            'Collisions': {'camera': [], 'lidar': []}
        }
        
        for condition in conditions:
            for sensor in ['camera', 'lidar']:
                metrics = self.results[sensor].get(condition)
                if metrics:
                    plot_data['CPS'][sensor].append(metrics['cps'])
                    plot_data['PDS'][sensor].append(metrics['pds'])
                    plot_data['OCS'][sensor].append(metrics['ocs'])
                    plot_data['Collisions'][sensor].append(metrics['total_collisions'])
                else:
                    plot_data['CPS'][sensor].append(0)
                    plot_data['PDS'][sensor].append(0)
                    plot_data['OCS'][sensor].append(0)
                    plot_data['Collisions'][sensor].append(0)
        
        # Plot 1: Composite Performance Score (CPS)
        x = np.arange(len(conditions))
        width = 0.35
        
        axes[0, 0].bar(x - width/2, plot_data['CPS']['camera'], width, 
                      label='Camera', alpha=0.8, color='#3498db')
        axes[0, 0].bar(x + width/2, plot_data['CPS']['lidar'], width, 
                      label='LiDAR', alpha=0.8, color='#e74c3c')
        axes[0, 0].set_xlabel('Light Condition')
        axes[0, 0].set_ylabel('Score (Lower is Better)')
        axes[0, 0].set_title('Composite Performance Score (CPS)')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels([c.capitalize() for c in conditions])
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Path Deviation Score (PDS)
        axes[0, 1].bar(x - width/2, plot_data['PDS']['camera'], width, 
                      label='Camera', alpha=0.8, color='#3498db')
        axes[0, 1].bar(x + width/2, plot_data['PDS']['lidar'], width, 
                      label='LiDAR', alpha=0.8, color='#e74c3c')
        axes[0, 1].set_xlabel('Light Condition')
        axes[0, 1].set_ylabel('Score (Lower is Better)')
        axes[0, 1].set_title('Path Deviation Score (PDS)')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels([c.capitalize() for c in conditions])
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Obstacle Collision Score (OCS)
        axes[1, 0].bar(x - width/2, plot_data['OCS']['camera'], width, 
                      label='Camera', alpha=0.8, color='#3498db')
        axes[1, 0].bar(x + width/2, plot_data['OCS']['lidar'], width, 
                      label='LiDAR', alpha=0.8, color='#e74c3c')
        axes[1, 0].set_xlabel('Light Condition')
        axes[1, 0].set_ylabel('Score (Lower is Better)')
        axes[1, 0].set_title('Obstacle Collision Score (OCS)')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels([c.capitalize() for c in conditions])
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Total Collisions
        axes[1, 1].bar(x - width/2, plot_data['Collisions']['camera'], width, 
                      label='Camera', alpha=0.8, color='#3498db')
        axes[1, 1].bar(x + width/2, plot_data['Collisions']['lidar'], width, 
                      label='LiDAR', alpha=0.8, color='#e74c3c')
        axes[1, 1].set_xlabel('Light Condition')
        axes[1, 1].set_ylabel('Number of Collisions')
        axes[1, 1].set_title('Total Collisions')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels([c.capitalize() for c in conditions])
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        output_file = self.output_dir / 'performance_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to: {output_file}")
        
        plt.show()
    
    def generate_report(self):
        """Generate text report with analysis"""
        report_file = self.output_dir / 'analysis_report.txt'
        
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("CAMERA VS LIDAR PERFORMANCE ANALYSIS REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("RESEARCH OBJECTIVES:\n")
            f.write("-" * 80 + "\n")
            f.write("1. Investigate AV performance under different light conditions\n")
            f.write("2. Compare Camera-based (Tesla) vs LiDAR-based (Waymo) approaches\n")
            f.write("3. Evaluate under: Bright, Medium, and Low light conditions\n\n")
            
            conditions = ['bright', 'medium', 'low']
            
            for condition in conditions:
                f.write("\n" + "="*80 + "\n")
                f.write(f"CONDITION: {condition.upper()} LIGHT\n")
                f.write("="*80 + "\n\n")
                
                for sensor in ['camera', 'lidar']:
                    metrics = self.results[sensor].get(condition)
                    
                    f.write(f"{sensor.upper()} System:\n")
                    f.write("-" * 40 + "\n")
                    
                    if metrics:
                        f.write(f"  Path Deviation (RMSE):     {metrics['rmse_cm']} cm\n")
                        f.write(f"  Mean Absolute Deviation:   {metrics['mad_cm']} cm\n")
                        f.write(f"  Standard Deviation:        {metrics['std_dev_cm']} cm\n")
                        f.write(f"  Total Collisions:          {metrics['total_collisions']}\n")
                        f.write(f"  \n")
                        f.write(f"  Scores (0-100, lower is better):\n")
                        f.write(f"    - Path Deviation Score (PDS):      {metrics['pds']}\n")
                        f.write(f"    - Obstacle Collision Score (OCS):  {metrics['ocs']}\n")
                        f.write(f"    - Obstacle Displacement Score (ODS): {metrics['ods']}\n")
                        f.write(f"    - Composite Performance Score (CPS): {metrics['cps']}\n")
                    else:
                        f.write("  No data available\n")
                    
                    f.write("\n")
            
            # Overall comparison
            f.write("\n" + "="*80 + "\n")
            f.write("OVERALL COMPARISON\n")
            f.write("="*80 + "\n\n")
            
            # Calculate averages
            for sensor in ['camera', 'lidar']:
                f.write(f"{sensor.upper()} Average CPS: ")
                cps_values = [
                    self.results[sensor][c]['cps'] 
                    for c in conditions 
                    if self.results[sensor].get(c)
                ]
                if cps_values:
                    f.write(f"{np.mean(cps_values):.2f}\n")
                else:
                    f.write("N/A\n")
            
            f.write("\n")
            f.write("KEY FINDINGS:\n")
            f.write("-" * 80 + "\n")
            f.write("1. Light Dependency:\n")
            f.write("   - Camera: [Expected to degrade in low light]\n")
            f.write("   - LiDAR: [Expected to maintain consistent performance]\n\n")
            
            f.write("2. Path Following Accuracy:\n")
            f.write("   - Compare RMSE values across conditions\n\n")
            
            f.write("3. Obstacle Avoidance:\n")
            f.write("   - Compare collision counts\n\n")
            
            f.write("4. Overall Winner:\n")
            f.write("   - Based on CPS scores\n\n")
            
            f.write("="*80 + "\n")
        
        print(f"Report saved to: {report_file}")
    
    def save_results_json(self):
        """Save results to JSON for further processing"""
        output_file = self.output_dir / 'results.json'
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results JSON saved to: {output_file}")

def main():
    print("\n" + "="*60)
    print("CAMERA vs LIDAR PERFORMANCE ANALYZER")
    print("="*60 + "\n")
    
    # Create analyzer
    analyzer = PerformanceAnalyzer()
    
    # Run analysis
    analyzer.analyze_all()
    
    # Generate outputs
    print("\nGenerating outputs...")
    analyzer.create_comparison_table()
    analyzer.plot_results()
    analyzer.generate_report()
    analyzer.save_results_json()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60 + "\n")
    print("Check the 'data/analysis' directory for:")
    print("  - comparison_table.csv")
    print("  - performance_comparison.png")
    print("  - analysis_report.txt")
    print("  - results.json")
    print()

if __name__ == "__main__":
    main()
