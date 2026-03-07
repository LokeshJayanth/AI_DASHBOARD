"""
Test Routes for Direct Workflow Step Access
Allows testing specific workflow steps by pre-populating session data
"""
from flask import Blueprint, session, redirect, url_for
import pandas as pd

test_bp = Blueprint('test', __name__)

@test_bp.route('/test/step4')
def test_step4():
    """
    Directly test Step 4 (Download Ready) by pre-populating session
    """
    # Create sample data
    sample_data = pd.DataFrame({
        'age': [25, 30, 35, 28, 45],
        'gender': ['M', 'F', 'M', 'F', 'M'],
        'salary': [50000, 60000, 70000, 52000, 85000],
        'department': ['IT', 'HR', 'Sales', 'IT', 'Sales']
    })
    
    # Populate session with required data for Step 4
    session['workflow_data'] = {
        'dataset_name': 'Test Dataset',
        'final_data': sample_data.to_json(orient='split', date_format='iso'),
        'selected_columns': list(sample_data.columns)
    }
    
    # Redirect to download ready page (Step 4)
    from flask import render_template
    return render_template('download_ready.html',
                         dataset_name='Test Dataset',
                         rows=len(sample_data),
                         columns=len(sample_data.columns))

@test_bp.route('/test/step5')
def test_step5():
    """
    Directly test Step 5 (Mode Selection) by pre-populating session
    """
    # Create sample data
    sample_data = pd.DataFrame({
        'age': [25, 30, 35, 28, 45],
        'gender': ['M', 'F', 'M', 'F', 'M'],
        'salary': [50000, 60000, 70000, 52000, 85000],
        'department': ['IT', 'HR', 'Sales', 'IT', 'Sales']
    })
    
    # Populate session with required data
    session['workflow_data'] = {
        'dataset_name': 'Test Dataset',
        'final_data': sample_data.to_json(orient='split', date_format='iso'),
        'selected_columns': list(sample_data.columns)
    }
    
    # Redirect to mode selection
    return redirect(url_for('workflow.mode_selection'))

@test_bp.route('/test/step6-auto')
def test_step6_auto():
    """
    Directly test Step 6a (Auto Mode) by pre-populating session
    """
    # Create sample data
    sample_data = pd.DataFrame({
        'age': [25, 30, 35, 28, 45, 32, 27, 38, 42, 29],
        'gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
        'salary': [50000, 60000, 70000, 52000, 85000, 58000, 48000, 75000, 90000, 55000],
        'department': ['IT', 'HR', 'Sales', 'IT', 'Sales', 'HR', 'IT', 'Sales', 'IT', 'HR']
    })
    
    # Populate session with required data
    session['workflow_data'] = {
        'dataset_name': 'Test Dataset',
        'final_data': sample_data.to_json(orient='split', date_format='iso'),
        'selected_columns': list(sample_data.columns)
    }
    
    # Redirect to auto mode
    return redirect(url_for('workflow.auto_mode'))

@test_bp.route('/test/step6-prompt')
def test_step6_prompt():
    """
    Directly test Step 6b (Prompt Mode) by pre-populating session
    """
    # Create sample data
    sample_data = pd.DataFrame({
        'age': [25, 30, 35, 28, 45, 32, 27, 38, 42, 29],
        'gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
        'salary': [50000, 60000, 70000, 52000, 85000, 58000, 48000, 75000, 90000, 55000],
        'department': ['IT', 'HR', 'Sales', 'IT', 'Sales', 'HR', 'IT', 'Sales', 'IT', 'HR']
    })
    
    # Populate session with required data
    session['workflow_data'] = {
        'dataset_name': 'Test Dataset',
        'final_data': sample_data.to_json(orient='split', date_format='iso'),
        'selected_columns': list(sample_data.columns)
    }
    
    # Redirect to prompt mode
    return redirect(url_for('workflow.prompt_mode'))
