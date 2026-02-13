"""
Test dashboard save functionality
"""
from services.dashboard_service import create_dashboard, get_user_dashboards

# Test data
test_stats = {
    'total_records': 50,
    'total_columns_count': 5,
    'average_salary': 70250.50,
    'median_salary': 70000.00,
    'min_salary': 50010.00,
    'max_salary': 80500.00
}

test_charts = [
    {
        'type': 'bar',
        'title': 'Salary by Department',
        'labels': ['Engineering', 'Marketing', 'Sales'],
        'data': [75000, 65000, 70000],
        'backgroundColor': ['#667eea', '#764ba2', '#f093fb']
    },
    {
        'type': 'pie',
        'title': 'Department Distribution',
        'labels': ['Engineering', 'Marketing', 'Sales', 'HR'],
        'data': [15, 12, 18, 5]
    }
]

test_insights = [
    "The dataset contains 50 records across 5 columns",
    "Average salary is $70,250.50",
    "Engineering department has the highest average salary"
]

print("🧪 Testing dashboard save functionality...\n")

# Create a test dashboard
print("1️⃣ Creating test dashboard...")
dashboard_id = create_dashboard(
    name="Test Dashboard - Auto Mode",
    dataset_id=1,  # Assuming dataset ID 1 exists
    user_id=1,     # Assuming user ID 1 exists
    project_id=1,  # Assuming project ID 1 exists
    stats_data=test_stats,
    charts_data=test_charts,
    insights_data=test_insights,
    mode='auto'
)

if dashboard_id:
    print(f"✅ Dashboard created successfully! ID: {dashboard_id}\n")
    
    # Retrieve dashboards for user
    print("2️⃣ Retrieving dashboards for user 1...")
    dashboards = get_user_dashboards(user_id=1)
    
    if dashboards:
        print(f"✅ Found {len(dashboards)} dashboard(s):\n")
        for dash in dashboards:
            print(f"   📊 {dash['name']}")
            print(f"      ID: {dash['id']}")
            print(f"      Charts: {dash['total_charts']}")
            print(f"      KPIs: {dash['total_kpis']}")
            print(f"      Created: {dash['created_at']}")
            print()
    else:
        print("❌ No dashboards found!")
else:
    print("❌ Failed to create dashboard!")
    print("\nPossible issues:")
    print("- Dataset ID 1 doesn't exist")
    print("- User ID 1 doesn't exist")
    print("- Project ID 1 doesn't exist")
    print("\nCheck your database for existing IDs")
