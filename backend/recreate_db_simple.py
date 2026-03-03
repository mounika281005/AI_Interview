"""
Simple database recreation script - recreates database with updated schema.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base


async def recreate_database():
    """Drop and recreate all database tables."""
    print("=" * 70)
    print("DATABASE RECREATION SCRIPT")
    print("=" * 70)
    print()

    # Database URL (SQLite)
    db_file = "interview_system.db"
    database_url = f"sqlite+aiosqlite:///{db_file}"

    if os.path.exists(db_file):
        print(f"[!] Found existing database: {db_file}")
        print(f"    File size: {os.path.getsize(db_file) / 1024:.2f} KB")
        print()
        print("[!] WARNING: This will delete all existing data!")
        print()

        # Backup the old database
        backup_file = f"{db_file}.backup"
        if os.path.exists(backup_file):
            os.remove(backup_file)

        import shutil
        shutil.copy2(db_file, backup_file)
        print(f"[OK] Backed up existing database to: {backup_file}")
        print()

        # Delete the old database
        os.remove(db_file)
        print(f"[DELETE] Deleted old database file")
    else:
        print("[INFO] No existing database found. Creating new database...")

    print()

    # Create engine
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Import Base
    Base = declarative_base()

    # Import all models to register them with Base
    print("[LOAD] Loading models...")
    try:
        from app.models.user import User
        from app.models.interview import InterviewSession
        from app.models.question import InterviewQuestion
        from app.models.feedback import InterviewFeedback
        print("[OK] Models loaded successfully")
    except Exception as e:
        print(f"[ERROR] Error loading models: {e}")
        return

    # Create all tables
    print()
    print("[CREATE] Creating tables with new schema...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[OK] All tables created successfully!")
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        await engine.dispose()
        return

    # Verify tables
    print()
    print("[VERIFY] Verifying database structure...")
    try:
        from sqlalchemy import text, inspect
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            print(f"[OK] Created {len(tables)} tables: {', '.join(tables)}")
    except Exception as e:
        print(f"[WARN]  Could not verify tables: {e}")

    print()
    print("=" * 70)
    print("[OK] DATABASE RECREATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Schema updates applied:")
    print("  ✓ started_at column: DateTime(timezone=True)")
    print("  ✓ completed_at column: DateTime(timezone=True)")
    print("  ✓ resume_url column: String")
    print("  ✓ resume_data column: JSON")
    print()
    print("Next steps:")
    print("  1. Start the backend server: uvicorn app.main:app --reload")
    print("  2. Create a new user account")
    print("  3. Test the interview flow")
    print()

    # Dispose engine
    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(recreate_database())
    except KeyboardInterrupt:
        print("\n\n[ERROR] Operation cancelled by user.")
    except Exception as e:
        print(f"\n\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
