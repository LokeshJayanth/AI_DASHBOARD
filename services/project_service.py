"""
Project Service
Handles project-related database operations and user-project management
"""
from services.db_service import execute_query
import os
from config import Config

def create_project(user_id, name, description=""):
    """
    Create a new project for a user
    Returns (success, message, project_id)
    """
    try:
        query = """
            INSERT INTO projects (user_id, name, description, status)
            VALUES (%s, %s, %s, 'active')
        """
        project_id = execute_query(query, (user_id, name, description))
        
        if project_id:
            # Create folder structure for the project
            create_project_folders(user_id, project_id)
            return True, "Project created successfully", project_id
        else:
            return False, "Failed to create project", None
            
    except Exception as e:
        print(f"Error creating project: {str(e)}")
        return False, f"Error: {str(e)}", None

def get_user_projects(user_id, status=None):
    """
    Get all projects for a user
    Optionally filter by status
    """
    try:
        query = "SELECT * FROM projects WHERE user_id = %s"
        params = [user_id]
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        projects = execute_query(query, tuple(params), fetch=True)
        
        # Add dataset count for each project
        if projects:
            for project in projects:
                count_query = "SELECT COUNT(*) as count FROM datasets WHERE project_id = %s"
                result = execute_query(count_query, (project['id'],), fetch=True)
                project['dataset_count'] = result[0]['count'] if result else 0
        
        return projects or []
        
    except Exception as e:
        print(f"Error getting user projects: {str(e)}")
        return []

def get_project_by_id(project_id):
    """
    Get a single project by ID
    Returns project dict or None
    """
    try:
        query = "SELECT * FROM projects WHERE id = %s"
        result = execute_query(query, (project_id,), fetch=True)
        return result[0] if result else None
    except Exception as e:
        print(f"Error getting project: {str(e)}")
        return None

def update_project(project_id, name=None, description=None, status=None):
    """
    Update project details
    Returns (success, message)
    """
    try:
        updates = []
        params = []
        
        if name:
            updates.append("name = %s")
            params.append(name)
        
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if status:
            updates.append("status = %s")
            params.append(status)
        
        if not updates:
            return False, "No updates provided"
        
        query = f"UPDATE projects SET {', '.join(updates)} WHERE id = %s"
        params.append(project_id)
        
        execute_query(query, tuple(params))
        return True, "Project updated successfully"
        
    except Exception as e:
        print(f"Error updating project: {str(e)}")
        return False, f"Error: {str(e)}"

def delete_project(project_id, user_id):
    """
    Delete a project and all associated data
    Returns (success, message)
    """
    try:
        # Verify ownership
        project = get_project_by_id(project_id)
        if not project:
            return False, "Project not found"
        
        if project['user_id'] != user_id:
            return False, "Unauthorized: You don't own this project"
        
        # Delete project (cascades to datasets via foreign key)
        query = "DELETE FROM projects WHERE id = %s"
        execute_query(query, (project_id,))
        
        # Delete project folder
        delete_project_folders(user_id, project_id)
        
        return True, "Project deleted successfully"
        
    except Exception as e:
        print(f"Error deleting project: {str(e)}")
        return False, f"Error: {str(e)}"

def validate_project_ownership(project_id, user_id):
    """
    Check if a user owns a project
    Returns True if user owns project, False otherwise
"""
    project = get_project_by_id(project_id)
    if not project:
        return False
    return project['user_id'] == user_id

def create_project_folders(user_id, project_id):
    """
    Create folder structure for a project:
    datasets/user_{user_id}/project_{project_id}/raw/
    datasets/user_{user_id}/project_{project_id}/cleaned/
    datasets/user_{user_id}/project_{project_id}/dashboards/
    """
    try:
        base_dir = os.path.join(Config.BASE_DIR, 'datasets')
        user_dir = os.path.join(base_dir, f'user_{user_id}')
        project_dir = os.path.join(user_dir, f'project_{project_id}')
        
        # Create subdirectories
        folders = ['raw', 'cleaned', 'dashboards']
        for folder in folders:
            folder_path = os.path.join(project_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
        
        print(f"✅ Created folder structure for user_{user_id}/project_{project_id}")
        return True
        
    except Exception as e:
        print(f"Error creating project folders: {str(e)}")
        return False

def delete_project_folders(user_id, project_id):
    """
    Delete project folder and all its contents
    """
    try:
        import shutil
        base_dir = os.path.join(Config.BASE_DIR, 'datasets')
        project_dir = os.path.join(base_dir, f'user_{user_id}', f'project_{project_id}')
        
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
            print(f"✅ Deleted folder for user_{user_id}/project_{project_id}")
        
        return True
        
    except Exception as e:
        print(f"Error deleting project folders: {str(e)}")
        return False

def get_project_path(user_id, project_id, subfolder='raw'):
    """
    Get the path to a project's subfolder
    Valid subfolders: 'raw', 'cleaned', 'dashboards'
    """
    base_dir = os.path.join(Config.BASE_DIR, 'datasets')
    project_path = os.path.join(base_dir, f'user_{user_id}', f'project_{project_id}', subfolder)
    
    # Ensure directory exists
    os.makedirs(project_path, exist_ok=True)
    
    return project_path

def get_recent_activity(user_id, limit=10):
    """
    Get recent activity for a user (recent datasets across all projects)
    """
    try:
        query = """
            SELECT d.*, p.name as project_name
            FROM datasets d
            LEFT JOIN projects p ON d.project_id = p.id
            WHERE d.user_id = %s
            ORDER BY d.created_at DESC
            LIMIT %s
        """
        result = execute_query(query, (user_id, limit), fetch=True)
        return result or []
        
    except Exception as e:
        print(f"Error getting recent activity: {str(e)}")
        return []
