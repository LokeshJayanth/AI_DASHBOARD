"""
Dashboard Service - Handles saving and retrieving AUTO MODE dashboards
"""
import json
from datetime import datetime
from services.db_service import execute_query


def create_dashboard(name, dataset_id, user_id, project_id, stats_data, charts_data, insights_data, mode='auto'):
    """
    Save a complete dashboard state to the database
    
    Args:
        name: Dashboard name
        dataset_id: Associated dataset ID
        user_id: Owner user ID
        project_id: Associated project ID
        stats_data: Dictionary of KPI stats
        charts_data: List of chart configurations
        insights_data: List of insights
        mode: 'auto' or 'prompt'
    
    Returns:
        dashboard_id if successful, None otherwise
    """
    try:
        # Convert data to JSON strings
        stats_json = json.dumps(stats_data) if stats_data else None
        charts_json = json.dumps(charts_data) if charts_data else None
        insights_json = json.dumps(insights_data) if insights_data else None
        
        # Count charts and KPIs
        total_charts = len(charts_data) if charts_data else 0
        total_kpis = len(stats_data) if stats_data else 0
        
        # Get dataset info
        dataset_rows = stats_data.get('total_records', 0) if stats_data else 0
        dataset_columns = stats_data.get('total_columns_count', 0) if stats_data else 0
        
        query = """
            INSERT INTO dashboards (
                name, dataset_id, user_id, project_id, mode,
                stats_data, charts_data, insights_data,
                total_charts, total_kpis, dataset_rows, dataset_columns,
                status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'published')
        """
        
        params = (
            name, dataset_id, user_id, project_id, mode,
            stats_json, charts_json, insights_json,
            total_charts, total_kpis, dataset_rows, dataset_columns
        )
        
        dashboard_id = execute_query(query, params)
        
        if dashboard_id:
            # Update dataset to mark it has a dashboard
            update_query = """
                UPDATE datasets 
                SET has_dashboard = TRUE, dashboard_id = %s
                WHERE id = %s
            """
            execute_query(update_query, (dashboard_id, dataset_id))
        
        return dashboard_id
        
    except Exception as e:
        print(f"Error creating dashboard: {e}")
        return None


def get_dashboard_by_id(dashboard_id):
    """Get a dashboard by ID with all its data"""
    query = """
        SELECT 
            d.*,
            ds.name as dataset_name,
            ds.file_path,
            p.name as project_name
        FROM dashboards d
        LEFT JOIN datasets ds ON d.dataset_id = ds.id
        LEFT JOIN projects p ON d.project_id = p.id
        WHERE d.id = %s
    """
    
    result = execute_query(query, (dashboard_id,), fetch=True)
    
    if result and len(result) > 0:
        dashboard = dict(result[0])
        
        # Parse JSON fields
        if dashboard.get('stats_data'):
            dashboard['stats_data'] = json.loads(dashboard['stats_data'])
        if dashboard.get('charts_data'):
            dashboard['charts_data'] = json.loads(dashboard['charts_data'])
        if dashboard.get('insights_data'):
            dashboard['insights_data'] = json.loads(dashboard['insights_data'])
        
        # Update last viewed timestamp
        update_query = "UPDATE dashboards SET last_viewed_at = NOW() WHERE id = %s"
        execute_query(update_query, (dashboard_id,))
        
        return dashboard
    
    return None


def get_user_dashboards(user_id, project_id=None):
    """Get all dashboards for a user, optionally filtered by project"""
    if project_id:
        query = """
            SELECT 
                d.*,
                ds.name as dataset_name,
                p.name as project_name
            FROM dashboards d
            LEFT JOIN datasets ds ON d.dataset_id = ds.id
            LEFT JOIN projects p ON d.project_id = p.id
            WHERE d.user_id = %s AND d.project_id = %s
            ORDER BY d.created_at DESC
        """
        params = (user_id, project_id)
    else:
        query = """
            SELECT 
                d.*,
                ds.name as dataset_name,
                p.name as project_name
            FROM dashboards d
            LEFT JOIN datasets ds ON d.dataset_id = ds.id
            LEFT JOIN projects p ON d.project_id = p.id
            WHERE d.user_id = %s
            ORDER BY d.created_at DESC
        """
        params = (user_id,)
    
    results = execute_query(query, params, fetch=True)
    
    if results:
        dashboards = []
        for row in results:
            dashboard = dict(row)
            # Don't parse JSON for list view (performance)
            dashboards.append(dashboard)
        return dashboards
    
    return []


def get_project_dashboards(project_id):
    """Get all dashboards for a specific project"""
    query = """
        SELECT 
            d.*,
            ds.name as dataset_name,
            u.username
        FROM dashboards d
        LEFT JOIN datasets ds ON d.dataset_id = ds.id
        LEFT JOIN users u ON d.user_id = u.id
        WHERE d.project_id = %s
        ORDER BY d.created_at DESC
    """
    
    results = execute_query(query, (project_id,), fetch=True)
    
    if results:
        return [dict(row) for row in results]
    
    return []


def delete_dashboard(dashboard_id, user_id):
    """Delete a dashboard (only if owned by user)"""
    # First check ownership
    check_query = "SELECT user_id FROM dashboards WHERE id = %s"
    result = execute_query(check_query, (dashboard_id,), fetch=True)
    
    if not result or result[0]['user_id'] != user_id:
        return False
    
    # Delete dashboard
    delete_query = "DELETE FROM dashboards WHERE id = %s"
    execute_query(delete_query, (dashboard_id,))
    
    return True


def update_dashboard_files(dashboard_id, preview_image=None, powerbi_file=None, csv_file=None):
    """Update file paths for a dashboard"""
    updates = []
    params = []
    
    if preview_image:
        updates.append("preview_image = %s")
        params.append(preview_image)
    if powerbi_file:
        updates.append("powerbi_file = %s")
        params.append(powerbi_file)
    if csv_file:
        updates.append("csv_file = %s")
        params.append(csv_file)
    
    if not updates:
        return False
    
    params.append(dashboard_id)
    query = f"UPDATE dashboards SET {', '.join(updates)} WHERE id = %s"
    
    execute_query(query, tuple(params))
    return True
