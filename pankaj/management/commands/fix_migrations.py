# fix_migrations.py
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bisht.settings')
django.setup()

from django.db import connection
import subprocess

def fix_migrations():
    print("Step 1: Checking current migration state...")
    
    # Check what migration files exist
    migration_dir = "pankaj/migrations"
    migration_files = os.listdir(migration_dir)
    print(f"Migrations found: {migration_files}")
    
    # Delete problematic migrations (keep 0001-0012)
    files_to_delete = []
    for file in migration_files:
        if file.startswith("0013_") or file.startswith("0014_") or file.startswith("0015_"):
            files_to_delete.append(file)
    
    print(f"\nStep 2: Deleting problematic migrations: {files_to_delete}")
    for file in files_to_delete:
        filepath = os.path.join(migration_dir, file)
        os.remove(filepath)
        print(f"Deleted: {file}")
    
    # Delete the __pycache__ folder
    pycache_path = os.path.join(migration_dir, "__pycache__")
    if os.path.exists(pycache_path):
        import shutil
        shutil.rmtree(pycache_path)
        print("Deleted __pycache__ folder")
    
    print("\nStep 3: Resetting database migration state...")
    # Reset the migration state in database
    with connection.cursor() as cursor:
        try:
            # Delete migration records for pankaj app
            cursor.execute("DELETE FROM django_migrations WHERE app = 'pankaj'")
            print("Cleared django_migrations table for pankaj")
            
            # Re-apply up to migration 0012
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                SELECT 'pankaj', name, CURRENT_TIMESTAMP 
                FROM (
                    VALUES ('0001_initial'),
                           ('0002_initial'),
                           -- Add all your migration names up to 0012
                           ('0012_alter_blogpost_options_blogpost_author_and_more')
                ) AS migrations(name)
            """)
        except Exception as e:
            print(f"Error resetting migrations: {e}")
    
    print("\nStep 4: Creating new migration for slug fix...")
    # Run makemigrations
    subprocess.run([sys.executable, "manage.py", "makemigrations", "pankaj", "--name", "fix_slugs_once"])
    
    print("\nStep 5: Applying migrations...")
    subprocess.run([sys.executable, "manage.py", "migrate", "pankaj"])

if __name__ == "__main__":
    fix_migrations()