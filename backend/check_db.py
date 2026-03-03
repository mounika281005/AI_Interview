import sqlite3
conn = sqlite3.connect('interview_system.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(users)')
cols = cursor.fetchall()
print("User table columns:")
for col in cols:
    print(f"  {col[1]}: {col[2]}")
column_names = [col[1] for col in cols]
print("\nResume columns:")
print(f"  resume_data: {'EXISTS' if 'resume_data' in column_names else 'MISSING'}")
print(f"  resume_url: {'EXISTS' if 'resume_url' in column_names else 'MISSING'}")
cursor.execute('SELECT COUNT(*) FROM users')
print(f"\nTotal users: {cursor.fetchone()[0]}")
conn.close()
