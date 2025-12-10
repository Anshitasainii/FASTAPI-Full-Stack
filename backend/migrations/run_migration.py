"""
Python script to run the database migration
This script will add the new columns to the users table
"""
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db import engine

# SQL statements to add new columns (one at a time to handle errors gracefully)
migration_statements = [
    ("first_name", "ALTER TABLE users ADD COLUMN first_name VARCHAR(255) NULL AFTER name"),
    ("last_name", "ALTER TABLE users ADD COLUMN last_name VARCHAR(255) NULL AFTER first_name"),
    ("dob", "ALTER TABLE users ADD COLUMN dob DATE NULL AFTER last_name"),
    ("mobile", "ALTER TABLE users ADD COLUMN mobile VARCHAR(20) NULL AFTER dob"),
    ("professional_summary", "ALTER TABLE users ADD COLUMN professional_summary TEXT NULL AFTER mobile"),
    ("gender", "ALTER TABLE users ADD COLUMN gender VARCHAR(20) NULL AFTER professional_summary"),
    ("job_status", "ALTER TABLE users ADD COLUMN job_status VARCHAR(50) NULL AFTER gender"),
    ("profile_image", "ALTER TABLE users MODIFY COLUMN profile_image VARCHAR(500) NULL")
]

def run_migration():
    try:
        # Get raw connection
        connection = engine.raw_connection()
        cursor = connection.cursor()
        
        print("Running database migration...")
        print("=" * 50)
        
        for column_name, statement in migration_statements:
            try:
                # Check if column already exists
                if "MODIFY" not in statement:
                    cursor.execute(f"SHOW COLUMNS FROM users LIKE '{column_name}'")
                    if cursor.fetchone():
                        print(f"\n[SKIP] Column '{column_name}' already exists, skipping")
                        continue
                
                print(f"\nExecuting: {statement[:60]}...")
                cursor.execute(statement)
                connection.commit()
                print("[OK] Success")
            except Exception as e:
                error_msg = str(e)
                # Check if column already exists (MySQL error 1060)
                if "Duplicate column name" in error_msg or "1060" in error_msg:
                    print(f"[SKIP] Column '{column_name}' already exists, skipping")
                # Check if column doesn't exist for MODIFY (MySQL error 1054)
                elif "1054" in error_msg and "MODIFY" in statement:
                    print(f"[SKIP] Column '{column_name}' doesn't exist yet, skipping MODIFY")
                else:
                    print(f"[ERROR] Error: {error_msg}")
                    # Continue with other statements even if one fails
        
        cursor.close()
        connection.close()
        print("\n" + "=" * 50)
        print("[SUCCESS] Migration completed!")
        print("\nNote: Some statements may have been skipped if columns already exist.")
        
    except Exception as e:
        print(f"\n[FAILED] Migration failed: {e}")
        print("\nYou can also run the SQL script manually:")
        print("mysql -u root -p test < backend/migrations/add_user_fields_mobile.sql")

if __name__ == "__main__":
    run_migration()

