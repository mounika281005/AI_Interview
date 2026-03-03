"""
Recreate the database with updated schema.
This will drop all existing tables and recreate them with the new schema changes.
"""

import asyncio
import os
from app.database import drop_db, init_db, engine


async def recreate_database():
    """Drop and recreate all database tables."""
    print("=" * 70)
    print("DATABASE RECREATION SCRIPT")
    print("=" * 70)
    print()

    # Get database file path
    db_path = "interview_system.db"

    if os.path.exists(db_path):
        print(f"⚠️  WARNING: This will delete all data in '{db_path}'")
        print()
        response = input("Are you sure you want to continue? (yes/no): ").strip().lower()

        if response != 'yes':
            print("❌ Operation cancelled.")
            return

    print()
    print("🗑️  Dropping all tables...")
    try:
        await drop_db()
        print("✅ All tables dropped successfully")
    except Exception as e:
        print(f"⚠️  Error dropping tables: {e}")
        print("   (This is normal if tables don't exist yet)")

    print()
    print("🔨 Creating tables with new schema...")
    try:
        await init_db()
        print("✅ All tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        await engine.dispose()
        return

    print()
    print("=" * 70)
    print("✅ DATABASE RECREATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("The database now has the updated schema with:")
    print("  ✓ Timezone-aware datetime columns for started_at and completed_at")
    print("  ✓ Resume data columns (resume_url, resume_data)")
    print("  ✓ All other schema improvements")
    print()
    print("You can now start the server and create a new user account.")
    print()

    # Dispose engine
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(recreate_database())
