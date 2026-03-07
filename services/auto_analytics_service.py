"""
Auto Analytics Service
Generates automatic KPIs, statistics, and visualizations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any

def detect_column_types(df):
    """
    Detect and categorize column types for analytics
    
    Returns:
        dict with 'numeric', 'categorical', 'date' lists
    """
    numeric_cols = []
    categorical_cols = []
    date_cols = []
    
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        else:
            # Categorical if less than 20 unique values
            if df[col].nunique() < 20:
                categorical_cols.append(col)
    
    return {
        'numeric': numeric_cols,
        'categorical': categorical_cols,
        'date': date_cols
    }

def generate_summary_stats(df):
    """
    Generate summary statistics for the dataset
    
    Returns:
        dict with key metrics
    """
    col_types = detect_column_types(df)
    
    # Basic stats
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': len(col_types['numeric']),
        'categorical_columns': len(col_types['categorical']),
        'date_columns': len(col_types['date']),
    }
    
    # Additional stats
    stats['memory_usage_mb'] = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    stats['missing_values'] = int(df.isnull().sum().sum())
    stats['duplicate_rows'] = int(df.duplicated().sum())
    stats['missing_percentage'] = round((stats['missing_values'] / (len(df) * len(df.columns)) * 100), 2)
    
    # Data quality score (0-100)
    quality_score = 100
    if stats['missing_values'] > 0:
        quality_score -= min(stats['missing_percentage'] * 2, 40)
    if stats['duplicate_rows'] > 0:
        dup_percentage = (stats['duplicate_rows'] / len(df)) * 100
        quality_score -= min(dup_percentage * 1.5, 30)
    stats['data_quality_score'] = max(0, round(quality_score, 1))
    
    # Add numeric column stats
    numeric_stats = {}
    for col in col_types['numeric']:
        numeric_stats[col] = {
            'total': float(df[col].sum()),
            'average': float(df[col].mean()),
            'median': float(df[col].median()),
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'std': float(df[col].std())
        }
    
    stats['numeric_stats'] = numeric_stats
    
    # Add categorical counts
    categorical_stats = {}
    for col in col_types['categorical']:
        value_counts = df[col].value_counts().to_dict()
        categorical_stats[col] = {
            'unique_values': df[col].nunique(),
            'top_values': dict(list(value_counts.items())[:5])
        }
    
    stats['categorical_stats'] = categorical_stats
    
    return stats

def create_auto_charts(df):
    """
    Create automatic chart configurations based on data
    
    Returns:
        list of chart configurations for Chart.js
    """
    col_types = detect_column_types(df)
    charts = []
    
    # Chart 1: Count by first categorical column (Bar Chart)
    if col_types['categorical']:
        cat_col = col_types['categorical'][0]
        value_counts = df[cat_col].value_counts().head(10)
        
        charts.append({
            'type': 'bar',
            'title': f'Count by {cat_col.replace("_", " ").title()}',
            'data': {
                'labels': value_counts.index.tolist(),
                'datasets': [{
                    'label': 'Count',
                    'data': value_counts.values.tolist(),
                    'backgroundColor': 'rgba(99, 102, 241, 0.6)',
                    'borderColor': 'rgba(99, 102, 241, 1)',
                    'borderWidth': 2
                }]
            }
        })
    
    # Chart 2: Sum/Average of first numeric column by category (if both exist)
    if col_types['numeric'] and col_types['categorical']:
        num_col = col_types['numeric'][0]
        cat_col = col_types['categorical'][0]
        
        grouped = df.groupby(cat_col)[num_col].sum().head(10)
        
        charts.append({
            'type': 'bar',
            'title': f'Total {num_col.replace("_", " ").title()} by {cat_col.replace("_", " ").title()}',
            'data': {
                'labels': grouped.index.tolist(),
                'datasets': [{
                    'label': num_col.replace("_", " ").title(),
                    'data': grouped.values.tolist(),
                    'backgroundColor': 'rgba(16, 185, 129, 0.6)',
                    'borderColor': 'rgba(16, 185, 129, 1)',
                    'borderWidth': 2
                }]
            }
        })
    
    # Chart 3: Trend over time (if date column exists)
    if col_types['date'] and col_types['numeric']:
        date_col = col_types['date'][0]
        num_col = col_types['numeric'][0]
        
        # Sort by date and aggregate
        df_sorted = df.sort_values(date_col)
        trend_data = df_sorted.groupby(df_sorted[date_col].dt.to_period('M'))[num_col].sum()
        
        charts.append({
            'type': 'line',
            'title': f'{num_col.replace("_", " ").title()} Trend Over Time',
            'data': {
                'labels': [str(x) for x in trend_data.index.tolist()],
                'datasets': [{
                    'label': num_col.replace("_", " ").title(),
                    'data': trend_data.values.tolist(),
                    'borderColor': 'rgba(239, 68, 68, 1)',
                    'backgroundColor': 'rgba(239, 68, 68, 0.1)',
                    'borderWidth': 2,
                    'tension': 0.4
                }]
            }
        })
    
    # Chart 4: Distribution of first numeric column (if numeric exists)
    if col_types['numeric']:
        num_col = col_types['numeric'][0]
        
        # Create histogram bins
        hist, bins = np.histogram(df[num_col].dropna(), bins=10)
        
        charts.append({
            'type': 'bar',
            'title': f'Distribution of {num_col.replace("_", " ").title()}',
            'data': {
                'labels': [f'{int(bins[i])}-{int(bins[i+1])}' for i in range(len(bins)-1)],
                'datasets': [{
                    'label': 'Frequency',
                    'data': hist.tolist(),
                    'backgroundColor': 'rgba(251, 146, 60, 0.6)',
                    'borderColor': 'rgba(251, 146, 60, 1)',
                    'borderWidth': 2
                }]
            }
        })
    
    # Chart 5: Pie chart for categorical distribution
    if col_types['categorical']:
        cat_col = col_types['categorical'][0]
        value_counts = df[cat_col].value_counts().head(6)
        
        colors = [
            'rgba(99, 102, 241, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(251, 146, 60, 0.8)',
            'rgba(167, 139, 250, 0.8)',
            'rgba(59, 130, 246, 0.8)'
        ]
        
        charts.append({
            'type': 'pie',
            'title': f'{cat_col.replace("_", " ").title()} Distribution',
            'data': {
                'labels': value_counts.index.tolist(),
                'datasets': [{
                    'label': 'Distribution',
                    'data': value_counts.values.tolist(),
                    'backgroundColor': colors[:len(value_counts)],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            }
        })
    
    # Chart 6: Average comparison (if multiple numeric columns)
    if len(col_types['numeric']) >= 2 and col_types['categorical']:
        cat_col = col_types['categorical'][0]
        num_cols = col_types['numeric'][:2]
        
        grouped_data = df.groupby(cat_col)[num_cols].mean().head(8)
        
        charts.append({
            'type': 'bar',
            'title': f'Average {" vs ".join([c.replace("_", " ").title() for c in num_cols])} by {cat_col.replace("_", " ").title()}',
            'data': {
                'labels': grouped_data.index.tolist(),
                'datasets': [
                    {
                        'label': num_cols[0].replace("_", " ").title(),
                        'data': grouped_data[num_cols[0]].tolist(),
                        'backgroundColor': 'rgba(99, 102, 241, 0.6)',
                        'borderColor': 'rgba(99, 102, 241, 1)',
                        'borderWidth': 2
                    },
                    {
                        'label': num_cols[1].replace("_", " ").title(),
                        'data': grouped_data[num_cols[1]].tolist(),
                        'backgroundColor': 'rgba(16, 185, 129, 0.6)',
                        'borderColor': 'rgba(16, 185, 129, 1)',
                        'borderWidth': 2
                    }
                ]
            }
        })
    
    # Chart 7: Doughnut chart for second categorical (if exists)
    if len(col_types['categorical']) >= 2:
        cat_col = col_types['categorical'][1]
        value_counts = df[cat_col].value_counts().head(5)
        
        colors = [
            'rgba(239, 68, 68, 0.8)',
            'rgba(251, 146, 60, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(167, 139, 250, 0.8)'
        ]
        
        charts.append({
            'type': 'doughnut',
            'title': f'{cat_col.replace("_", " ").title()} Breakdown',
            'data': {
                'labels': value_counts.index.tolist(),
                'datasets': [{
                    'label': 'Count',
                    'data': value_counts.values.tolist(),
                    'backgroundColor': colors[:len(value_counts)],
                    'borderWidth': 3,
                    'borderColor': '#ffffff'
                }]
            }
        })
    
    # Chart 8: Top/Bottom comparison for numeric column
    if col_types['numeric'] and col_types['categorical']:
        num_col = col_types['numeric'][0]
        cat_col = col_types['categorical'][0]
        
        grouped = df.groupby(cat_col)[num_col].sum().sort_values()
        top_5 = grouped.tail(5)
        
        charts.append({
            'type': 'horizontalBar',
            'title': f'Top 5 {cat_col.replace("_", " ").title()} by {num_col.replace("_", " ").title()}',
            'data': {
                'labels': top_5.index.tolist(),
                'datasets': [{
                    'label': num_col.replace("_", " ").title(),
                    'data': top_5.values.tolist(),
                    'backgroundColor': [
                        'rgba(16, 185, 129, 0.6)',
                        'rgba(59, 130, 246, 0.6)',
                        'rgba(167, 139, 250, 0.6)',
                        'rgba(251, 146, 60, 0.6)',
                        'rgba(239, 68, 68, 0.6)'
                    ],
                    'borderColor': [
                        'rgba(16, 185, 129, 1)',
                        'rgba(59, 130, 246, 1)',
                        'rgba(167, 139, 250, 1)',
                        'rgba(251, 146, 60, 1)',
                        'rgba(239, 68, 68, 1)'
                    ],
                    'borderWidth': 2
                }]
            }
        })
    
    return charts

def generate_insights_text(stats):
    """
    Generate human-readable insights from statistics
    
    Returns:
        list of insight strings
    """
    insights = []
    
    insights.append(f"📊 Dataset contains {stats['total_rows']:,} rows and {stats['total_columns']} columns")
    
    # Numeric insights
    if stats.get('numeric_stats'):
        for col, col_stats in stats['numeric_stats'].items():
            col_name = col.replace('_', ' ').title()
            insights.append(
                f"💰 Total {col_name}: {col_stats['total']:,.2f} | "
                f"Average: {col_stats['average']:,.2f}"
            )
    
    # Categorical insights
    if stats.get('categorical_stats'):
        for col, col_stats in stats['categorical_stats'].items():
            col_name = col.replace('_', ' ').title()
            top_value = list(col_stats['top_values'].keys())[0]
            insights.append(
                f"🏆 Most common {col_name}: {top_value} "
                f"({col_stats['unique_values']} unique values)"
            )
    
    return insights
