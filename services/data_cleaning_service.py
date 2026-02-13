"""
Data Cleaning Service
Handles data cleaning, validation, and storage to MySQL
"""
import pandas as pd
import numpy as np
from datetime import datetime
from services.db_service import get_db_connection, execute_query
from services.file_service import (
    clean_dataframe, 
    generate_table_name, 
    create_table_schema
)

def process_and_store_dataset(filepath, dataset_name, dataset_id):
    """
    Main function to process uploaded file and store in MySQL
    
    Args:
        filepath: Path to uploaded file
        dataset_name: User-provided name for dataset
        dataset_id: Database ID for this dataset
    
    Returns:
        (success: bool, message: str, stats: dict)
    """
    try:
        # 1. Read the file
        df, error = read_file(filepath)
        if error:
            return False, error, None
        
        # 2. Clean the dataframe
        df_clean = clean_dataframe(df)
        
        # 3. Generate table name
        table_name = generate_table_name(dataset_name)
        
        # 4. Create table schema
        create_sql = create_table_schema(df_clean, table_name)
        
        # 5. Create the table in MySQL
        success = execute_query(create_sql, fetch=False)
        if success is None:
            return False, "Failed to create table in database", None
        
        # 6. Insert data into table
        rows_inserted = insert_dataframe_to_mysql(df_clean, table_name)
        
        # 7. Update datasets table with table name
        update_sql = "UPDATE datasets SET table_name = %s WHERE id = %s"
        execute_query(update_sql, params=(table_name, dataset_id), fetch=False)
        
        # 8. Generate statistics
        stats = {
            'rows': len(df_clean),
            'columns': len(df_clean.columns),
            'column_names': list(df_clean.columns),
            'table_name': table_name,
            'rows_inserted': rows_inserted,
            'data_types': {col: str(df_clean[col].dtype) for col in df_clean.columns}
        }
        
        return True, "Dataset processed and stored successfully", stats
    
    except Exception as e:
        return False, f"Error processing dataset: {str(e)}", None

def read_file(filepath):
    """Read various file formats into DataFrame"""
    try:
        ext = filepath.lower().split('.')[-1]
        
        if ext == 'csv':
            df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
        elif ext in ['xlsx', 'xls']:
            df = pd.read_excel(filepath, engine='openpyxl' if ext == 'xlsx' else None)
        elif ext == 'json':
            df = pd.read_json(filepath)
        elif ext == 'txt':
            # Try to read as CSV with tab or comma delimiter
            try:
                df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
            except:
                df = pd.read_csv(filepath, encoding='utf-8')
        else:
            return None, f"Unsupported file format: {ext}"
        
        if df.empty:
            return None, "File is empty"
        
        return df, None
    
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def insert_dataframe_to_mysql(df, table_name):
    """Insert DataFrame rows into MySQL table - BI optimized"""
    try:
        connection = get_db_connection()
        if not connection:
            return 0
        
        cursor = connection.cursor()
        
        # Prepare column names
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        
        # Prepare INSERT query
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Convert DataFrame to list of tuples
        rows = []
        for _, row in df.iterrows():
            # Convert numpy/pandas types to Python native types
            row_values = []
            for val in row:
                if pd.isna(val) or val is None:
                    row_values.append(None)
                elif isinstance(val, (pd.Timestamp)):
                    # Pandas Timestamp - convert to ISO date string (YYYY-MM-DD)
                    row_values.append(val.strftime('%Y-%m-%d'))
                elif isinstance(val, (np.integer, np.floating)):
                    # Convert to int or float
                    if isinstance(val, np.floating):
                        # Check if it's actually an integer
                        if val.is_integer():
                            row_values.append(int(val))
                        else:
                            row_values.append(float(val))
                    else:
                        row_values.append(int(val))
                elif str(type(val)) == "<class 'pandas._libs.missing.NAType'>":
                    # Handle pandas NA
                    row_values.append(None)
                else:
                    row_values.append(str(val))
            rows.append(tuple(row_values))
        
        # Execute batch insert
        cursor.executemany(insert_sql, rows)
        connection.commit()
        
        rows_inserted = cursor.rowcount
        
        cursor.close()
        connection.close()
        
        return rows_inserted
    
    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        return 0

def get_dataset_preview(table_name, limit=10):
    """Get preview of dataset from MySQL"""
    try:
        query = f"SELECT * FROM `{table_name}` LIMIT {limit}"
        result = execute_query(query, fetch=True)
        print(f"Preview query: {query}")
        print(f"Preview result count: {len(result) if result else 0}")
        return result if result else []
    except Exception as e:
        print(f"Error getting preview from {table_name}: {str(e)}")
        return []

def get_dataset_statistics(table_name):
    """Get statistics about the dataset"""
    try:
        # Get row count
        count_query = f"SELECT COUNT(*) as total FROM {table_name}"
        count_result = execute_query(count_query, fetch=True)
        total_rows = count_result[0]['total'] if count_result else 0
        
        # Get column info
        column_query = f"DESCRIBE {table_name}"
        columns = execute_query(column_query, fetch=True)
        
        return {
            'total_rows': total_rows,
            'columns': columns,
            'column_count': len(columns) - 2  # Exclude id and uploaded_at
        }
    except Exception as e:
        print(f"Error getting statistics: {str(e)}")
        return None
