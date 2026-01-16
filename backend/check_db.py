"""Check database tables and structure"""
import sqlite3

conn = sqlite3.connect('interview_system.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("=" * 60)
print("DATABASE TABLES")
print("=" * 60)
print(f"Found {len(tables)} tables: {tables}")
print()

# Get schema for each table
for table in tables:
    print(f"\n--- {table.upper()} ---")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]}: {col[2]} {'(PK)' if col[5] else ''}")
    
    # Count rows
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  Rows: {count}")

conn.close()
print("\n" + "=" * 60)
print("Database check complete!")
