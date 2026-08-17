import os
import sys
import argparse
import subprocess
from datetime import datetime

def backup_postgresql(db_url: str, output_dir: str = "./backups"):
    """
    Perform PostgreSQL Database Backup.
    Generates a timestamped .sql / .dump database snapshot.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(output_dir, f"revenueos_backup_{timestamp}.sql")

    print(f"Starting database backup to {backup_file}...")
    
    if db_url.startswith("sqlite"):
        print("[INFO] SQLite database detected. Creating direct file copy backup...")
        import shutil
        sqlite_file = db_url.replace("sqlite:///", "").replace("./", "")
        if os.path.exists(sqlite_file):
            shutil.copy(sqlite_file, backup_file)
            print(f"[OK] Backup created cleanly at: {backup_file}")
        else:
            print(f"[ERROR] SQLite file {sqlite_file} not found.")
        return

    # PostgreSQL pg_dump execution
    try:
        cmd = ["pg_dump", "--dbname=" + db_url, "-f", backup_file]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[OK] PostgreSQL backup completed cleanly: {backup_file}")
        else:
            print(f"[ERROR] Backup failed: {res.stderr}")
    except Exception as e:
        print(f"[ERROR] Backup command failed: {e}")

def restore_postgresql(db_url: str, backup_file: str):
    """
    Perform PostgreSQL Database Restore.
    """
    if not os.path.exists(backup_file):
        print(f"[ERROR] Backup file {backup_file} does not exist.")
        return

    print(f"Starting database restore from {backup_file}...")

    if db_url.startswith("sqlite"):
        print("[INFO] SQLite database restore...")
        import shutil
        sqlite_file = db_url.replace("sqlite:///", "").replace("./", "")
        shutil.copy(backup_file, sqlite_file)
        print(f"[OK] SQLite database restored cleanly to {sqlite_file}")
        return

    try:
        cmd = ["psql", "--dbname=" + db_url, "-f", backup_file]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[OK] PostgreSQL restore completed cleanly from {backup_file}")
        else:
            print(f"[ERROR] Restore failed: {res.stderr}")
    except Exception as e:
        print(f"[ERROR] Restore command failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RevenueOS AI Backup & Restore Script")
    parser.add_argument("action", choices=["backup", "restore"], help="Action to perform")
    parser.add_argument("--db-url", default="sqlite:///./revenueos.db", help="Database URL")
    parser.add_argument("--file", help="Backup file for restore action")

    args = parser.parse_args()

    if args.action == "backup":
        backup_postgresql(args.db_url)
    elif args.action == "restore":
        if not args.file:
            print("Error: --file argument is required for restore action.")
        else:
            restore_postgresql(args.db_url, args.file)
