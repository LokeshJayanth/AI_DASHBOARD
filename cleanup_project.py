"""
Project Cleanup Script
Identifies and optionally deletes unwanted files
"""
import os
import shutil

# Files that can be safely deleted
SAFE_TO_DELETE = {
    'test_scripts': [
        'check_table_structure.py',
        'check_users.py',
        'create_loki_user.py',
        'create_user_fixed.py',
        'fix_users_table.py',
        'rebuild_users_table.py',
        'setup_db.py',
        'setup_user.py',
        'run_migration.py',
        'run_projects_migration.py',
        'test_auth_system.py',
        'test_dashboard_save.py',
        'test_workflow.py',
        'demo_login_flow.py',
        'show_final_status.py',
    ],
    'test_data': [
        'sample_employee_data.csv',
        'test_dataset.csv',
        'test_sample_data.csv',
    ],
    'old_docs': [
        'DASHBOARD_SAVE_FIXED.md',
        'DRAG_DROP_IMPLEMENTATION.md',
        'FINAL_IMPLEMENTATION.md',
        'IDE_LINT_ERRORS_EXPLAINED.md',
        'IMPLEMENTATION_COMPLETE.md',
        'IMPLEMENTATION_SUMMARY.md',
        'SAVE_TO_STORAGE_IMPLEMENTATION.md',
        'VERIFICATION_CHECKLIST.md',
        'CLEAR_BROWSER_AUTOFILL.md',
    ],
    'cache_folders': [
        '__pycache__',
        'routes/__pycache__',
        'services/__pycache__',
        'utils/__pycache__',
    ]
}

# Files to keep (important)
KEEP_FILES = [
    'app.py',
    'config.py',
    'requirements.txt',
    'README.md',
    'LOGIN_SYSTEM_GUIDE.md',
    'AUTH_SYSTEM_COMPLETE.md',
    'QUICK_LOGIN_REFERENCE.md',
    'AUTOFILL_FIX_COMPLETE.md',
    'fix_auth_system.py',
    'test_login_system.py',
    'test_db.py',
    'CLEANUP_GUIDE.md',
    'cleanup_project.py',
]

def analyze_files():
    """Analyze files and show what can be deleted"""
    print("\n" + "="*70)
    print("🔍 PROJECT CLEANUP ANALYSIS")
    print("="*70 + "\n")
    
    total_size = 0
    file_count = 0
    
    for category, files in SAFE_TO_DELETE.items():
        print(f"\n📁 {category.upper().replace('_', ' ')}")
        print("-" * 70)
        
        category_size = 0
        category_count = 0
        
        for file in files:
            if os.path.exists(file):
                if os.path.isfile(file):
                    size = os.path.getsize(file)
                    size_kb = size / 1024
                    print(f"  ❌ {file:<40} ({size_kb:.1f} KB)")
                    category_size += size
                    category_count += 1
                elif os.path.isdir(file):
                    try:
                        size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(file)
                            for filename in filenames
                        )
                        size_kb = size / 1024
                        print(f"  ❌ {file:<40} ({size_kb:.1f} KB)")
                        category_size += size
                        category_count += 1
                    except:
                        print(f"  ❌ {file:<40} (folder)")
            else:
                print(f"  ✓  {file:<40} (already deleted)")
        
        if category_count > 0:
            print(f"\n  Subtotal: {category_count} items, {category_size/1024:.1f} KB")
            total_size += category_size
            file_count += category_count
    
    print("\n" + "="*70)
    print(f"📊 TOTAL: {file_count} items can be deleted, {total_size/1024:.1f} KB")
    print("="*70 + "\n")
    
    return file_count, total_size

def show_keep_files():
    """Show files that will be kept"""
    print("\n" + "="*70)
    print("✅ ESSENTIAL FILES (WILL BE KEPT)")
    print("="*70 + "\n")
    
    for file in KEEP_FILES:
        if os.path.exists(file):
            size = os.path.getsize(file)
            size_kb = size / 1024
            print(f"  ✅ {file:<40} ({size_kb:.1f} KB)")
    
    print("\n" + "="*70)
    print("📁 ESSENTIAL FOLDERS (WILL BE KEPT)")
    print("="*70 + "\n")
    
    folders = [
        'routes', 'services', 'templates', 'static', 'utils',
        'database', 'migrations', 'uploads', 'datasets', 'downloads'
    ]
    
    for folder in folders:
        if os.path.exists(folder):
            print(f"  ✅ {folder}/")

def delete_files(dry_run=True):
    """Delete unwanted files"""
    if dry_run:
        print("\n" + "="*70)
        print("🔍 DRY RUN MODE (No files will be deleted)")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("🗑️  DELETING FILES...")
        print("="*70 + "\n")
    
    deleted_count = 0
    deleted_size = 0
    
    for category, files in SAFE_TO_DELETE.items():
        for file in files:
            if os.path.exists(file):
                try:
                    if os.path.isfile(file):
                        size = os.path.getsize(file)
                        if not dry_run:
                            os.remove(file)
                            print(f"  ✅ Deleted: {file}")
                        else:
                            print(f"  🔍 Would delete: {file}")
                        deleted_count += 1
                        deleted_size += size
                    elif os.path.isdir(file):
                        size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(file)
                            for filename in filenames
                        )
                        if not dry_run:
                            shutil.rmtree(file)
                            print(f"  ✅ Deleted folder: {file}")
                        else:
                            print(f"  🔍 Would delete folder: {file}")
                        deleted_count += 1
                        deleted_size += size
                except Exception as e:
                    print(f"  ❌ Error with {file}: {str(e)}")
    
    print("\n" + "="*70)
    if dry_run:
        print(f"🔍 Would delete: {deleted_count} items, {deleted_size/1024:.1f} KB")
    else:
        print(f"✅ Deleted: {deleted_count} items, {deleted_size/1024:.1f} KB")
    print("="*70 + "\n")

def main():
    """Main cleanup function"""
    print("\n" + "="*70)
    print("🧹 PROJECT CLEANUP TOOL")
    print("="*70)
    
    # Show analysis
    file_count, total_size = analyze_files()
    
    if file_count == 0:
        print("\n✅ Project is already clean! No files to delete.")
        return
    
    # Show what will be kept
    show_keep_files()
    
    # Ask user what to do
    print("\n" + "="*70)
    print("⚠️  CLEANUP OPTIONS")
    print("="*70 + "\n")
    print("1. Dry run (show what would be deleted)")
    print("2. Delete all unwanted files")
    print("3. Cancel")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        delete_files(dry_run=True)
        print("\n💡 To actually delete files, run this script again and choose option 2")
    elif choice == '2':
        confirm = input("\n⚠️  Are you sure you want to delete these files? (yes/no): ").strip().lower()
        if confirm == 'yes':
            delete_files(dry_run=False)
            print("\n✅ Cleanup complete!")
            print("\n💡 Your project is now cleaner and easier to navigate.")
        else:
            print("\n❌ Cleanup cancelled.")
    else:
        print("\n❌ Cleanup cancelled.")

if __name__ == '__main__':
    main()
