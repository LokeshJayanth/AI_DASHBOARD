"""
Dashboard Routes - View and manage saved AUTO MODE dashboards
"""
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from services.dashboard_service import (
    get_dashboard_by_id,
    get_user_dashboards,
    get_project_dashboards,
    delete_dashboard
)
from utils.auth_utils import login_required, get_current_user_id

dashboard_view_bp = Blueprint('dashboards', __name__, url_prefix='/dashboards')


@dashboard_view_bp.route('/')
@login_required
def dashboard_gallery():
    """View all saved dashboards for the current user"""
    user_id = get_current_user_id()
    
    # Get filter from query params
    project_id = request.args.get('project_id', type=int)
    
    if project_id:
        dashboards = get_project_dashboards(project_id)
    else:
        dashboards = get_user_dashboards(user_id)
    
    return render_template('dashboard_gallery.html',
                         dashboards=dashboards,
                         username=session.get('username', 'User'))


@dashboard_view_bp.route('/<int:dashboard_id>')
@login_required
def view_dashboard(dashboard_id):
    """View a specific saved dashboard with all its analytics"""
    user_id = get_current_user_id()
    
    dashboard = get_dashboard_by_id(dashboard_id)
    
    if not dashboard:
        return redirect(url_for('dashboards.dashboard_gallery'))
    
    # Check ownership
    if dashboard['user_id'] != user_id:
        return redirect(url_for('dashboards.dashboard_gallery'))
    
    return render_template('dashboard_view.html',
                         dashboard=dashboard,
                         username=session.get('username', 'User'))


@dashboard_view_bp.route('/<int:dashboard_id>/delete', methods=['POST'])
@login_required
def delete_dashboard_route(dashboard_id):
    """Delete a dashboard"""
    user_id = get_current_user_id()
    
    success = delete_dashboard(dashboard_id, user_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Dashboard deleted'})
    else:
        return jsonify({'success': False, 'error': 'Failed to delete dashboard'}), 403
