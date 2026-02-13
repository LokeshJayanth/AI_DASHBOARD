"""
AI Prompts Service
Production-ready prompts for LLM-based analytics generation
Designed to prevent hallucinations and ensure Power BI compatibility
"""
import json
from typing import Dict, List, Any
import pandas as pd


def get_master_system_prompt() -> str:
    """
    Master system prompt - Use once to set context for the LLM
    
    Returns:
        str: System prompt for LLM
    """
    return """You are an expert Data Analyst and Business Intelligence Assistant.

You work with already cleaned datasets.
You must design analytics that are compatible with Power BI.

Rules:
- Use only the provided dataset columns
- Choose meaningful KPIs and charts
- Prefer business-friendly visuals
- Do NOT generate Power BI binary files
- Instead, describe visuals that can be built in Power BI

Output must be structured JSON only."""


def get_dataset_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract dataset schema for AI prompt
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        dict: Schema information including columns, types, and sample values
    """
    schema = {
        "columns": [],
        "total_rows": len(df),
        "total_columns": len(df.columns)
    }
    
    for col in df.columns:
        col_info = {
            "name": col,
            "type": str(df[col].dtype),
            "unique_values": int(df[col].nunique()),
            "null_count": int(df[col].isnull().sum()),
            "sample_values": df[col].dropna().head(3).tolist() if len(df[col].dropna()) > 0 else []
        }
        
        # Add numeric stats if applicable
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["min"] = float(df[col].min()) if pd.notna(df[col].min()) else None
            col_info["max"] = float(df[col].max()) if pd.notna(df[col].max()) else None
            col_info["mean"] = float(df[col].mean()) if pd.notna(df[col].mean()) else None
        
        schema["columns"].append(col_info)
    
    return schema


def get_auto_mode_prompt(dataset_schema: Dict[str, Any]) -> str:
    """
    Generate Auto Mode prompt for LLM
    
    Args:
        dataset_schema: Schema dictionary from get_dataset_schema()
        
    Returns:
        str: Complete prompt for auto analytics generation
    """
    schema_json = json.dumps(dataset_schema, indent=2)
    
    prompt = f"""Dataset schema:
{schema_json}

Automatically generate a complete analytics dashboard plan including:
1. KPI cards (4-6 cards)
2. Basic charts (bar, line, pie)
3. Medium-level charts (scatter, box plot, stacked bar)

For each visualization provide:
- visual_type (kpi, bar, line, pie, doughnut, scatter, box, stacked_bar)
- title (clear, business-friendly title)
- x_axis (column name for x-axis, if applicable)
- y_axis (column name for y-axis, if applicable)
- aggregation (count, sum, average, min, max, median)
- description (brief explanation of what this visual shows)

Return a JSON array.

Expected Output Example:
[
  {{
    "visual_type": "kpi",
    "title": "Total Employees",
    "aggregation": "count",
    "description": "Total number of records"
  }},
  {{
    "visual_type": "bar",
    "title": "Average Salary by Department",
    "x_axis": "department",
    "y_axis": "salary",
    "aggregation": "average",
    "description": "Shows average salary across different departments"
  }},
  {{
    "visual_type": "line",
    "title": "Employee Hiring Trend",
    "x_axis": "join_date",
    "y_axis": "employee_id",
    "aggregation": "count",
    "description": "Trend of employee hiring over time"
  }},
  {{
    "visual_type": "pie",
    "title": "Department Distribution",
    "x_axis": "department",
    "aggregation": "count",
    "description": "Percentage breakdown of employees by department"
  }}
]

Generate the JSON array now:"""
    
    return prompt


def get_prompt_mode_prompt(dataset_schema: Dict[str, Any], user_query: str) -> str:
    """
    Generate Prompt Mode prompt for LLM based on user's natural language query
    
    Args:
        dataset_schema: Schema dictionary from get_dataset_schema()
        user_query: User's natural language question
        
    Returns:
        str: Complete prompt for custom analytics generation
    """
    schema_json = json.dumps(dataset_schema, indent=2)
    
    prompt = f"""Dataset schema:
{schema_json}

User Question:
"{user_query}"

Based on the user's question, generate appropriate visualizations and analytics.

For each visualization provide:
- visual_type (kpi, bar, line, pie, doughnut, scatter, box, stacked_bar)
- title (clear, business-friendly title)
- x_axis (column name for x-axis, if applicable)
- y_axis (column name for y-axis, if applicable)
- aggregation (count, sum, average, min, max, median)
- description (brief explanation answering the user's question)

Return a JSON array.

Example Output:
[
  {{
    "visual_type": "bar",
    "title": "Average Salary by Department",
    "x_axis": "department",
    "y_axis": "salary",
    "aggregation": "average",
    "description": "This chart shows the average salary for each department"
  }}
]

Generate the JSON array now:"""
    
    return prompt


def get_powerbi_template_spec(dataset_schema: Dict[str, Any], visualizations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate Power BI template specification (not actual .pbix file)
    This creates a JSON spec that can be used to manually build Power BI dashboard
    
    Args:
        dataset_schema: Schema dictionary
        visualizations: List of visualization specs from AI
        
    Returns:
        dict: Power BI template specification
    """
    template = {
        "template_version": "1.0",
        "dataset_info": {
            "name": "AI Dashboard Dataset",
            "columns": [col["name"] for col in dataset_schema["columns"]],
            "total_rows": dataset_schema["total_rows"]
        },
        "recommended_visuals": [],
        "instructions": "Import your CSV/Excel file into Power BI Desktop, then create these visualizations:"
    }
    
    for idx, viz in enumerate(visualizations, 1):
        visual_spec = {
            "visual_number": idx,
            "type": viz.get("visual_type", "bar"),
            "title": viz.get("title", f"Visual {idx}"),
            "description": viz.get("description", ""),
            "configuration": {}
        }
        
        # Add axis configuration
        if viz.get("x_axis"):
            visual_spec["configuration"]["x_axis"] = viz["x_axis"]
        if viz.get("y_axis"):
            visual_spec["configuration"]["y_axis"] = viz["y_axis"]
        if viz.get("aggregation"):
            visual_spec["configuration"]["aggregation"] = viz["aggregation"]
        
        # Add Power BI specific instructions
        visual_spec["powerbi_steps"] = generate_powerbi_steps(viz)
        
        template["recommended_visuals"].append(visual_spec)
    
    return template


def generate_powerbi_steps(viz: Dict[str, Any]) -> List[str]:
    """
    Generate step-by-step instructions for creating a visual in Power BI
    
    Args:
        viz: Visualization specification
        
    Returns:
        list: Step-by-step instructions
    """
    visual_type = viz.get("visual_type", "bar")
    x_axis = viz.get("x_axis", "")
    y_axis = viz.get("y_axis", "")
    aggregation = viz.get("aggregation", "count")
    
    steps = []
    
    if visual_type == "kpi":
        steps = [
            "1. Add a 'Card' visual to the canvas",
            f"2. Drag the appropriate field to 'Fields'",
            f"3. Set aggregation to '{aggregation.upper()}'",
            "4. Format the card with title and styling"
        ]
    elif visual_type in ["bar", "column"]:
        steps = [
            "1. Add a 'Clustered Bar Chart' or 'Clustered Column Chart' visual",
            f"2. Drag '{x_axis}' to the X-axis",
            f"3. Drag '{y_axis}' to the Y-axis",
            f"4. Set Y-axis aggregation to '{aggregation.upper()}'",
            "5. Add data labels and format as needed"
        ]
    elif visual_type == "line":
        steps = [
            "1. Add a 'Line Chart' visual",
            f"2. Drag '{x_axis}' to the X-axis",
            f"3. Drag '{y_axis}' to the Y-axis",
            f"4. Set Y-axis aggregation to '{aggregation.upper()}'",
            "5. Enable data markers and format"
        ]
    elif visual_type in ["pie", "doughnut"]:
        steps = [
            f"1. Add a '{'Pie' if visual_type == 'pie' else 'Donut'}' chart visual",
            f"2. Drag '{x_axis}' to 'Legend'",
            "3. Drag the value field to 'Values'",
            f"4. Set aggregation to '{aggregation.upper()}'",
            "5. Enable data labels showing percentages"
        ]
    elif visual_type == "scatter":
        steps = [
            "1. Add a 'Scatter Chart' visual",
            f"2. Drag '{x_axis}' to X-axis",
            f"3. Drag '{y_axis}' to Y-axis",
            "4. Optionally add a third field to 'Size'",
            "5. Format markers and add trend line if needed"
        ]
    else:
        steps = [
            f"1. Add a '{visual_type}' visual to the canvas",
            "2. Configure fields according to your data",
            "3. Apply appropriate aggregations",
            "4. Format and style the visual"
        ]
    
    return steps


def validate_ai_response(response: List[Dict[str, Any]], dataset_schema: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate AI-generated visualizations against dataset schema
    Prevents hallucinations by checking if columns exist
    
    Args:
        response: AI-generated visualization list
        dataset_schema: Dataset schema
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(response, list):
        return False, "Response must be a JSON array"
    
    available_columns = [col["name"] for col in dataset_schema["columns"]]
    
    for idx, viz in enumerate(response):
        # Check required fields
        if "visual_type" not in viz:
            return False, f"Visual {idx + 1} missing 'visual_type'"
        
        if "title" not in viz:
            return False, f"Visual {idx + 1} missing 'title'"
        
        # Validate column references
        if "x_axis" in viz and viz["x_axis"]:
            if viz["x_axis"] not in available_columns:
                return False, f"Visual {idx + 1}: Column '{viz['x_axis']}' does not exist in dataset"
        
        if "y_axis" in viz and viz["y_axis"]:
            if viz["y_axis"] not in available_columns:
                return False, f"Visual {idx + 1}: Column '{viz['y_axis']}' does not exist in dataset"
    
    return True, "Validation passed"


def export_powerbi_template_json(template_spec: Dict[str, Any], filename: str = "powerbi_template.json") -> str:
    """
    Export Power BI template specification to JSON file
    
    Args:
        template_spec: Template specification dictionary
        filename: Output filename
        
    Returns:
        str: File path
    """
    import os
    import tempfile
    
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(template_spec, f, indent=2, ensure_ascii=False)
    
    return filepath
