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

def find_column_by_keywords(df, keywords):
    """
    Find column name that matches any of the keywords (case-insensitive)
    """
    df_cols_lower = [col.lower() for col in df.columns]
    for keyword in keywords:
        for i, col_lower in enumerate(df_cols_lower):
            if keyword in col_lower:
                return df.columns[i]
    return None

def generate_summary_stats(df):
    """
    Generate summary statistics for the dataset with specific KPIs
    
    Returns:
        dict with key metrics including specific KPIs (Total Records, Columns, Departments, Salary stats)
    """
    col_types = detect_column_types(df)
    
    # Find common column names
    department_col = find_column_by_keywords(df, ['department', 'dept', 'division', 'team'])
    salary_col = find_column_by_keywords(df, ['salary', 'wage', 'pay', 'income', 'compensation'])
    date_col = find_column_by_keywords(df, ['date', 'join', 'hire', 'start', 'created', 'time'])
    
    # Basic stats
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': len(col_types['numeric']),
        'categorical_columns': len(col_types['categorical']),
        'date_columns': len(col_types['date']),
    }
    
    # Specific KPIs as requested
    stats['total_records'] = len(df)
    stats['total_columns_count'] = len(df.columns)
    
    # Total Departments (if department column exists)
    if department_col:
        stats['total_departments'] = int(df[department_col].nunique())
    else:
        # Use first categorical column as fallback
        if col_types['categorical']:
            cat_col_name = col_types['categorical'][0]
            stats['total_departments'] = int(df[cat_col_name].nunique())
        else:
            stats['total_departments'] = 0
    
    # Salary KPIs (if salary column exists)
    if salary_col and salary_col in df.columns:
        try:
            mean_val = df[salary_col].mean()
            max_val = df[salary_col].max()
            min_val = df[salary_col].min()
            stats['average_salary'] = round(float(mean_val), 2) if pd.notna(mean_val) else 0
            stats['max_salary'] = round(float(max_val), 2) if pd.notna(max_val) else 0
            stats['min_salary'] = round(float(min_val), 2) if pd.notna(min_val) else 0
        except Exception:
            stats['average_salary'] = 0
            stats['max_salary'] = 0
            stats['min_salary'] = 0
    else:
        # Use first numeric column as fallback
        if col_types['numeric']:
            num_col = col_types['numeric'][0]
            try:
                mean_val = df[num_col].mean()
                max_val = df[num_col].max()
                min_val = df[num_col].min()
                stats['average_salary'] = round(float(mean_val), 2) if pd.notna(mean_val) else 0
                stats['max_salary'] = round(float(max_val), 2) if pd.notna(max_val) else 0
                stats['min_salary'] = round(float(min_val), 2) if pd.notna(min_val) else 0
            except Exception:
                stats['average_salary'] = 0
                stats['max_salary'] = 0
                stats['min_salary'] = 0
        else:
            stats['average_salary'] = 0
            stats['max_salary'] = 0
            stats['min_salary'] = 0
    
    # Store detected column names for chart generation
    stats['detected_columns'] = {
        'department': department_col,
        'salary': salary_col,
        'date': date_col
    }
    
    # Additional stats
    stats['memory_usage_mb'] = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    stats['missing_values'] = int(df.isnull().sum().sum())
    stats['duplicate_rows'] = int(df.duplicated().sum())
    stats['missing_percentage'] = round((stats['missing_values'] / (len(df) * len(df.columns)) * 100), 2) if len(df) > 0 else 0
    
    # Additional KPIs
    stats['total_unique_values'] = int(df.nunique().sum())
    stats['data_completeness'] = round(100 - stats['missing_percentage'], 2)
    
    # Calculate median salary if available
    if salary_col and salary_col in df.columns:
        try:
            median_val = df[salary_col].median()
            stats['median_salary'] = round(float(median_val), 2) if pd.notna(median_val) else 0
        except Exception:
            stats['median_salary'] = 0
    elif col_types['numeric']:
        try:
            num_col = col_types['numeric'][0]
            median_val = df[num_col].median()
            stats['median_salary'] = round(float(median_val), 2) if pd.notna(median_val) else 0
        except Exception:
            stats['median_salary'] = 0
    else:
        stats['median_salary'] = 0
    
    # Calculate salary range
    if stats['max_salary'] > 0 and stats['min_salary'] > 0:
        stats['salary_range'] = round(stats['max_salary'] - stats['min_salary'], 2)
    else:
        stats['salary_range'] = 0
    
    # Data quality score (0-100)
    quality_score = 100
    if stats['missing_values'] > 0:
        quality_score -= min(stats['missing_percentage'] * 2, 40)
    if stats['duplicate_rows'] > 0:
        dup_percentage = (stats['duplicate_rows'] / len(df)) * 100 if len(df) > 0 else 0
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
            'std': float(df[col].std()) if len(df) > 1 else 0
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
    Generates specific charts: Employee Count by Dept, Avg Salary by Dept, Employees Over Time, Box Plot, Pie Chart
    
    Returns:
        list of chart configurations for Chart.js
    """
    col_types = detect_column_types(df)
    charts = []
    
    # Find common column names
    department_col = find_column_by_keywords(df, ['department', 'dept', 'division', 'team'])
    salary_col = find_column_by_keywords(df, ['salary', 'wage', 'pay', 'income', 'compensation'])
    date_col = find_column_by_keywords(df, ['date', 'join', 'hire', 'start', 'created', 'time'])
    
    # Use detected columns or fallback to first available
    dept_col = department_col if department_col else (col_types['categorical'][0] if col_types['categorical'] else None)
    sal_col = salary_col if salary_col else (col_types['numeric'][0] if col_types['numeric'] else None)
    dt_col = date_col if date_col else (col_types['date'][0] if col_types['date'] else None)
    
    # Chart 1: Employee Count by Department (Bar Chart) - MUST HAVE
    if dept_col:
        value_counts = df[dept_col].value_counts().head(15)
        chart_title = f'Employee Count by {dept_col.replace("_", " ").title()}'
        
        charts.append({
            'type': 'bar',
            'title': chart_title,
            'data': {
                'labels': [str(x) for x in value_counts.index.tolist()],
                'datasets': [{
                    'label': 'Count',
                    'data': value_counts.values.tolist(),
                    'backgroundColor': 'rgba(99, 102, 241, 0.6)',
                    'borderColor': 'rgba(99, 102, 241, 1)',
                    'borderWidth': 2
                }]
            }
        })
    
    # Chart 2: Average Salary by Department (Bar Chart) - MUST HAVE
    if dept_col and sal_col:
        grouped = df.groupby(dept_col)[sal_col].mean().head(15)
        chart_title = f'Average {sal_col.replace("_", " ").title()} by {dept_col.replace("_", " ").title()}'
        
        charts.append({
            'type': 'bar',
            'title': chart_title,
            'data': {
                'labels': [str(x) for x in grouped.index.tolist()],
                'datasets': [{
                    'label': f'Average {sal_col.replace("_", " ").title()}',
                    'data': [round(float(x), 2) for x in grouped.values.tolist()],
                    'backgroundColor': 'rgba(16, 185, 129, 0.6)',
                    'borderColor': 'rgba(16, 185, 129, 1)',
                    'borderWidth': 2
                }]
            }
        })
    
    # Chart 3: Employees Over Time (Line Chart) - MUST HAVE
    if dt_col and dept_col:
        try:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df[dt_col]):
                df[dt_col] = pd.to_datetime(df[dt_col], errors='coerce')
            
            # Sort by date and aggregate by month/year
            df_sorted = df.sort_values(dt_col).dropna(subset=[dt_col])
            if len(df_sorted) > 0:
                # Group by month
                df_sorted['period'] = df_sorted[dt_col].dt.to_period('M')
                trend_data = df_sorted.groupby('period').size()
                
                charts.append({
                    'type': 'line',
                    'title': f'Employees Over Time',
                    'data': {
                        'labels': [str(x) for x in trend_data.index.tolist()],
                        'datasets': [{
                            'label': 'Employee Count',
                            'data': trend_data.values.tolist(),
                            'borderColor': 'rgba(239, 68, 68, 1)',
                            'backgroundColor': 'rgba(239, 68, 68, 0.1)',
                            'borderWidth': 2,
                            'tension': 0.4,
                            'fill': True
                        }]
                    }
                })
        except Exception as e:
            # If date parsing fails, skip this chart
            pass
    
    # Chart 4: Box Plot - Salary Distribution (MEDIUM LEVEL)
    if sal_col and dept_col:
        try:
            # Create box plot data by grouping salary by department
            # Chart.js doesn't have native box plots, so we'll create a grouped bar showing quartiles
            def calculate_stats(x):
                try:
                    return {
                        'min': float(x.min()) if pd.notna(x.min()) else 0,
                        'q1': float(x.quantile(0.25)) if pd.notna(x.quantile(0.25)) else 0,
                        'median': float(x.median()) if pd.notna(x.median()) else 0,
                        'q3': float(x.quantile(0.75)) if pd.notna(x.quantile(0.75)) else 0,
                        'max': float(x.max()) if pd.notna(x.max()) else 0,
                        'mean': float(x.mean()) if pd.notna(x.mean()) else 0
                    }
                except Exception:
                    return {
                        'min': 0, 'q1': 0, 'median': 0, 'q3': 0, 'max': 0, 'mean': 0
                    }
            
            grouped_salary = df.groupby(dept_col)[sal_col].apply(calculate_stats).to_dict()
            
            # Create box plot visualization using grouped bars
            dept_names = list(grouped_salary.keys())[:10]  # Limit to 10 departments
            if dept_names:
                min_vals = [grouped_salary[d].get('min', 0) for d in dept_names]
                q1_vals = [grouped_salary[d].get('q1', 0) for d in dept_names]
                median_vals = [grouped_salary[d].get('median', 0) for d in dept_names]
                q3_vals = [grouped_salary[d].get('q3', 0) for d in dept_names]
                max_vals = [grouped_salary[d].get('max', 0) for d in dept_names]
                
                charts.append({
                    'type': 'bar',
                    'title': f'{sal_col.replace("_", " ").title()} Distribution by {dept_col.replace("_", " ").title()} (Box Plot Style)',
                    'data': {
                        'labels': [str(x) for x in dept_names],
                        'datasets': [
                            {
                                'label': 'Min',
                                'data': min_vals,
                                'backgroundColor': 'rgba(156, 163, 175, 0.6)',
                                'borderColor': 'rgba(156, 163, 175, 1)',
                                'borderWidth': 1
                            },
                            {
                                'label': 'Q1',
                                'data': q1_vals,
                                'backgroundColor': 'rgba(251, 146, 60, 0.6)',
                                'borderColor': 'rgba(251, 146, 60, 1)',
                                'borderWidth': 2
                            },
                            {
                                'label': 'Median',
                                'data': median_vals,
                                'backgroundColor': 'rgba(239, 68, 68, 0.8)',
                                'borderColor': 'rgba(239, 68, 68, 1)',
                                'borderWidth': 2
                            },
                            {
                                'label': 'Q3',
                                'data': q3_vals,
                                'backgroundColor': 'rgba(251, 146, 60, 0.6)',
                                'borderColor': 'rgba(251, 146, 60, 1)',
                                'borderWidth': 2
                            },
                            {
                                'label': 'Max',
                                'data': max_vals,
                                'backgroundColor': 'rgba(156, 163, 175, 0.6)',
                                'borderColor': 'rgba(156, 163, 175, 1)',
                                'borderWidth': 1
                            }
                        ]
                    }
                })
        except Exception as e:
            # Skip box plot if there's an error
            pass
    
    # Chart 5: Pie / Donut Chart - Department Share (MEDIUM LEVEL)
    # Only show if departments <= 6
    if dept_col:
        value_counts = df[dept_col].value_counts()
        if len(value_counts) <= 6:
            colors = [
                'rgba(99, 102, 241, 0.8)',
                'rgba(16, 185, 129, 0.8)',
                'rgba(239, 68, 68, 0.8)',
                'rgba(251, 146, 60, 0.8)',
                'rgba(167, 139, 250, 0.8)',
                'rgba(59, 130, 246, 0.8)'
            ]
            
            charts.append({
                'type': 'doughnut',
                'title': f'{dept_col.replace("_", " ").title()} Share (%)',
                'data': {
                    'labels': [str(x) for x in value_counts.index.tolist()],
                    'datasets': [{
                        'label': 'Count',
                        'data': value_counts.values.tolist(),
                        'backgroundColor': colors[:len(value_counts)],
                        'borderWidth': 3,
                        'borderColor': '#ffffff'
                    }]
                }
            })
    
    # Chart 6: Horizontal Bar - Top Departments by Count
    if dept_col:
        try:
            top_depts = df[dept_col].value_counts().head(10).sort_values()
            charts.append({
                'type': 'bar',
                'title': f'Top 10 {dept_col.replace("_", " ").title()} by Count',
                'data': {
                    'labels': [str(x) for x in top_depts.index.tolist()],
                    'datasets': [{
                        'label': 'Count',
                        'data': top_depts.values.tolist(),
                        'backgroundColor': 'rgba(139, 92, 246, 0.6)',
                        'borderColor': 'rgba(139, 92, 246, 1)',
                        'borderWidth': 2
                    }]
                },
                'options': {
                    'indexAxis': 'y'  # Horizontal bar chart
                }
            })
        except Exception:
            pass
    
    # Chart 7: Scatter Plot - If we have two numeric columns
    if len(col_types['numeric']) >= 2:
        try:
            num_col1 = col_types['numeric'][0]
            num_col2 = col_types['numeric'][1]
            
            # Sample data if too many points
            sample_size = min(100, len(df))
            df_sample = df.sample(n=sample_size, random_state=42) if len(df) > sample_size else df
            
            # Filter out NaN values
            df_clean = df_sample[[num_col1, num_col2]].dropna()
            
            if len(df_clean) > 0:
                scatter_data = [
                    {'x': float(df_clean.iloc[i][num_col1]), 'y': float(df_clean.iloc[i][num_col2])}
                    for i in range(min(100, len(df_clean)))
                ]
                
                if scatter_data:
                    charts.append({
                        'type': 'scatter',
                        'title': f'{num_col1.replace("_", " ").title()} vs {num_col2.replace("_", " ").title()}',
                        'data': {
                            'datasets': [{
                                'label': 'Data Points',
                                'data': scatter_data,
                                'backgroundColor': 'rgba(59, 130, 246, 0.5)',
                                'borderColor': 'rgba(59, 130, 246, 1)',
                                'pointRadius': 4,
                                'pointHoverRadius': 6
                            }]
                        }
                    })
        except Exception:
            pass
    
    # Chart 8: Area Chart - Cumulative Trend
    if dt_col and sal_col:
        try:
            if not pd.api.types.is_datetime64_any_dtype(df[dt_col]):
                df[dt_col] = pd.to_datetime(df[dt_col], errors='coerce')
            
            df_sorted = df.sort_values(dt_col).dropna(subset=[dt_col, sal_col])
            if len(df_sorted) > 0:
                df_sorted['period'] = df_sorted[dt_col].dt.to_period('M')
                cumulative_data = df_sorted.groupby('period')[sal_col].sum().cumsum()
                
                charts.append({
                    'type': 'line',
                    'title': f'Cumulative {sal_col.replace("_", " ").title()} Over Time',
                    'data': {
                        'labels': [str(x) for x in cumulative_data.index.tolist()],
                        'datasets': [{
                            'label': 'Cumulative Total',
                            'data': [round(float(x), 2) for x in cumulative_data.values.tolist()],
                            'borderColor': 'rgba(16, 185, 129, 1)',
                            'backgroundColor': 'rgba(16, 185, 129, 0.2)',
                            'borderWidth': 2,
                            'tension': 0.4,
                            'fill': True
                        }]
                    }
                })
        except Exception:
            pass
    
    # Chart 9: Stacked Bar Chart - Multiple Metrics by Category
    if dept_col and len(col_types['numeric']) >= 2:
        try:
            num_col1 = col_types['numeric'][0]
            num_col2 = col_types['numeric'][1]
            
            grouped = df.groupby(dept_col)[[num_col1, num_col2]].sum().head(10)
            
            charts.append({
                'type': 'bar',
                'title': f'{num_col1.replace("_", " ").title()} & {num_col2.replace("_", " ").title()} by {dept_col.replace("_", " ").title()}',
                'data': {
                    'labels': [str(x) for x in grouped.index.tolist()],
                    'datasets': [
                        {
                            'label': num_col1.replace("_", " ").title(),
                            'data': [round(float(x), 2) for x in grouped[num_col1].tolist()],
                            'backgroundColor': 'rgba(99, 102, 241, 0.7)',
                            'borderColor': 'rgba(99, 102, 241, 1)',
                            'borderWidth': 2
                        },
                        {
                            'label': num_col2.replace("_", " ").title(),
                            'data': [round(float(x), 2) for x in grouped[num_col2].tolist()],
                            'backgroundColor': 'rgba(251, 146, 60, 0.7)',
                            'borderColor': 'rgba(251, 146, 60, 1)',
                            'borderWidth': 2
                        }
                    ]
                },
                'options': {
                    'scales': {
                        'x': {'stacked': True},
                        'y': {'stacked': True}
                    }
                }
            })
        except Exception:
            pass
    
    # Chart 10: Radar Chart - If we have multiple numeric columns
    if len(col_types['numeric']) >= 3 and dept_col:
        try:
            # Get top 3 departments
            top_depts = df[dept_col].value_counts().head(3).index.tolist()
            num_cols = col_types['numeric'][:3]
            
            radar_datasets = []
            colors = [
                {'bg': 'rgba(99, 102, 241, 0.2)', 'border': 'rgba(99, 102, 241, 1)'},
                {'bg': 'rgba(16, 185, 129, 0.2)', 'border': 'rgba(16, 185, 129, 1)'},
                {'bg': 'rgba(239, 68, 68, 0.2)', 'border': 'rgba(239, 68, 68, 1)'}
            ]
            
            for idx, dept in enumerate(top_depts):
                dept_data = df[df[dept_col] == dept]
                values = [float(dept_data[col].mean()) if len(dept_data) > 0 else 0 for col in num_cols]
                
                radar_datasets.append({
                    'label': str(dept),
                    'data': values,
                    'backgroundColor': colors[idx % len(colors)]['bg'],
                    'borderColor': colors[idx % len(colors)]['border'],
                    'borderWidth': 2
                })
            
            charts.append({
                'type': 'radar',
                'title': f'Comparison: Top 3 {dept_col.replace("_", " ").title()}',
                'data': {
                    'labels': [col.replace("_", " ").title() for col in num_cols],
                    'datasets': radar_datasets
                }
            })
        except Exception:
            pass
    
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
