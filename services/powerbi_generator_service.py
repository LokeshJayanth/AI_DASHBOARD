"""
Power BI File Generator Service
Creates actual .pbix files with embedded data and visualizations

Note: .pbix files are complex ZIP archives containing:
- DataModel (data + relationships)
- Report (layout + visuals)
- Metadata

This service creates a template-based .pbix file.
"""

import os
import json
import zipfile
import tempfile
import shutil
from typing import Dict, List, Any
import pandas as pd


def create_powerbi_layout(visualizations: List[Dict[str, Any]], dataset_name: str) -> Dict[str, Any]:
    """
    Create Power BI report layout JSON
    
    Args:
        visualizations: List of visualization specs
        dataset_name: Name of the dataset
        
    Returns:
        dict: Power BI layout configuration
    """
    
    # Power BI uses a specific JSON structure for layouts
    layout = {
        "name": f"{dataset_name} Dashboard",
        "displayName": f"{dataset_name} Dashboard",
        "pages": [
            {
                "name": "ReportSection",
                "displayName": "Dashboard",
                "width": 1280,
                "height": 720,
                "displayOption": 0,
                "visualContainers": []
            }
        ],
        "config": json.dumps({
            "layoutType": 1,
            "defaultLayout": {
                "displayOption": 1
            }
        })
    }
    
    # Position visuals in a grid
    x_positions = [0, 640, 0, 640, 0, 640]
    y_positions = [0, 0, 360, 360, 720, 720]
    
    for idx, viz in enumerate(visualizations[:6]):  # Limit to 6 visuals for clean layout
        visual_container = create_visual_container(viz, idx, x_positions[idx % 6], y_positions[idx % 6])
        layout["pages"][0]["visualContainers"].append(visual_container)
    
    return layout


def create_visual_container(viz: Dict[str, Any], index: int, x: int, y: int) -> Dict[str, Any]:
    """
    Create a visual container for Power BI
    
    Args:
        viz: Visualization specification
        index: Visual index
        x: X position
        y: Y position
        
    Returns:
        dict: Visual container configuration
    """
    
    visual_type = viz.get("visual_type", "bar")
    
    # Map our visual types to Power BI visual types
    powerbi_visual_map = {
        "kpi": "card",
        "bar": "clusteredBarChart",
        "line": "lineChart",
        "pie": "pieChart",
        "doughnut": "donutChart",
        "scatter": "scatterChart",
        "stacked_bar": "clusteredColumnChart"
    }
    
    pbi_visual_type = powerbi_visual_map.get(visual_type, "clusteredBarChart")
    
    container = {
        "x": x,
        "y": y,
        "z": index * 1000,
        "width": 640,
        "height": 360,
        "config": json.dumps({
            "name": f"visual_{index}",
            "title": viz.get("title", f"Visual {index + 1}"),
            "singleVisual": {
                "visualType": pbi_visual_type,
                "projections": create_projections(viz),
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "d", "Entity": "Data"}]
                }
            }
        })
    }
    
    return container


def create_projections(viz: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create field projections for Power BI visual
    
    Args:
        viz: Visualization specification
        
    Returns:
        dict: Projections configuration
    """
    
    projections = {}
    
    if viz.get("x_axis"):
        projections["Category"] = [{
            "queryRef": f"Data.{viz['x_axis']}"
        }]
    
    if viz.get("y_axis"):
        aggregation = viz.get("aggregation", "Sum").capitalize()
        projections["Values"] = [{
            "queryRef": f"Data.{viz['y_axis']}",
            "aggregation": aggregation
        }]
    
    return projections


def create_data_model(df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
    """
    Create Power BI data model
    
    Args:
        df: DataFrame with data
        dataset_name: Name of the dataset
        
    Returns:
        dict: Data model configuration
    """
    
    # Create table schema
    columns = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        
        # Map pandas dtypes to Power BI types
        if 'int' in dtype:
            pbi_type = "Int64"
        elif 'float' in dtype:
            pbi_type = "Double"
        elif 'datetime' in dtype:
            pbi_type = "DateTime"
        else:
            pbi_type = "String"
        
        columns.append({
            "name": col,
            "dataType": pbi_type,
            "sourceColumn": col
        })
    
    data_model = {
        "name": "SemanticModel",
        "tables": [
            {
                "name": "Data",
                "columns": columns,
                "partitions": [
                    {
                        "name": "Partition",
                        "mode": "import",
                        "source": {
                            "type": "m",
                            "expression": f"let Source = Csv.Document(File.Contents(\"{dataset_name}.csv\")) in Source"
                        }
                    }
                ]
            }
        ]
    }
    
    return data_model


def create_pbix_file(
    df: pd.DataFrame,
    visualizations: List[Dict[str, Any]],
    dataset_name: str,
    output_path: str = None
) -> str:
    """
    Create a .pbix file with data and visualizations
    
    Args:
        df: DataFrame with data
        visualizations: List of visualization specs
        dataset_name: Name of the dataset
        output_path: Optional output path
        
    Returns:
        str: Path to created .pbix file
    """
    
    # Create temporary directory for .pbix contents
    temp_dir = tempfile.mkdtemp()
    
    try:
        # .pbix is a ZIP file with specific structure
        # Create the required folders
        os.makedirs(os.path.join(temp_dir, "DataModelSchema"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "Report"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "DiagramLayout"), exist_ok=True)
        
        # 1. Create DataModelSchema (data model definition)
        data_model = create_data_model(df, dataset_name)
        with open(os.path.join(temp_dir, "DataModelSchema", "model.bim"), 'w', encoding='utf-8') as f:
            json.dump(data_model, f, indent=2)
        
        # 2. Create Report layout
        layout = create_powerbi_layout(visualizations, dataset_name)
        with open(os.path.join(temp_dir, "Report", "Layout"), 'w', encoding='utf-8') as f:
            json.dump(layout, f, indent=2)
        
        # 3. Create Version file
        version_info = {
            "version": "1.0",
            "powerBIVersion": "2.0"
        }
        with open(os.path.join(temp_dir, "Version"), 'w') as f:
            json.dump(version_info, f)
        
        # 4. Embed the data as CSV
        csv_path = os.path.join(temp_dir, f"{dataset_name}.csv")
        df.to_csv(csv_path, index=False)
        
        # 5. Create the .pbix file (ZIP archive)
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), f"{dataset_name}_dashboard.pbix")
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files to the ZIP
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        return output_path
    
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def create_powerbi_template_pbix(
    df: pd.DataFrame,
    charts: List[Dict[str, Any]],
    dataset_name: str
) -> str:
    """
    High-level function to create Power BI file from analytics
    
    Args:
        df: DataFrame with cleaned data
        charts: Chart configurations from auto_analytics_service
        dataset_name: Name of the dataset
        
    Returns:
        str: Path to created .pbix file
    """
    
    # Convert chart configs to visualization specs
    visualizations = []
    
    for chart in charts:
        viz_spec = {
            "visual_type": chart.get("type", "bar"),
            "title": chart.get("title", "Chart"),
            "x_axis": extract_x_axis_from_chart(chart),
            "y_axis": extract_y_axis_from_chart(chart),
            "aggregation": "sum",
            "description": chart.get("title", "")
        }
        visualizations.append(viz_spec)
    
    # Create the .pbix file
    pbix_path = create_pbix_file(df, visualizations, dataset_name)
    
    return pbix_path


def extract_x_axis_from_chart(chart: Dict[str, Any]) -> str:
    """Extract x-axis column from chart data"""
    if "data" in chart and "labels" in chart["data"]:
        # Try to infer from chart structure
        # This is a simplified extraction
        return "category"
    return ""


def extract_y_axis_from_chart(chart: Dict[str, Any]) -> str:
    """Extract y-axis column from chart data"""
    if "data" in chart and "datasets" in chart["data"]:
        datasets = chart["data"]["datasets"]
        if datasets and len(datasets) > 0:
            label = datasets[0].get("label", "")
            # Try to extract column name from label
            return label.lower().replace(" ", "_")
    return "value"


# Note: This is a simplified implementation
# Real .pbix files have more complex structure including:
# - Binary data model (VertiPaq engine)
# - Custom visuals
# - Themes and formatting
# - Relationships and measures
# - DAX expressions

# For production use, consider:
# 1. Using Power BI REST API
# 2. Power BI Embedded
# 3. Pre-built template files that you modify
