"""
Simple database reset script - just deletes and lets the app recreate it.
"""

import os
import shutil

db_file = "interview_system.db"

print("=" * 70)
print("DATABASE RESET SCRIPT")
print("=" * 70)
print()

if os.path.exists(db_file):
    print(f"[!] Found existing database: {db_file}")
    print(f"    File size: {os.path.getsize(db_file) / 1024:.2f} KB")
    print()

    # Backup
    backup_file = f"{db_file}.backup"
    if os.path.exists(backup_file):
        os.remove(backup_file)

    shutil.copy2(db_file, backup_file)
    print(f"[OK] Backed up to: {backup_file}")

    # Delete
    os.remove(db_file)
    print(f"[DELETE] Deleted database file")
    print()
    print("=" * 70)
    print("[OK] DATABASE DELETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Start the backend server: uvicorn app.main:app --reload")
    print("  2. The database will be auto-created with the new schema")
    print("  3. Create a new user account")
    print()
else:
    print("[INFO] No database file found")
    print()
