# backend/database.py
import os
import glob
import sqlite3
import pandas as pd
from config import DB_PATH, DATASETS_DIR

def get_db_connection():
    """Returns a SQLite connection object with row factory set to sqlite3.Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Reads all CSV files from datasets directory and replacement-writes them to SQLite tables."""
    print("Initializing SQLite Database from CSV files...")
    conn = sqlite3.connect(DB_PATH)
    
    csv_files = glob.glob(os.path.join(DATASETS_DIR, "*.csv"))
    if not csv_files:
        print(f"Warning: No datasets found in '{DATASETS_DIR}'. Please check simulation data.")
        return

    for file_path in csv_files:
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            df = pd.read_csv(file_path)
            # Write to SQL
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"  - Loaded table '{table_name}' ({len(df)} rows)")
        except Exception as e:
            print(f"  - Error loading table '{table_name}': {e}")
            
    conn.close()
    print("Database initialization complete.")
