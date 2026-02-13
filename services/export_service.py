"""
Export Service
Handles dataset export to various formats (CSV, Excel)
"""
import os
import pandas as pd
from datetime import datetime
from config import Config
from io import BytesIO

def export_to_csv(df, filename):
    """
    Export DataFrame to CSV with UTF-8 BOM for Excel compatibility
    
    Args:
        df: pandas DataFrame
        filename: desired filename (without extension)
    
    Returns:
        BytesIO object containing CSV data
    """
    output = BytesIO()
    # Add BOM for Excel compatibility
    output.write(b'\xef\xbb\xbf')
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output

def export_to_excel(df, filename):
    """
    Export DataFrame to Excel with formatting
    
    Args:
        df: pandas DataFrame
        filename: desired filename (without extension)
    
    Returns:
        BytesIO object containing Excel data
    """
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
        
        # Get the worksheet
        worksheet = writer.sheets['Data']
        
        # Auto-adjust column widths
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).str.len().max(),
                len(str(col))
            )
            # Add some padding
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[chr(65 + idx)].width = adjusted_width
    
    output.seek(0)
    return output

def save_to_local_folder(df, filename, file_format='csv'):
    """
    Save DataFrame to local downloads folder
    
    Args:
        df: pandas DataFrame
        filename: desired filename (without extension)
        file_format: 'csv' or 'excel'
    
    Returns:
        (success: bool, filepath: str or error: str)
    """
    try:
        # Create downloads directory if it doesn't exist
        downloads_dir = os.path.join(Config.BASE_DIR, 'downloads')
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if file_format == 'csv':
            filepath = os.path.join(downloads_dir, f"{filename}_{timestamp}.csv")
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        else:  # excel
            filepath = os.path.join(downloads_dir, f"{filename}_{timestamp}.xlsx")
            df.to_excel(filepath, index=False, engine='openpyxl')
        
        return True, filepath
    
    except Exception as e:
        return False, f"Error saving file: {str(e)}"

def get_download_filename(original_name, suffix='cleaned'):
    """
    Generate a clean download filename
    
    Args:
        original_name: original dataset name
        suffix: suffix to add (e.g., 'cleaned')
    
    Returns:
        cleaned filename
    """
    # Remove file extension if present
    base_name = os.path.splitext(original_name)[0]
    
    # Clean the name
    clean_name = base_name.lower().replace(' ', '_')
    
    # Add suffix
    return f"{clean_name}_{suffix}"
