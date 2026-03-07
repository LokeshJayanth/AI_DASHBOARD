"""
Storage Routes - Central hub for all dataset management
Displays all stored datasets and handles storage operations
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from services.db_service import get_all_datasets, create_dataset, execute_query
from services.data_cleaning_service import process_and_store_dataset, read_file
from utils.auth_utils import login_required, get_current_user_id
from services.file_service import save_uploaded_file
import pandas as pd

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/')
@login_required
def storage_page():
    """Display storage page with all datasets (user-specific)"""
    user_id = get_current_user_id()
    datasets = get_all_datasets(user_id=user_id)
    return render_template('storage.html', datasets=datasets or [])

@storage_bp.route('/upload', methods=['POST'])
@login_required
def upload_to_storage():
    """Upload file and automatically save to storage (user-specific)"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    dataset_name = request.form.get('name', file.filename)
    user_id = get_current_user_id()  # Get logged-in user's ID
    
    try:
        # Save the file
        file_info, error = save_uploaded_file(file)
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # Read the file into DataFrame
        df_raw, error = read_file(file_info['filepath'])
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # Create dataset record in database with user_id
        dataset_id = create_dataset(
            name=dataset_name,
            description=f'Uploaded on {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}',
            file_path=file_info['filepath'],
            file_type=file_info['file_type'],
            file_size=file_info['file_size'],
            user_id=user_id  # Associate with logged-in user
        )
        
        if not dataset_id:
            return jsonify({'success': False, 'error': 'Failed to create dataset record'}), 500
        
        # Process and store in MySQL (clean and store)
        success, message, stats = process_and_store_dataset(
            filepath=file_info['filepath'],
            dataset_name=dataset_name,
            dataset_id=dataset_id
        )
        
        if not success:
            # Update status to failed
            execute_query(
                "UPDATE datasets SET status = 'failed' WHERE id = %s",
                params=(dataset_id,),
                fetch=False
            )
            return jsonify({'success': False, 'error': message}), 500
        
        # Update status to completed
        execute_query(
            "UPDATE datasets SET status = 'completed' WHERE id = %s",
            params=(dataset_id,),
            fetch=False
        )
        
        return jsonify({
            'success': True,
            'message': 'Dataset uploaded and saved successfully',
            'dataset_id': dataset_id,
            'stats': stats
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@storage_bp.route('/api/list')
@login_required
def list_storage_datasets():
    """API endpoint to get all datasets (user-specific)"""
    user_id = get_current_user_id()
    datasets = get_all_datasets(user_id=user_id)
    
    # Add statistics for each dataset
    if datasets:
        for dataset in datasets:
            if dataset.get('table_name'):
                from services.data_cleaning_service import get_dataset_statistics
                stats = get_dataset_statistics(dataset['table_name'])
                if stats:
                    dataset['row_count'] = stats.get('total_rows', 0)
                    dataset['column_count'] = stats.get('column_count', 0)
    
    return jsonify({'success': True, 'datasets': datasets or []}), 200
