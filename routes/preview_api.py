"""
API endpoint to get dataset preview (first 10 rows)
"""
from flask import Blueprint, jsonify
from services.db_service import execute_query
from utils.auth_utils import login_required, get_current_user_id
import logging

storage_preview_bp = Blueprint('storage_preview', __name__)

@storage_preview_bp.route('/api/dataset/<int:dataset_id>/preview')
@login_required
def get_dataset_preview(dataset_id):
    """Get first 10 rows of a dataset for preview"""
    try:
        user_id = get_current_user_id()
        
        # Get dataset info and verify ownership
        dataset = execute_query(
            "SELECT * FROM datasets WHERE id = %s AND user_id = %s",
            (dataset_id, user_id),
            fetch=True
        )
        
        if not dataset:
            return jsonify({'success': False, 'error': 'Dataset not found'}), 404
        
        dataset = dataset[0]
        table_name = f"dataset_{dataset_id}_cleaned"
        
        # Get first 10 rows
        preview_data = execute_query(
            f"SELECT * FROM `{table_name}` LIMIT 10",
            fetch=True
        )
        
        if not preview_data:
            return jsonify({'success': False, 'error': 'No data found'}), 404
        
        # Get column names
        columns = list(preview_data[0].keys()) if preview_data else []
        
        # Convert to list of lists
        rows = [[row[col] for col in columns] for row in preview_data]
        
        return jsonify({
            'success': True,
            'columns': columns,
            'rows': rows,
            'total_rows': len(rows)
        })
        
    except Exception as e:
        logging.error(f"Error getting preview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
