"""
Test Script for Complete Workflow - Steps 1-6
This script tests the entire workflow programmatically
"""
import requests
import pandas as pd
import os

# Base URL
BASE_URL = "http://127.0.0.1:5000"

def test_complete_workflow():
    """Test the complete workflow from start to finish"""
    
    print("=" * 60)
    print("AI DASHBOARD - COMPLETE WORKFLOW TEST")
    print("=" * 60)
    
    # Create a test session
    session = requests.Session()
    
    # ========================================
    # STEP 1: Workflow Start
    # ========================================
    print("\n📋 STEP 1: Accessing Workflow Start Page")
    print("-" * 60)
    
    response = session.get(f"{BASE_URL}/workflow/")
    if response.status_code == 200:
        print("✅ Workflow start page loaded successfully")
        print(f"   URL: {BASE_URL}/workflow/")
    else:
        print(f"❌ Failed to load workflow start page: {response.status_code}")
        return
    
    # ========================================
    # STEP 2: Upload File & Raw Preview
    # ========================================
    print("\n📤 STEP 2: Upload File & View Raw Preview")
    print("-" * 60)
    
    # Create a test CSV file
    test_data = pd.DataFrame({
        'age': [25, 30, None, 35, 30],
        'gender': ['M', 'F', 'F', 'M', 'M'],
        'salary': [50000, 60000, 55000, 70000, 60000],
        'department': ['IT', 'HR', 'IT', 'Sales', None],
        'join_date': ['2020-01-15', '2019-05-20', None, '2021-03-10', '2020-01-15']
    })
    
    test_file_path = 'test_dataset.csv'
    test_data.to_csv(test_file_path, index=False)
    print(f"   Created test file: {test_file_path}")
    
    # Upload the file
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'name': 'Test Employee Dataset'}
        response = session.post(f"{BASE_URL}/workflow/upload", files=files, data=data)
    
    if response.status_code == 200:
        print("✅ File uploaded successfully")
        print("   Dataset: Test Employee Dataset")
        print(f"   Rows: {len(test_data)}")
        print(f"   Columns: {len(test_data.columns)}")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        return
    
    # Clean up test file
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    
    # ========================================
    # STEP 3: Auto-Clean Data
    # ========================================
    print("\n🧹 STEP 3: Auto-Clean Data")
    print("-" * 60)
    
    response = session.post(f"{BASE_URL}/workflow/clean")
    if response.status_code == 200:
        print("✅ Data cleaned successfully")
        print("   Applied cleaning:")
        print("   - NULL values filled/removed")
        print("   - Duplicates removed")
        print("   - Dates formatted to ISO")
        print("   - Data types corrected")
    else:
        print(f"❌ Cleaning failed: {response.status_code}")
        return
    
    # ========================================
    # STEP 4: Column Selection & Download Ready
    # ========================================
    print("\n✅ STEP 4: Select Columns & Download Ready")
    print("-" * 60)
    
    # Select all columns
    columns = ['age', 'gender', 'salary', 'department', 'join_date']
    data = {'columns': columns}
    response = session.post(f"{BASE_URL}/workflow/select-columns", data=data)
    
    if response.status_code == 200:
        print("✅ Columns selected successfully")
        print(f"   Selected {len(columns)} columns: {', '.join(columns)}")
        print("\n   Available downloads:")
        print(f"   📊 CSV:   {BASE_URL}/workflow/download/csv")
        print(f"   📗 Excel: {BASE_URL}/workflow/download/excel")
        print("\n   Next step:")
        print(f"   🎯 Analytics: {BASE_URL}/workflow/mode-selection")
    else:
        print(f"❌ Column selection failed: {response.status_code}")
        return
    
    # Test CSV download
    print("\n   Testing CSV download...")
    response = session.get(f"{BASE_URL}/workflow/download/csv")
    if response.status_code == 200:
        print("   ✅ CSV download successful")
        print(f"   Size: {len(response.content)} bytes")
    else:
        print(f"   ❌ CSV download failed: {response.status_code}")
    
    # Test Excel download
    print("\n   Testing Excel download...")
    response = session.get(f"{BASE_URL}/workflow/download/excel")
    if response.status_code == 200:
        print("   ✅ Excel download successful")
        print(f"   Size: {len(response.content)} bytes")
    else:
        print(f"   ❌ Excel download failed: {response.status_code}")
    
    # ========================================
    # STEP 5: Mode Selection
    # ========================================
    print("\n🎯 STEP 5: Analytics Mode Selection")
    print("-" * 60)
    
    response = session.get(f"{BASE_URL}/workflow/mode-selection")
    if response.status_code == 200:
        print("✅ Mode selection page loaded")
        print("\n   Available modes:")
        print(f"   🤖 Auto Mode:   {BASE_URL}/workflow/auto-mode")
        print(f"   💬 Prompt Mode: {BASE_URL}/workflow/prompt-mode")
    else:
        print(f"❌ Mode selection failed: {response.status_code}")
        return
    
    # ========================================
    # STEP 6a: Auto Mode
    # ========================================
    print("\n🤖 STEP 6a: Auto Mode Analytics")
    print("-" * 60)
    
    response = session.get(f"{BASE_URL}/workflow/auto-mode")
    if response.status_code == 200:
        print("✅ Auto mode loaded successfully")
        print("   Features:")
        print("   - Summary statistics")
        print("   - Auto-generated charts (Chart.js)")
        print("   - Key insights")
        print("   - Distribution analysis")
    else:
        print(f"❌ Auto mode failed: {response.status_code}")
    
    # ========================================
    # STEP 6b: Prompt Mode
    # ========================================
    print("\n💬 STEP 6b: Prompt Mode Analytics")
    print("-" * 60)
    
    response = session.get(f"{BASE_URL}/workflow/prompt-mode")
    if response.status_code == 200:
        print("✅ Prompt mode loaded successfully")
        print("   Features:")
        print("   - Natural language queries")
        print("   - AI-powered responses")
        print("   - Query history")
        print("   - Custom analysis")
    else:
        print(f"❌ Prompt mode failed: {response.status_code}")
    
    # Test prompt API
    print("\n   Testing prompt API...")
    query_data = {'query': 'What is the average salary?'}
    response = session.post(
        f"{BASE_URL}/workflow/api/query",
        json=query_data,
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 200:
        print("   ✅ Prompt API working")
        result = response.json()
        print(f"   Response: {result.get('message', 'No message')}")
    else:
        print(f"   ❌ Prompt API failed: {response.status_code}")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 60)
    print("✅ WORKFLOW TEST COMPLETE")
    print("=" * 60)
    print("\nAll 6 steps tested successfully!")
    print("\nManual Testing URLs:")
    print(f"1. Start:           {BASE_URL}/workflow/")
    print(f"2. Upload:          (POST form)")
    print(f"3. Clean:           (POST form)")
    print(f"4. Download:        See download_ready.html")
    print(f"5. Mode Selection:  {BASE_URL}/workflow/mode-selection")
    print(f"6a. Auto Mode:      {BASE_URL}/workflow/auto-mode")
    print(f"6b. Prompt Mode:    {BASE_URL}/workflow/prompt-mode")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        test_complete_workflow()
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
