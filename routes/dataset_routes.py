from flask import Blueprint, render_template, request, jsonify
from services.db_service import get_all_datasets, get_dataset_by_id, execute_query
from services.file_service import get_file_preview, delete_file
from services.data_cleaning_service import get_dataset_preview, get_dataset_statistics
from utils.auth_utils import login_required, get_current_user_id

dataset_bp = Blueprint('dataset', __name__)

@dataset_bp.route('/')
def list_datasets():
    """List all datasets"""
    datasets = get_all_datasets()
    
    # Add statistics for each dataset
    if datasets:
        for dataset in datasets:
            if dataset.get('table_name'):
                stats = get_dataset_statistics(dataset['table_name'])
                if stats:
                    dataset['row_count'] = stats.get('total_rows', 0)
                    dataset['column_count'] = stats.get('column_count', 0)
    
    return jsonify({'success': True, 'datasets': datasets or []}), 200

@dataset_bp.route('/<int:dataset_id>')
def get_dataset(dataset_id):
    """Get a specific dataset with preview from MySQL table"""
    dataset = get_dataset_by_id(dataset_id)
    
    if dataset:
        # Get data from the cleaned MySQL table
        if dataset.get('table_name'):
            preview_data = get_dataset_preview(dataset['table_name'], limit=10)
            dataset['preview'] = preview_data
            
            # Get statistics
            stats = get_dataset_statistics(dataset['table_name'])
            if stats:
                dataset['statistics'] = stats
        else:
            dataset['preview'] = []
            dataset['statistics'] = None
        
        return jsonify({'success': True, 'dataset': dataset}), 200
    else:
        return jsonify({'success': False, 'error': 'Dataset not found'}), 404

@dataset_bp.route('/<int:dataset_id>/preview')
def preview_dataset(dataset_id):
    """Get dataset preview from MySQL table"""
    dataset = get_dataset_by_id(dataset_id)
    
    if dataset and dataset.get('table_name'):
        preview_data = get_dataset_preview(dataset['table_name'], limit=20)
        return jsonify({'success': True, 'preview': preview_data}), 200
    else:
        return jsonify({'success': False, 'error': 'Dataset not found or not processed'}), 404

@dataset_bp.route('/<int:dataset_id>/view')
@login_required
def view_dataset(dataset_id):
    """Get dataset data for viewing (user-specific)"""
    user_id = get_current_user_id()
    
    # Get dataset and verify ownership
    dataset = execute_query(
        "SELECT * FROM datasets WHERE id = %s AND user_id = %s",
        (dataset_id, user_id),
        fetch=True
    )
    
    if not dataset:
        return jsonify({'success': False, 'error': 'Dataset not found'}), 404
    
    dataset = dataset[0]
    
    if dataset.get('table_name'):
        preview_data = get_dataset_preview(dataset['table_name'], limit=100)
        return jsonify({'success': True, 'data': preview_data}), 200
    else:
        return jsonify({'success': False, 'error': 'Dataset not processed'}), 404

@dataset_bp.route('/<int:dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """Delete a dataset and its associated MySQL table"""
    try:
        dataset = get_dataset_by_id(dataset_id)
        
        if not dataset:
            return jsonify({'success': False, 'error': 'Dataset not found'}), 404
        
        # Drop the MySQL table if it exists
        if dataset.get('table_name'):
            try:
                drop_sql = f"DROP TABLE IF EXISTS {dataset['table_name']}"
                execute_query(drop_sql, fetch=False)
            except Exception as e:
                print(f"Error dropping table: {e}")
        
        # Delete the dataset record from database
        delete_sql = "DELETE FROM datasets WHERE id = %s"
        execute_query(delete_sql, params=(dataset_id,), fetch=False)
        
        # Optionally delete the uploaded file
        import os
        if dataset.get('file_path') and os.path.exists(dataset['file_path']):
            try:
                os.remove(dataset['file_path'])
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Dataset deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete dataset: {str(e)}'
        }), 500
