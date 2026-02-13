"""
Dashboard Routes - User-specific dashboard and project management
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from utils.auth_utils import login_required, get_current_user_id
from services.project_service import (
    create_project, get_user_projects, get_project_by_id, 
    update_project, delete_project, get_recent_activity
)
from services.db_service import get_all_datasets, execute_query

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def user_dashboard():
    """User-specific dashboard showing their projects and recent activity"""
    user_id = get_current_user_id()
    username = session.get('username', 'User')
    
    # Get user's projects
    projects = get_user_projects(user_id)
    
    # Get recent activity
    recent_activity = get_recent_activity(user_id, limit=5)
    
    # Get total datasets count
    all_datasets = get_all_datasets(user_id=user_id)
    total_datasets = len(all_datasets) if all_datasets else 0
    
    return render_template('user_dashboard.html',
                         username=username,
                         projects=projects,
                         recent_activity=recent_activity,
                         total_datasets=total_datasets,
                         total_projects=len(projects))

@dashboard_bp.route('/project/create', methods=['POST'])
@login_required
def create_new_project():
    """Create a new project for the user"""
    user_id = get_current_user_id()
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Project name is required', 'error')
        return redirect(url_for('dashboard.user_dashboard'))
    
    success, message, project_id = create_project(user_id, name, description)
    
    if success:
        flash(f'✅ Project "{name}" created successfully! Now upload your data.', 'success')
        # Redirect directly to upload page with project_id
        return redirect(url_for('upload.upload_page', project_id=project_id))
    else:
        flash(f'❌ {message}', 'error')
        return redirect(url_for('dashboard.user_dashboard'))

@dashboard_bp.route('/project/<int:project_id>')
@login_required
def view_project(project_id):
    """View a specific project"""
    user_id = get_current_user_id()
    project = get_project_by_id(project_id)
    
    # Check ownership
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('dashboard.user_dashboard'))
    
    if project['user_id'] != user_id:
        flash('❌ Unauthorized: You do not have access to this project', 'error')
        return redirect(url_for('dashboard.user_dashboard'))
    
    # Get datasets for this project
    datasets = execute_query(
        "SELECT * FROM datasets WHERE project_id = %s ORDER BY created_at DESC",
        (project_id,),
        fetch=True
    )
    
    # Store project_id in session for upload workflow
    session['current_project_id'] = project_id
    session.modified = True
    
    return render_template('project_view.html',
                         project=project,
                         datasets=datasets or [],
                         username=session.get('username', 'User'))

@dashboard_bp.route('/project/<int:project_id>/update', methods=['POST'])
@login_required
def update_project_route(project_id):
    """Update project details"""
    user_id = get_current_user_id()
    project = get_project_by_id(project_id)
    
    # Check ownership
    if not project or project['user_id'] != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    name = request.form.get('name')
    description = request.form.get('description')
    status = request.form.get('status')
    
    success, message = update_project(project_id, name, description, status)
    
    if success:
        flash(f'✅ {message}', 'success')
    else:
        flash(f'❌ {message}', 'error')
    
    return redirect(url_for('dashboard.view_project', project_id=project_id))

@dashboard_bp.route('/project/<int:project_id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_project_route(project_id):
    """Delete a project"""
    user_id = get_current_user_id()
    
    success, message = delete_project(project_id, user_id)
    
    if success:
        flash(f'✅ {message}', 'success')
    else:
        flash(f'❌ {message}', 'error')
    
    return redirect(url_for('dashboard.user_dashboard'))

@dashboard_bp.route('/api/projects')
@login_required
def get_projects_api():
    """API endpoint to get user's projects"""
    user_id = get_current_user_id()
    projects = get_user_projects(user_id)
    
    return jsonify({
        'success': True,
        'projects': projects
    }), 200

@dashboard_bp.route('/datasets')
@login_required  
def datasets_page():
    """Show all user's datasets across all projects"""
    user_id = get_current_user_id()
    username = session.get('username', 'User')
    
    # Get all datasets with project information
    query = """
        SELECT d.*, p.name as project_name
        FROM datasets d
        LEFT JOIN projects p ON d.project_id = p.id
        WHERE d.user_id = %s
        ORDER BY d.created_at DESC
    """
    datasets = execute_query(query, (user_id,), fetch=True)
    
    return render_template('datasets_page.html',
                         username=username,
                         datasets=datasets or [])
