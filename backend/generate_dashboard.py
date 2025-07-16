#!/usr/bin/env python3
"""
Generate evaluation dashboard from results JSON
Creates an accurate, dynamic dashboard that loads real evaluation data
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def find_latest_results_file() -> str:
    """Find the most recent evaluation results JSON file"""
    backend_dir = Path(__file__).parent
    
    # Look for evaluation results files
    results_files = list(backend_dir.glob("evaluation_results_*_summary.json"))
    
    if not results_files:
        raise FileNotFoundError("No evaluation results files found. Run evaluations first.")
    
    # Sort by modification time and get the latest
    latest_file = max(results_files, key=lambda f: f.stat().st_mtime)
    return str(latest_file)

def load_evaluation_data(results_file: str) -> Dict[str, Any]:
    """Load evaluation data from JSON file"""
    with open(results_file, 'r') as f:
        return json.load(f)

def generate_dashboard_html(evaluation_data: Dict[str, Any], results_filename: str) -> str:
    """Generate complete dashboard HTML with embedded data"""
    
    metadata = evaluation_data['metadata']
    metrics = evaluation_data['aggregate_metrics']
    
    # Extract data for JavaScript embedding
    food_detection = metrics['food_detection']
    protein_estimation = metrics['protein_estimation'] 
    conversational_quality = metrics['conversational_quality']
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Protein Tracker Evaluation Dashboard</title>
    <style>
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .metric-card h3 {{
            color: #667eea;
            font-size: 1.3rem;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        .section {{
            background: white;
            margin-bottom: 30px;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #333;
            font-size: 1.8rem;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .charts-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }}
        
        .chart-container {{
            height: 300px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .metric-item {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .metric-item .label {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .metric-item .value {{
            font-size: 1.5rem;
            color: #333;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 30px;
        }}
        
        .status-good {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-danger {{ color: #dc3545; }}
        
        .data-source {{
            background: #e7f3ff;
            color: #0066cc;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 0.9rem;
        }}
        
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        
        <div class="header">
            <h1>🥗 Protein Tracker Evaluation Dashboard</h1>
            <p>Evaluation completed on {datetime.fromisoformat(metadata['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')} | {metadata['total_cases_evaluated']} total test cases</p>
        </div>
        
        <div class="data-source">
            📊 <strong>Data Source:</strong> {os.path.basename(results_filename)} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <div class="overview">
            <div class="metric-card">
                <h3>Food Detection</h3>
                <div class="metric-value">{food_detection['ground_truth_metrics']['avg_f1_score']:.3f}</div>
                <div class="metric-label">Average F1 Score</div>
            </div>
            <div class="metric-card">
                <h3>Protein Estimation</h3>
                <div class="metric-value">{protein_estimation['error_metrics']['mean_absolute_error']:.2f}g</div>
                <div class="metric-label">Mean Absolute Error</div>
            </div>
            <div class="metric-card">
                <h3>Response Quality</h3>
                <div class="metric-value">{conversational_quality['criteria_analysis']['avg_criteria_score']:.3f}</div>
                <div class="metric-label">Criteria Score</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🍽️ Food Detection Accuracy</h2>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="label">Precision</div>
                    <div class="value">{food_detection['ground_truth_metrics']['avg_precision']:.3f}</div>
                </div>
                <div class="metric-item">
                    <div class="label">Recall</div>
                    <div class="value">{food_detection['ground_truth_metrics']['avg_recall']:.3f}</div>
                </div>
                <div class="metric-item">
                    <div class="label">F1 Score</div>
                    <div class="value">{food_detection['ground_truth_metrics']['avg_f1_score']:.3f}</div>
                </div>
                <div class="metric-item">
                    <div class="label">Total Cases</div>
                    <div class="value">{food_detection['total_cases']}</div>
                </div>
            </div>
            <div class="charts-container">
                <div class="chart-container">
                    <canvas id="foodDetectionChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>💪 Protein Estimation Accuracy</h2>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="label">Mean Absolute Error</div>
                    <div class="value">{protein_estimation['error_metrics']['mean_absolute_error']:.2f}g</div>
                </div>
                <div class="metric-item">
                    <div class="label">Median Error</div>
                    <div class="value">{protein_estimation['error_metrics']['median_absolute_error']:.2f}g</div>
                </div>
                <div class="metric-item">
                    <div class="label">Within ±5g</div>
                    <div class="value">{protein_estimation['threshold_accuracy']['within_5g_pct']*100:.1f}%</div>
                </div>
                <div class="metric-item">
                    <div class="label">Within ±10g</div>
                    <div class="value">{protein_estimation['threshold_accuracy']['within_10g_pct']*100:.1f}%</div>
                </div>
            </div>
            <div class="charts-container">
                <div class="chart-container">
                    <canvas id="proteinAccuracyChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="proteinThresholdChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>💬 Conversational Response Quality</h2>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="label">Avg Criteria Score</div>
                    <div class="value">{conversational_quality['criteria_analysis']['avg_criteria_score']:.3f}</div>
                </div>
                <div class="metric-item">
                    <div class="label">Median Criteria Score</div>
                    <div class="value">{conversational_quality['criteria_analysis']['median_criteria_score']:.3f}</div>
                </div>
                <div class="metric-item">
                    <div class="label">Total Cases</div>
                    <div class="value">{conversational_quality.get('total_cases', food_detection['total_cases'])}</div>
                </div>
            </div>
            <div class="charts-container">
                <div class="chart-container">
                    <canvas id="helpfulnessChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="accuracyChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="toneChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="completenessChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p>Protein Tracker Evaluation Framework</p>
        </div>
        
    </div>
    
    <script>
        // Embedded evaluation data
        const evaluationData = {json.dumps(evaluation_data, indent=8)};
        
        // Color schemes for charts
        const colors = {{
            primary: ["#28a745", "#17a2b8", "#ffc107", "#fd7e14", "#dc3545"],
            success: ["#28a745", "#20c997", "#6610f2"],
            warning: ["#ffc107", "#fd7e14", "#e83e8c"],
            info: ["#17a2b8", "#6f42c1", "#20c997"]
        }};
        
        // Chart configuration
        Chart.defaults.plugins.legend.position = 'bottom';
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        
        function createDoughnutChart(elementId, data, title, colorScheme = colors.primary) {{
            const labels = Object.keys(data);
            const values = Object.values(data);
            
            new Chart(document.getElementById(elementId), {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: values,
                        backgroundColor: colorScheme.slice(0, labels.length)
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: title
                        }}
                    }}
                }}
            }});
        }}
        
        function createBarChart(elementId, labels, values, title, colorScheme = colors.info) {{
            new Chart(document.getElementById(elementId), {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Accuracy %',
                        data: values,
                        backgroundColor: colorScheme
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: title
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Render all charts when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            const metrics = evaluationData.aggregate_metrics;
            
            // Food Detection Chart
            createDoughnutChart(
                'foodDetectionChart', 
                metrics.food_detection.llm_evaluation_distribution,
                'LLM Judge - Food Detection Categories'
            );
            
            // Protein Accuracy Chart
            createDoughnutChart(
                'proteinAccuracyChart', 
                metrics.protein_estimation.accuracy_distribution,
                'Protein Estimation Accuracy Categories',
                colors.success
            );
            
            // Protein Threshold Chart
            const thresholds = metrics.protein_estimation.threshold_accuracy;
            createBarChart(
                'proteinThresholdChart',
                ['Within ±5g', 'Within ±10g', 'Within ±15g'],
                [thresholds.within_5g_pct * 100, thresholds.within_10g_pct * 100, thresholds.within_15g_pct * 100],
                'Protein Estimation - Threshold Accuracy'
            );
            
            // Conversational Quality Charts
            const conversational = metrics.conversational_quality.llm_evaluation_distributions;
            const chartConfigs = [
                {{ id: 'helpfulnessChart', data: 'helpfulness', colors: colors.success }},
                {{ id: 'accuracyChart', data: 'accuracy', colors: colors.primary }},
                {{ id: 'toneChart', data: 'tone', colors: colors.warning }},
                {{ id: 'completenessChart', data: 'completeness', colors: colors.info }}
            ];
            
            chartConfigs.forEach(config => {{
                if (conversational[config.data]) {{
                    createDoughnutChart(
                        config.id,
                        conversational[config.data],
                        config.data.charAt(0).toUpperCase() + config.data.slice(1) + ' Distribution',
                        config.colors
                    );
                }}
            }});
        }});
        
    </script>
</body>
</html>"""
    
    return html_template

def main():
    """Generate dashboard from latest evaluation results"""
    try:
        print("🎯 Generating Evaluation Dashboard")
        print("=" * 40)
        
        # Find latest results file
        results_file = find_latest_results_file()
        print(f"📊 Using results: {os.path.basename(results_file)}")
        
        # Load evaluation data
        evaluation_data = load_evaluation_data(results_file)
        print(f"✅ Loaded {evaluation_data['metadata']['total_cases_evaluated']} test cases")
        
        # Generate dashboard HTML
        dashboard_html = generate_dashboard_html(evaluation_data, results_file)
        
        # Save dashboard
        output_file = "evaluation_dashboard_current.html"
        with open(output_file, 'w') as f:
            f.write(dashboard_html)
        
        print(f"✅ Dashboard generated: {output_file}")
        print(f"🌐 Open file://{os.path.abspath(output_file)} in your browser")
        print()
        print("🎉 Dashboard Features:")
        print("   ✅ Dynamic data loading from JSON")
        print("   ✅ Accurate conversational quality charts") 
        print("   ✅ Real-time data source tracking")
        print("   ✅ Proper color coding and formatting")
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())