"""
Workflow Routes
Handles the complete data workflow: Upload → Clean → Select → Download → Analyze
"""
from flask import Blueprint, render_template, request, jsonify, session, send_file, redirect, url_for
import pandas as pd
import os
from werkzeug.utils import secure_filename
from config import Config
from services.file_service import clean_dataframe, save_uploaded_file
from services.data_cleaning_service import read_file
from services.export_service import export_to_csv, export_to_excel, get_download_filename, save_to_local_folder
from services.auto_analytics_service import generate_summary_stats, create_auto_charts, generate_insights_text

workflow_bp = Blueprint('workflow', __name__)

@workflow_bp.route('/')
def workflow_start():
    """Landing page for workflow"""
    # Clear any existing session data
    session.pop('workflow_data', None)
    return render_template('workflow_start.html')

@workflow_bp.route('/upload', methods=['POST'])
def upload_and_preview():
    """Upload file and show raw preview"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    dataset_name = request.form.get('name', file.filename)
    
    try:
        # Save the file temporarily
        file_info, error = save_uploaded_file(file)
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # Read the file into DataFrame
        df_raw, error = read_file(file_info['filepath'])
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # Store raw data in session (as JSON for serialization)
        session['workflow_data'] = {
            'dataset_name': dataset_name,
            'filepath': file_info['filepath'],
            'raw_data': df_raw.to_json(orient='split', date_format='iso'),
            'columns': df_raw.columns.tolist()
        }
        
        # Get preview data (first 10 rows)
        preview_html = df_raw.head(10).to_html(classes='data-table', index=False, border=0)
        
        # Get basic stats
        stats = {
            'rows': len(df_raw),
            'columns': len(df_raw.columns),
            'null_counts': df_raw.isnull().sum().to_dict(),
            'duplicates': df_raw.duplicated().sum()
        }
        
        return render_template('raw_preview.html', 
                             dataset_name=dataset_name,
                             preview=preview_html,
                             stats=stats)
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'}), 500

@workflow_bp.route('/clean', methods=['POST'])
def auto_clean():
    """Apply auto-cleaning and show cleaned preview"""
    if 'workflow_data' not in session:
        return redirect(url_for('workflow.workflow_start'))
    
    try:
        # Load raw data from session
        workflow_data = session['workflow_data']
        df_raw = pd.read_json(workflow_data['raw_data'], orient='split')
        
        # Apply cleaning
        df_clean = clean_dataframe(df_raw)
        
        # Update session with cleaned data
        session['workflow_data']['cleaned_data'] = df_clean.to_json(orient='split', date_format='iso')
        session['workflow_data']['cleaned_columns'] = df_clean.columns.tolist()
        session.modified = True
        
        # Get preview
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
        
        return render_template('cleaned_preview.html',
                             dataset_name=workflow_data['dataset_name'],
                             preview=preview_html,
                             columns=df_clean.columns.tolist(),
                             stats=stats)
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Cleaning failed: {str(e)}'}), 500

@workflow_bp.route('/select-columns', methods=['POST'])
def select_columns():
    """Handle column selection and prepare for download"""
    if 'workflow_data' not in session:
        return redirect(url_for('workflow.workflow_start'))
    
    try:
        selected_columns = request.form.getlist('columns')
        
        if not selected_columns:
            return jsonify({'success': False, 'error': 'Please select at least one column'}), 400
        
        # Load cleaned data
        workflow_data = session['workflow_data']
        df_clean = pd.read_json(workflow_data['cleaned_data'], orient='split')
        
        # Filter to selected columns
        df_final = df_clean[selected_columns]
        
        # Update session with final data
        session['workflow_data']['final_data'] = df_final.to_json(orient='split', date_format='iso')
        session['workflow_data']['selected_columns'] = selected_columns
        session.modified = True
        
        return render_template('download_ready.html',
                             dataset_name=workflow_data['dataset_name'],
                             rows=len(df_final),
                             columns=len(selected_columns))
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Column selection failed: {str(e)}'}), 500

@workflow_bp.route('/download/csv')
def download_csv():
    """Download cleaned dataset as CSV"""
    if 'workflow_data' not in session or 'final_data' not in session['workflow_data']:
        return redirect(url_for('workflow.workflow_start'))
    
    try:
        workflow_data = session['workflow_data']
        df_final = pd.read_json(workflow_data['final_data'], orient='split')
        
        # Generate filename
        filename = get_download_filename(workflow_data['dataset_name'], 'cleaned')
        
        # Also save to local downloads folder
        save_to_local_folder(df_final, filename, 'csv')
        
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

@workflow_bp.route('/download/excel')
def download_excel():
    """Download cleaned dataset as Excel"""
    if 'workflow_data' not in session or 'final_data' not in session['workflow_data']:
        return redirect(url_for('workflow.workflow_start'))
    
    try:
        workflow_data = session['workflow_data']
        df_final = pd.read_json(workflow_data['final_data'], orient='split')
        
        # Generate filename
        filename = get_download_filename(workflow_data['dataset_name'], 'cleaned')
        
        # Also save to local downloads folder
        save_to_local_folder(df_final, filename, 'excel')
        
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

@workflow_bp.route('/mode-selection')
def mode_selection():
    """Show mode selection page (Auto vs Prompt)"""
    if 'workflow_data' not in session or 'final_data' not in session['workflow_data']:
        return redirect(url_for('workflow.workflow_start'))
    
    return render_template('mode_selection.html',
                         dataset_name=session['workflow_data']['dataset_name'])

@workflow_bp.route('/auto-mode')
def auto_mode():
    """Auto-generated analytics dashboard"""
    if 'workflow_data' not in session or 'final_data' not in session['workflow_data']:
        return redirect(url_for('workflow.workflow_start'))
    
    try:
        workflow_data = session['workflow_data']
        df_final = pd.read_json(workflow_data['final_data'], orient='split')
        
        # Generate statistics
        stats = generate_summary_stats(df_final)
        
        # Generate charts
        charts = create_auto_charts(df_final)
        
        # Generate insights
        insights = generate_insights_text(stats)
        
        return render_template('auto_mode.html',
                             dataset_name=workflow_data['dataset_name'],
                             stats=stats,
                             charts=charts,
                             insights=insights)
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Auto mode failed: {str(e)}'}), 500

@workflow_bp.route('/prompt-mode')
def prompt_mode():
    """LLM-based prompt analytics"""
    if 'workflow_data' not in session or 'final_data' not in session['workflow_data']:
        return redirect(url_for('workflow.workflow_start'))
    
    workflow_data = session['workflow_data']
    df_final = pd.read_json(workflow_data['final_data'], orient='split')
    
    # Get column info for context
    columns_info = {
        'columns': df_final.columns.tolist(),
        'types': {col: str(df_final[col].dtype) for col in df_final.columns}
    }
    
    return render_template('prompt_mode.html',
                         dataset_name=workflow_data['dataset_name'],
                         columns_info=columns_info)

@workflow_bp.route('/api/query', methods=['POST'])
def process_query():
    """Process natural language query (placeholder for LLM integration)"""
    if 'workflow_data' not in session or 'final_data' not in session['workflow_data']:
        return jsonify({'success': False, 'error': 'No data in session'}), 400
    
    try:
        query = request.json.get('query', '')
        
        # TODO: Integrate with LLM service (Gemini/OpenAI)
        # For now, return a placeholder response
        
        return jsonify({
            'success': True,
            'message': 'Prompt mode is in development. LLM integration coming soon!',
            'query': query
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
