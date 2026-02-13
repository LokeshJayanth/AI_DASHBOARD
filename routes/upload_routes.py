"""
Enhanced Upload Routes - Unified Dashboard Interface
Handles upload, preview, cleaning, column selection, downloads, and analytics in one flow
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file, flash
from services.file_service import save_uploaded_file, clean_dataframe
from services.db_service import create_dataset, execute_query
from services.data_cleaning_service import process_and_store_dataset, read_file
from services.export_service import export_to_csv, export_to_excel, get_download_filename
from services.auto_analytics_service import generate_summary_stats, create_auto_charts, generate_insights_text
from services.ai_prompts_service import (
    get_dataset_schema, 
    get_auto_mode_prompt, 
    get_powerbi_template_spec,
    export_powerbi_template_json
)
from services.powerbi_generator_service import create_powerbi_template_pbix
import pandas as pd
import json

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/')
def upload_page():
    """Render upload page"""
    # Get project_id from query parameters if provided
    project_id = request.args.get('project_id', type=int)
    
    # Store project_id in session if provided
    if project_id:
        session['current_project_id'] = project_id
        session.modified = True
    
    # Get current project_id from session
    current_project_id = session.get('current_project_id')
    
    return render_template('upload.html', project_id=current_project_id)

# ============================================================================
# STEP 1: Upload & Raw Preview
# ============================================================================

@upload_bp.route('/file', methods=['POST'])
def upload_file():
    """Upload file and show raw preview page"""
    if 'file' not in request.files:
        flash('No file provided', 'error')
        return redirect(url_for('upload.upload_page'))
    
    file = request.files['file']
    dataset_name = request.form.get('name', file.filename)
    
    try:
        # Save the file temporarily
        file_info, error = save_uploaded_file(file)
        if error:
            flash(error, 'error')
            return redirect(url_for('upload.upload_page'))
        
        # Read the file into DataFrame
        df_raw, error = read_file(file_info['filepath'])
        if error:
            flash(error, 'error')
            return redirect(url_for('upload.upload_page'))
        
        # Store essential data in session
        session['upload_data'] = {
            'dataset_name': dataset_name,
            'filepath': file_info['filepath'],
            'columns': df_raw.columns.tolist(),
            'rows': len(df_raw),
            'project_id': session.get('current_project_id')  # Associate with current project
        }
        session.modified = True
        
        # Get preview HTML (first 10 rows)
        preview_html = df_raw.head(10).to_html(classes='data-table', index=False, border=0)
        
        # Get basic stats
        stats = {
            'rows': len(df_raw),
            'columns': len(df_raw.columns),
            'null_counts': df_raw.isnull().sum().to_dict(),
            'duplicates': int(df_raw.duplicated().sum())
        }
        
        # Render raw preview page
        return render_template('upload_raw_preview.html',
                             dataset_name=dataset_name,
                             preview=preview_html,
                             stats=stats)
    
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'error')
        return redirect(url_for('upload.upload_page'))

# ============================================================================
# STEP 2: Clean Data
# ============================================================================

@upload_bp.route('/clean', methods=['POST'])
def clean_data():
    """Clean the data and show cleaned preview page"""
    if 'upload_data' not in session:
        flash('No upload session found', 'error')
        return redirect(url_for('upload.upload_page'))
    
    try:
        # Load raw data from file
        upload_data = session['upload_data']
        df_raw, error = read_file(upload_data['filepath'])
        if error:
            flash(error, 'error')
            return redirect(url_for('upload.upload_page'))
        
        # Apply cleaning
        df_clean = clean_dataframe(df_raw)
        
        # Save cleaned data to temp file
        import os
        import tempfile
        temp_dir = tempfile.gettempdir()
        cleaned_filepath = os.path.join(temp_dir, f"cleaned_{os.path.basename(upload_data['filepath'])}")
        df_clean.to_pickle(cleaned_filepath)
        
        # Store file path in session
        session['upload_data']['cleaned_filepath'] = cleaned_filepath
        session['upload_data']['cleaned_columns'] = df_clean.columns.tolist()
        session.modified = True
        
        # Get preview HTML
        preview_html = df_clean.head(10).to_html(classes='data-table', index=False, border=0)
        
        # Compare before/after stats
        stats = {
            'before': {
                'rows': len(df_raw),
                'columns': len(df_raw.columns),
                'nulls': int(df_raw.isnull().sum().sum()),
                'duplicates': int(df_raw.duplicated().sum())
            },
            'after': {
                'rows': len(df_clean),
                'columns': len(df_clean.columns),
                'nulls': int(df_clean.isnull().sum().sum()),
                'duplicates': int(df_clean.duplicated().sum())
            }
        }
        
        # Render cleaned preview page
        return render_template('upload_cleaned_preview.html',
                             dataset_name=upload_data['dataset_name'],
                             preview=preview_html,
                             columns=df_clean.columns.tolist(),
                             stats=stats)
    
    except Exception as e:
        flash(f'Cleaning failed: {str(e)}', 'error')
        return redirect(url_for('upload.upload_page'))

# ============================================================================
# STEP 3: Select Columns
# ============================================================================

@upload_bp.route('/select-columns', methods=['POST'])
def select_columns():
    """Handle column selection and show download page"""
    if 'upload_data' not in session or 'cleaned_filepath' not in session['upload_data']:
        flash('No cleaned data available', 'error')
        return redirect(url_for('upload.upload_page'))
    
    try:
        # Get selected columns from form
        selected_columns = request.form.getlist('columns')
        
        if not selected_columns:
            flash('Please select at least one column', 'error')
            return redirect(url_for('upload.upload_page'))
        
        # Load cleaned data from file
        upload_data = session['upload_data']
        df_clean = pd.read_pickle(upload_data['cleaned_filepath'])
        
        # Filter to selected columns
        df_final = df_clean[selected_columns]
        
        # Save final data to temp file
        import os
        import tempfile
        temp_dir = tempfile.gettempdir()
        final_filepath = os.path.join(temp_dir, f"final_{os.path.basename(upload_data['filepath'])}")
        df_final.to_pickle(final_filepath)
        
        # Update session
        session['upload_data']['final_filepath'] = final_filepath
        session['upload_data']['selected_columns'] = selected_columns
        session.modified = True
        
        
        # Redirect to analytics page
        return redirect(url_for('upload.analytics'))
    
    except Exception as e:
        flash(f'Column selection failed: {str(e)}', 'error')
        return redirect(url_for('upload.upload_page'))

# ============================================================================
# STEP 4: Downloads
# ============================================================================

@upload_bp.route('/download/csv')
def download_csv():
    """Download cleaned dataset as CSV"""
    if 'upload_data' not in session or 'final_filepath' not in session['upload_data']:
        return redirect(url_for('upload.upload_page'))
    
    try:
        upload_data = session['upload_data']
        df_final = pd.read_pickle(upload_data['final_filepath'])
        
        # Generate filename
        filename = get_download_filename(upload_data['dataset_name'], 'cleaned')
        
        # Export to BytesIO for download
        output = export_to_csv(df_final, filename)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{filename}.csv'
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Download failed: {str(e)}'}), 500

@upload_bp.route('/download/excel')
def download_excel():
    """Download cleaned dataset as Excel"""
    if 'upload_data' not in session or 'final_filepath' not in session['upload_data']:
        return redirect(url_for('upload.upload_page'))
    
    try:
        upload_data = session['upload_data']
        df_final = pd.read_pickle(upload_data['final_filepath'])
        
        # Generate filename
        filename = get_download_filename(upload_data['dataset_name'], 'cleaned')
        
        # Export to BytesIO for download
        output = export_to_excel(df_final, filename)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{filename}.xlsx'
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Download failed: {str(e)}'}), 500


@upload_bp.route('/download/powerbi')
def download_powerbi():
    """Download Power BI file (.pbix) with embedded data and visualizations"""
    if 'upload_data' not in session or 'final_filepath' not in session['upload_data']:
        return jsonify({
            'success': False,
            'error': 'No data available'
        }), 404
    
    try:
        upload_data = session['upload_data']
        df_final = pd.read_pickle(upload_data['final_filepath'])
        
        # Generate auto analytics to get chart configurations
        charts = create_auto_charts(df_final)
        
        # Get dataset name
        dataset_name = upload_data.get('dataset_name', 'dataset').replace(' ', '_')
        
        # Create the .pbix file with data and visualizations
        pbix_path = create_powerbi_template_pbix(
            df=df_final,
            charts=charts,
            dataset_name=dataset_name
        )
        
        # Send file for download
        return send_file(
            pbix_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'{dataset_name}_dashboard.pbix'
        )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Power BI generation error: {error_details}")
        
        return jsonify({
            'success': False,
            'error': f'Power BI file generation failed: {str(e)}',
            'details': 'Check server logs for more information'
        }), 500


# ============================================================================
# STEP 5: Analytics Page
# ============================================================================

@upload_bp.route('/analytics')
def analytics():
    """Show analytics dashboard page"""
    if 'upload_data' not in session or 'final_filepath' not in session['upload_data']:
        flash('No data available for analysis', 'error')
        return redirect(url_for('upload.upload_page'))
    
    return render_template('upload_analytics.html',
                         dataset_name=session['upload_data']['dataset_name'])

# ============================================================================
# AJAX API: Auto Mode Analytics
# ============================================================================

@upload_bp.route('/api/analyze-auto', methods=['POST'])
def analyze_auto():
    """Generate auto analytics (AJAX endpoint)"""
    if 'upload_data' not in session or 'final_filepath' not in session['upload_data']:
        return jsonify({'success': False, 'error': 'No data in session'}), 400
    
    try:
        upload_data = session['upload_data']
        df_final = pd.read_pickle(upload_data['final_filepath'])
        
        # Generate statistics
        stats = generate_summary_stats(df_final)
        
        # Generate charts
        charts = create_auto_charts(df_final)
        
        # Generate insights
        insights = generate_insights_text(stats)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'charts': charts,
            'insights': insights
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Auto analytics failed: {str(e)}'
        }), 500

# ============================================================================
# AJAX API: Prompt Mode Analytics
# ============================================================================

@upload_bp.route('/api/analyze-prompt', methods=['POST'])
def analyze_prompt():
    """Process natural language query (placeholder for LLM integration)"""
    if 'upload_data' not in session or 'final_filepath' not in session['upload_data']:
        return jsonify({'success': False, 'error': 'No data in session'}), 400
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # TODO: Integrate with LLM service (Gemini/OpenAI)
        # For now, return a placeholder response
        
        return jsonify({
            'success': True,
            'message': 'Prompt mode is in development. LLM integration coming soon!',
            'query': query
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# Legacy Route - Store to Database
# ============================================================================

@upload_bp.route('/api/save-to-database', methods=['POST'])
def save_to_database():
    """Store the final cleaned data to MySQL database"""
    if 'upload_data' not in session or 'final_filepath' not in session['upload_data']:
        return jsonify({'success': False, 'error': 'No data in session'}), 400
    
    try:
        upload_data = session['upload_data']
        
        # Load final data
        df_final = pd.read_pickle(upload_data['final_filepath'])
        
        # Create initial database record
        dataset_id = create_dataset(
            name=upload_data['dataset_name'],
            description='Uploaded and cleaned via AI Dashboard',
            file_path=upload_data['filepath'],
            file_type='csv',
            file_size=0,
            user_id=1,
            project_id=upload_data.get('project_id')  # Associate with project
        )
        
        if not dataset_id:
            return jsonify({'success': False, 'error': 'Failed to create dataset record'}), 500
        
        # Process and store in MySQL
        success, message, stats = process_and_store_dataset(
            filepath=upload_data['filepath'],
            dataset_name=upload_data['dataset_name'],
            dataset_id=dataset_id
        )
        
        if not success:
            execute_query(
                "UPDATE datasets SET status = 'failed' WHERE id = %s",
                params=(dataset_id,),
                fetch=False
            )
            return jsonify({'success': False, 'error': message}), 500
        
        # Update status to completed
        execute_query(
            "UPDATE datasets SET status = 'completed', rows = %s, columns = %s WHERE id = %s",
            params=(len(df_final), len(df_final.columns), dataset_id),
            fetch=False
        )
        
        # Get dashboard data from request (if provided)
        dashboard_data = request.get_json() if request.is_json else {}
        stats_data = dashboard_data.get('stats', {})
        charts_data = dashboard_data.get('charts', [])
        insights_data = dashboard_data.get('insights', [])
        
        # Create dashboard record if analytics data provided
        dashboard_id = None
        if stats_data or charts_data:
            from services.dashboard_service import create_dashboard
            
            dashboard_name = f"{upload_data['dataset_name']} - Auto Dashboard"
            dashboard_id = create_dashboard(
                name=dashboard_name,
                dataset_id=dataset_id,
                user_id=1,  # TODO: Get from session
                project_id=upload_data.get('project_id'),
                stats_data=stats_data,
                charts_data=charts_data,
                insights_data=insights_data,
                mode='auto'
            )
        
        # Store dashboard_id in session for redirect
        if dashboard_id:
            session['last_dashboard_id'] = dashboard_id
            session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Dataset and dashboard saved successfully',
            'dataset_id': dataset_id,
            'dashboard_id': dashboard_id,
            'stats': stats
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Storage failed: {str(e)}'
        }), 500
