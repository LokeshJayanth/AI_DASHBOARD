"""
File Service
Handles file operations, data cleaning, and type detection
"""
import os
import re
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
from config import Config

def save_uploaded_file(file):
    """Save an uploaded file securely and return file info"""
    if not file or file.filename == '':
        return None, "No file selected"
    
    if not Config.allowed_file(file.filename):
        return None, "File type not allowed"
    
    # Create upload directory if it doesn't exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Generate unique filename if file already exists
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(Config.UPLOAD_FOLDER, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    
    # Save the file
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Get file info
    file_size = os.path.getsize(filepath)
    file_type = ext.lstrip('.')
    
    return {
        'filename': filename,
        'filepath': filepath,
        'file_size': file_size,
        'file_type': file_type
    }, None

def clean_column_name(col_name):
    """Clean column names for MySQL compatibility"""
    # Remove special characters, convert to lowercase
    col_name = str(col_name).strip().lower()
    col_name = re.sub(r'[^\w\s]', '', col_name)  # Remove special chars
    col_name = re.sub(r'\s+', '_', col_name)  # Replace spaces with underscores
    
    # Ensure it doesn't start with a number
    if col_name and col_name[0].isdigit():
        col_name = 'col_' + col_name
    
    return col_name[:64]  # MySQL column name limit

def detect_data_type(series):
    """Detect appropriate MySQL data type for a pandas Series - BI optimized"""
    # Remove null values for analysis
    series_clean = series.dropna()
    
    if len(series_clean) == 0:
        return 'TEXT'
    
    # Check for datetime64 types
    if pd.api.types.is_datetime64_any_dtype(series):
        return 'DATE'
    
    # Check for Int64 (pandas nullable integer)
    if pd.api.types.is_integer_dtype(series) or str(series.dtype) == 'Int64':
        max_val = series_clean.max() if len(series_clean) > 0 else 0
        if max_val < 128:
            return 'TINYINT'
        elif max_val < 32768:
            return 'SMALLINT'
        elif max_val < 2147483648:
            return 'INT'
        else:
            return 'BIGINT'
    
    elif pd.api.types.is_float_dtype(series_clean):
        # Check if actually integers stored as floats
        if series_clean.apply(lambda x: x.is_integer() if pd.notna(x) else True).all():
            return 'INT'
        return 'DECIMAL(10,2)'
    
    elif pd.api.types.is_bool_dtype(series_clean):
        return 'BOOLEAN'
    
    else:
        # String type - determine appropriate VARCHAR length
        max_length = series_clean.astype(str).str.len().max()
        # Ensure max_length is numeric (handle NaN, None cases)
        if pd.isna(max_length) or max_length is None:
            max_length = 50
        else:
            max_length = int(max_length)
        
        if max_length <= 255:
            return f'VARCHAR({min(255, int(max_length * 1.5))})'
        else:
            return 'TEXT'

def clean_dataframe(df):
    """
    🔥 UNIVERSAL DATA CLEANING ENGINE - Industry Level
    Handles ALL possible data quality issues for ANY dataset
    
    Covers 20+ cleaning scenarios:
    - Missing values (NULL, NaN, empty strings)
    - Wrong datatypes (text in numeric columns)
    - Invalid numeric values (negative, outliers)
    - Duplicate rows and columns
    - Date formatting and validation
    - Categorical value standardization
    - Special characters in column names
    - Encoding issues
    - Column-specific validation rules
    """
    
    df_clean = df.copy()
    
    # ============================================
    # 🔹 STEP 1: Clean Column Names
    # ============================================
    # Remove special characters, convert to lowercase snake_case
    df_clean.columns = df_clean.columns.str.strip().str.lower()
    df_clean.columns = df_clean.columns.str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)
    df_clean.columns = df_clean.columns.str.replace(r'_+', '_', regex=True)  # Remove multiple underscores
    df_clean.columns = df_clean.columns.str.strip('_')  # Remove leading/trailing underscores
    
    # Handle duplicate column names
    cols = df_clean.columns.tolist()
    seen = {}
    new_cols = []
    for col in cols:
        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)
    df_clean.columns = new_cols
    
    # ============================================
    # 🔹 STEP 2: Remove Completely Empty Rows/Columns
    # ============================================
    df_clean.dropna(how='all', axis=0, inplace=True)  # Empty rows
    df_clean.dropna(axis=1, how='all', inplace=True)  # Empty columns
    
    # ============================================
    # 🔹 STEP 3: Replace Various NULL Representations
    # ============================================
    null_values = ["", " ", "  ", "NULL", "null", "Null", "NaN", "nan", "N/A", "n/a", "#N/A", "NA", "None", "none", "-", "--", "?"]
    df_clean.replace(null_values, np.nan, inplace=True)
    
    # 🔥 CRITICAL: Convert ALL string variations of 'nan' to actual NaN
    # This catches cases where pandas reads 'nan' as a string from CSV
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':  # Only for text columns
            df_clean[col] = df_clean[col].replace('nan', np.nan)
            df_clean[col] = df_clean[col].replace('NaN', np.nan)
            df_clean[col] = df_clean[col].replace('NAN', np.nan)
            df_clean[col] = df_clean[col].replace('None', np.nan)
            df_clean[col] = df_clean[col].replace('NONE', np.nan)
            df_clean[col] = df_clean[col].replace('null', np.nan)
            df_clean[col] = df_clean[col].replace('NULL', np.nan)
    
    # ============================================
    # 🔹 STEP 4: Strip Whitespace from All Text Columns
    # ============================================
    for col in df_clean.select_dtypes(include=['object']).columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()
    
    # ============================================
    # 🔹 STEP 5: Convert Numeric Columns Properly
    # ============================================
    for col in df_clean.columns:
        # Try to convert to numeric - use 'coerce' to turn invalid values to NaN
        numeric_col = pd.to_numeric(df_clean[col], errors='coerce')
        
        # If more than 50% values could be converted, treat as numeric
        if numeric_col.notna().sum() > len(df_clean) * 0.5:
            df_clean[col] = numeric_col
    
    # ============================================
    # 🔹 STEP 6: COLUMN-SPECIFIC CLEANING RULES
    # ============================================
    
    # AGE Column - Must be 1-100, remove outliers
    if "age" in df_clean.columns:
        df_clean["age"] = pd.to_numeric(df_clean["age"], errors="coerce")
        # Remove invalid ages (negative, zero, or > 100)
        df_clean.loc[(df_clean["age"] <= 0) | (df_clean["age"] > 100), "age"] = np.nan
        # Fill with median
        if df_clean["age"].notna().any():
            df_clean["age"].fillna(df_clean["age"].median(), inplace=True)
    
    # SALARY Column - Must be positive, remove text values
    if "salary" in df_clean.columns:
        df_clean["salary"] = pd.to_numeric(df_clean["salary"], errors="coerce")
        # Remove negative or zero salaries
        df_clean.loc[df_clean["salary"] <= 0, "salary"] = np.nan
        # Fill with median
        if df_clean["salary"].notna().any():
            df_clean["salary"].fillna(df_clean["salary"].median(), inplace=True)
    
    # PRICE / AMOUNT Columns - Must be positive
    for col in df_clean.columns:
        if any(keyword in col.lower() for keyword in ['price', 'amount', 'cost', 'revenue', 'sales']):
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            # Remove negative values
            df_clean.loc[df_clean[col] < 0, col] = np.nan
            # Fill with median
            if df_clean[col].notna().any():
                df_clean[col].fillna(df_clean[col].median(), inplace=True)
    
    # QUANTITY / COUNT Columns - Must be positive integers
    for col in df_clean.columns:
        if any(keyword in col.lower() for keyword in ['quantity', 'count', 'qty', 'units']):
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            # Remove negative or zero quantities
            df_clean.loc[df_clean[col] <= 0, col] = 1
            # Round to integers
            df_clean[col] = df_clean[col].round().astype('Int64')
    
    # PERCENTAGE Columns - Must be 0-100
    for col in df_clean.columns:
        if any(keyword in col.lower() for keyword in ['percent', 'percentage', 'pct', 'rate']):
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            # Clip to 0-100 range
            df_clean.loc[df_clean[col] < 0, col] = 0
            df_clean.loc[df_clean[col] > 100, col] = 100
    
    # MARKS / SCORE Columns - Must be 0-100
    for col in df_clean.columns:
        if any(keyword in col.lower() for keyword in ['marks', 'score', 'grade']):
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            # Remove invalid marks (negative or > 100)
            df_clean.loc[df_clean[col] < 0, col] = np.nan
            df_clean.loc[df_clean[col] > 100, col] = np.nan
            # Remove zero marks (usually indicates missing data, not actual zero score)
            df_clean = df_clean[df_clean[col] > 0]
    
    # GENDER Column - Standardize values
    if "gender" in df_clean.columns:
        df_clean["gender"] = df_clean["gender"].str.lower().str.strip()
        # Standardize variations
        gender_mapping = {
            'm': 'male',
            'f': 'female',
            'male': 'male',
            'female': 'female',
            'man': 'male',
            'woman': 'female',
            'boy': 'male',
            'girl': 'female'
        }
        df_clean["gender"] = df_clean["gender"].replace(gender_mapping)
        # Replace "unknown" with NaN, then fill with mode
        df_clean["gender"].replace("unknown", np.nan, inplace=True)
        if df_clean["gender"].notna().any() and not df_clean["gender"].mode().empty:
            df_clean["gender"].fillna(df_clean["gender"].mode()[0], inplace=True)
        else:
            df_clean["gender"].fillna("Not Specified", inplace=True)
    
    # CITY Column - Use mode instead of Unknown
    if "city" in df_clean.columns:
        df_clean["city"].replace("unknown", np.nan, inplace=True)
        # Fill with most common city
        if df_clean["city"].notna().any() and not df_clean["city"].mode().empty:
            df_clean["city"].fillna(df_clean["city"].mode()[0], inplace=True)
        else:
            df_clean["city"].fillna("Not Available", inplace=True)
    
    # NAME Column - Fill with placeholder
    if "name" in df_clean.columns:
        df_clean["name"].fillna("Not Provided", inplace=True)
    
    # STUDENT_NAME / CUSTOMER_NAME / EMPLOYEE_NAME - Fill with placeholder
    for col in df_clean.columns:
        if 'name' in col.lower() and col.lower() != 'name':
            # Already converted string 'nan' in Step 3, just fill NaN values
            if df_clean[col].notna().any() and not df_clean[col].mode().empty:
                mode_val = df_clean[col].mode()[0]
                # Check if mode is valid
                if pd.notna(mode_val) and str(mode_val).lower() not in ['nan', 'none', 'null']:
                    df_clean[col].fillna(mode_val, inplace=True)
                else:
                    df_clean[col].fillna("Not Provided", inplace=True)
            else:
                df_clean[col].fillna("Not Provided", inplace=True)
    
    # DEPARTMENT Column - Critical for student/employee datasets, fill with mode
    if "department" in df_clean.columns:
        # Fill missing departments with most common department
        if df_clean["department"].notna().any() and not df_clean["department"].mode().empty:
            mode_dept = df_clean["department"].mode()[0]
            # Ensure mode is a valid department
            if pd.notna(mode_dept) and str(mode_dept).lower() not in ['nan', 'none', 'null', 'not available']:
                df_clean["department"].fillna(mode_dept, inplace=True)
            else:
                df_clean["department"].fillna("General", inplace=True)
        else:
            df_clean["department"].fillna("General", inplace=True)
    
    # DISEASE Column - Critical for medical/hospital datasets, fill with mode
    if "disease" in df_clean.columns:
        # Fill missing diseases with most common disease
        if df_clean["disease"].notna().any() and not df_clean["disease"].mode().empty:
            mode_disease = df_clean["disease"].mode()[0]
            # Ensure mode is a valid disease
            if pd.notna(mode_disease) and str(mode_disease).lower() not in ['nan', 'none', 'null', 'not available']:
                df_clean["disease"].fillna(mode_disease, inplace=True)
            else:
                df_clean["disease"].fillna("Unknown Disease", inplace=True)
        else:
            df_clean["disease"].fillna("Unknown Disease", inplace=True)
    
    # ROLL_NO / STUDENT_ID / EMPLOYEE_ID - Should not be NaN
    for col in df_clean.columns:
        if any(keyword in col.lower() for keyword in ['roll', 'roll_no', 'student_id', 'employee_id', 'id']):
            df_clean[col] = df_clean[col].replace('nan', np.nan)  # Convert string 'nan' to NaN
            # Drop rows with missing IDs (critical field)
            df_clean = df_clean[df_clean[col].notna()]
    
    # EMAIL Column - Validate format (basic)
    if "email" in df_clean.columns:
        # Replace invalid emails with NaN
        df_clean.loc[~df_clean["email"].str.contains('@', na=False), "email"] = np.nan
        df_clean["email"].fillna("Not Available", inplace=True)
    
    # PHONE Column - Remove non-digits, validate length
    for col in df_clean.columns:
        if any(keyword in col.lower() for keyword in ['phone', 'mobile', 'contact']):
            # Keep only digits
            df_clean[col] = df_clean[col].astype(str).str.replace(r'[^0-9]', '', regex=True)
            # Replace too short/long numbers with NaN
            df_clean.loc[df_clean[col].str.len() < 10, col] = np.nan
            df_clean[col].fillna("Not Available", inplace=True)
    
    # PRODUCT Column - Critical for sales datasets, fill with mode
    if "product" in df_clean.columns:
        # Fill missing products with most common product
        if df_clean["product"].notna().any() and not df_clean["product"].mode().empty:
            df_clean["product"].fillna(df_clean["product"].mode()[0], inplace=True)
        else:
            df_clean["product"].fillna("Unknown Product", inplace=True)
    
    # ============================================
    # 🔹 STEP 7: Handle Date Columns - Convert to ISO Format
    # ============================================
    for col in df_clean.columns:
        # Check if column might be a date
        if any(keyword in col.lower() for keyword in ['date', 'time', 'day', 'month', 'year', 'dob', 'birth']):
            try:
                # Try to parse as datetime
                dt_col = pd.to_datetime(df_clean[col], errors='coerce')
                
                # If at least 50% could be converted, it's a date column
                if dt_col.notna().sum() > len(df_clean) * 0.5:
                    # Fill missing dates with most common date (mode)
                    if dt_col.notna().any() and not dt_col.mode().empty:
                        dt_col.fillna(dt_col.mode()[0], inplace=True)
                    else:
                        # If all dates are NaN, use today's date
                        dt_col.fillna(pd.Timestamp.today(), inplace=True)
                    
                    # Convert to ISO format (YYYY-MM-DD)
                    df_clean[col] = dt_col.dt.strftime('%Y-%m-%d')
            except:
                pass
    
    # ============================================
    # 🔹 STEP 8: Fill Remaining Missing Values Intelligently
    # ============================================
    for col in df_clean.columns:
        # First convert string 'nan' to actual NaN for all columns
        if df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].replace('nan', np.nan)
            df_clean[col] = df_clean[col].replace('NaN', np.nan)
            df_clean[col] = df_clean[col].replace('None', np.nan)
        
        if df_clean[col].dtype in ['float64', 'int64', 'Int64']:
            # Numeric columns: fill with MEDIAN (better than mean for outliers)
            if df_clean[col].notna().any():
                df_clean[col].fillna(df_clean[col].median(), inplace=True)
            else:
                df_clean[col].fillna(0, inplace=True)
        else:
            # Text/categorical columns: fill with most common value (MODE)
            if df_clean[col].notna().any() and not df_clean[col].mode().empty:
                mode_value = df_clean[col].mode()[0]
                # Only use mode if it's not "nan" or similar
                if str(mode_value).lower() not in ['nan', 'none', 'not available']:
                    df_clean[col].fillna(mode_value, inplace=True)
                else:
                    df_clean[col].fillna("Not Available", inplace=True)
            else:
                df_clean[col].fillna("Not Available", inplace=True)
    
    # ============================================
    # 🔹 STEP 9: Remove Duplicate Rows
    # ============================================
    df_clean.drop_duplicates(inplace=True, keep='first')
    
    # ============================================
    # 🔹 STEP 10: Convert Float to Int Where Appropriate
    # ============================================
    for col in df_clean.select_dtypes(include=['float64']).columns:
        # Check if all values are whole numbers
        if df_clean[col].apply(lambda x: x.is_integer() if pd.notna(x) else True).all():
            df_clean[col] = df_clean[col].astype('Int64')  # Nullable integer type
    
    # ============================================
    # 🔹 STEP 11: Reset Index
    # ============================================
    df_clean.reset_index(drop=True, inplace=True)
    
    return df_clean

def generate_table_name(filename):
    """Generate a valid MySQL table name from filename"""
    # Remove extension and clean
    base_name = os.path.splitext(filename)[0]
    table_name = clean_column_name(base_name)
    
    # Ensure it's not a reserved word by adding prefix
    table_name = f"dataset_{table_name}"
    
    return table_name[:64]  # MySQL table name limit

def create_table_schema(df, table_name):
    """Generate CREATE TABLE SQL statement from DataFrame"""
    columns = []
    
    # Add auto-increment ID
    columns.append("id INT AUTO_INCREMENT PRIMARY KEY")
    
    # Add columns based on DataFrame
    for col in df.columns:
        data_type = detect_data_type(df[col])
        columns.append(f"{col} {data_type}")
    
    # Add timestamp
    columns.append("uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    
    # Fix: Move join outside f-string to avoid backslash issue
    column_defs = ',\n        '.join(columns)
    sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {column_defs}
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    return sql

def parse_dataset_file(filepath):
    """Parse uploaded dataset file and extract metadata"""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    try:
        if ext == '.csv':
            df = pd.read_csv(filepath)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
        elif ext == '.json':
            df = pd.read_json(filepath)
        else:
            return None, f"Cannot parse {ext} files yet"
        
        metadata = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'preview': df.head(5).to_dict('records')
        }
        
        return metadata, None
    except Exception as e:
        return None, f"Error parsing file: {str(e)}"

def get_file_preview(filepath, num_rows=10):
    """Get a preview of the file content"""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    try:
        if ext == '.csv':
            df = pd.read_csv(filepath, nrows=num_rows)
            return df.to_html(classes='table table-striped', index=False)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath, nrows=num_rows)
            return df.to_html(classes='table table-striped', index=False)
        elif ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [f.readline() for _ in range(num_rows)]
                return '<br>'.join(lines)
        else:
            return "Preview not available for this file type"
    except Exception as e:
        return f"Error generating preview: {str(e)}"

def delete_file(filepath):
    """Delete a file from the filesystem"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True, "File deleted successfully"
        return False, "File not found"
    except Exception as e:
        return False, f"Error deleting file: {str(e)}"
