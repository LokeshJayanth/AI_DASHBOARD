# End-to-End Project Upload Flow - Testing Guide

## Overview
This document provides step-by-step instructions to test the complete project creation to data analytics workflow.

## Complete User Journey

### Step 1: Dashboard → Create Project
**Location:** `http://localhost:5000/dashboard`

**Actions:**
1. Navigate to the user dashboard
2. Click the "+ New Project" button
3. Modal appears with form fields
4. Enter:
   - **Project Name:** "Test Data Upload"
   - **Description:** "Testing the complete upload workflow"
5. Click "Create Project" button

**Expected Result:**
- ✅ Flash message: "Project created successfully! Now upload your data."
- ✅ Automatic redirect to: `/upload?project_id=X`
- ✅ Upload page shows project context indicator

---

### Step 2: Upload Page → Select File
**Location:** `http://localhost:5000/upload?project_id=X`

**Visual Indicators:**
- "← Back to Dashboard" link at top
- Blue info box showing "📁 Uploading to Project ID: X"
- Upload form with drag & drop zone

**Actions:**
1. Enter dataset name (e.g., "Employee Data")
2. Either:
   - Drag and drop a CSV/Excel file, OR
   - Click "Browse Files" and select a file
3. File preview card appears showing filename and size
4. Click "✨ Upload & Analyze" button

**Expected Result:**
- ✅ File uploaded successfully
- ✅ Redirect to: `/upload/file` (Raw Preview page)
- ✅ Session stores `project_id` in `upload_data`

---

### Step 3: Raw Preview → Review Data
**Location:** Automatically redirected after upload

**Visual Elements:**
- Page title: "📊 Raw Data Preview"
- Dataset name displayed
- 4 stat cards showing:
  - Total Rows
  - Columns
  - NULL Values
  - Duplicates
- Data quality warning (if issues found)
- Preview table (first 10 rows)

**Actions:**
1. Review the statistics
2. Check the data preview table
3. Click "✨ Clean Data →" button

**Expected Result:**
- ✅ Data cleaning process initiated
- ✅ Redirect to: `/upload/clean` (Cleaned Preview page)

---

### Step 4: Cleaned Preview → Select Columns
**Location:** Automatically redirected after cleaning

**Visual Elements:**
- Page title: "✨ Cleaned Data Preview"
- Before/After statistics comparison
- Cleaned data preview table
- Column selection checkboxes

**Actions:**
1. Review the before/after stats
2. Check the cleaned data preview
3. Select columns to include (or select all)
4. Click "Continue to Column Selection →" or similar button

**Expected Result:**
- ✅ Selected columns stored in session
- ✅ Redirect to: `/upload/select-columns` (Analytics page)

---

### Step 5: Analytics → View Insights
**Location:** `/upload/analytics`

**Visual Elements:**
- Auto-generated charts:
  - Bar charts
  - Pie charts
  - Line charts
  - Correlation matrices
- Summary statistics cards
- AI-generated insights
- Download options:
  - CSV
  - Excel
  - Power BI (.pbix)

**Actions:**
1. Review the auto-generated analytics
2. Explore different chart types
3. Read AI insights
4. (Optional) Download files
5. (Optional) Click "Save to Database" to persist data

**Expected Result:**
- ✅ Analytics displayed correctly
- ✅ Downloads work properly
- ✅ If saved: Dataset linked to project_id in database

---

## Database Verification

After completing the workflow, verify in MySQL:

```sql
-- Check if project was created
SELECT * FROM projects WHERE name = 'Test Data Upload';

-- Check if dataset was created and linked to project
SELECT d.*, p.name as project_name 
FROM datasets d 
LEFT JOIN projects p ON d.project_id = p.id 
WHERE d.name = 'Employee Data';

-- Verify project_id is set
SELECT id, name, project_id, user_id, created_at 
FROM datasets 
ORDER BY created_at DESC 
LIMIT 5;
```

**Expected Results:**
- ✅ Project exists in `projects` table
- ✅ Dataset exists in `datasets` table
- ✅ Dataset's `project_id` matches the created project's `id`
- ✅ Both have the same `user_id`

---

## Session Flow Verification

The session should maintain these values throughout:

```python
# After project creation
session['current_project_id'] = X

# After file upload
session['upload_data'] = {
    'dataset_name': 'Employee Data',
    'filepath': '/path/to/file.csv',
    'columns': ['col1', 'col2', ...],
    'rows': 100,
    'project_id': X  # ← CRITICAL: Must match current_project_id
}

# After cleaning
session['upload_data']['cleaned_filepath'] = '/path/to/cleaned.pkl'
session['upload_data']['cleaned_columns'] = [...]

# After column selection
session['upload_data']['final_filepath'] = '/path/to/final.pkl'
session['upload_data']['selected_columns'] = [...]
```

---

## Common Issues & Troubleshooting

### Issue 1: project_id not in URL
**Symptom:** Upload page doesn't show project context
**Solution:** Check that `create_new_project` redirects with `project_id` parameter

### Issue 2: Dataset not linked to project
**Symptom:** `project_id` is NULL in database
**Solution:** Verify `upload_data` contains `project_id` before calling `create_dataset`

### Issue 3: Session lost between steps
**Symptom:** "No upload session found" error
**Solution:** Ensure `session.modified = True` after updating session data

### Issue 4: Redirect loop
**Symptom:** Page keeps redirecting
**Solution:** Check that each route properly handles the POST request and redirects to next step

---

## Test Data

Use this sample CSV for testing:

```csv
name,age,department,salary,join_date
John Doe,30,Engineering,75000,2020-01-15
Jane Smith,28,Marketing,65000,2020-03-20
Bob Johnson,35,Sales,70000,2019-11-10
Alice Williams,32,Engineering,80000,2021-05-12
Charlie Brown,29,HR,60000,2020-08-25
```

Save as `test_employees.csv` and use for upload testing.

---

## Success Criteria

✅ **Project Creation:**
- Project created in database
- Redirect to upload page with project_id
- Project context visible on upload page

✅ **File Upload:**
- File uploaded successfully
- Raw preview displays correctly
- Statistics calculated accurately

✅ **Data Cleaning:**
- NULL values handled
- Duplicates removed
- Cleaned preview shows improvements

✅ **Column Selection:**
- All columns available for selection
- Selected columns stored in session
- Redirect to analytics works

✅ **Analytics:**
- Charts generated automatically
- Statistics calculated correctly
- Download options functional

✅ **Database Integration:**
- Dataset saved with correct project_id
- Foreign key relationship maintained
- User ownership preserved

---

## Performance Benchmarks

Expected timing for each step:

| Step | Expected Time |
|------|--------------|
| Project Creation | < 500ms |
| File Upload (10MB) | < 2s |
| Raw Preview | < 1s |
| Data Cleaning | < 3s |
| Column Selection | < 1s |
| Analytics Generation | < 5s |
| **Total End-to-End** | **< 15s** |

---

## Next Steps After Testing

1. **Test with different file types:**
   - CSV files
   - Excel (.xlsx, .xls)
   - JSON files

2. **Test with various data sizes:**
   - Small (< 1MB, < 1000 rows)
   - Medium (1-10MB, 1000-10000 rows)
   - Large (10-50MB, 10000+ rows)

3. **Test edge cases:**
   - Empty files
   - Files with all NULL values
   - Files with special characters
   - Files with date columns
   - Files with mixed data types

4. **Test error handling:**
   - Invalid file formats
   - Corrupted files
   - Files exceeding size limit
   - Network interruptions

5. **Test concurrent users:**
   - Multiple users creating projects
   - Multiple uploads simultaneously
   - Session isolation

---

## Conclusion

This comprehensive workflow ensures:
- Seamless user experience from project creation to analytics
- Proper data organization and project association
- Robust error handling and validation
- Scalable architecture for future enhancements

**Status:** ✅ READY FOR TESTING
