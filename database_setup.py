import sqlite3
import pandas as pd
import os
from analytics import hash_password, ensure_interventions_table

def setup_database():
    db_name = 'edutrak.db'
    behavior_csv = 'Online_Learning_Behavior_Dataset_Worldwide.csv'
    engagement_csv = 'online_learning_engagement_dataset.csv'

    print(f"Connecting to {db_name}...")
    conn = sqlite3.connect(db_name)

    try:
        cursor = conn.cursor()
        # Datasets Tracking Table
        print("Creating 'datasets' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL, -- 'behavior' or 'engagement'
                table_name TEXT NOT NULL UNIQUE,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add initial datasets if empty
        cursor.execute("SELECT COUNT(*) FROM datasets")
        if cursor.fetchone()[0] == 0:
            print("Registering initial datasets...")
            initial_datasets = [
                ('Original Behavior Data', 'behavior', 'behavior'),
                ('Original Engagement Data', 'engagement', 'engagement')
            ]
            cursor.executemany("INSERT INTO datasets (name, type, table_name) VALUES (?, ?, ?)", initial_datasets)
            conn.commit()

        # Load Behavior Dataset
        if os.path.exists(behavior_csv):
            print(f"Loading {behavior_csv} into 'behavior' table...")
            df_behavior = pd.read_csv(behavior_csv)
            df_behavior.to_sql('behavior', conn, if_exists='replace', index=False)
            print(f"Successfully loaded {len(df_behavior)} records into 'behavior'.")
        else:
            print(f"Error: {behavior_csv} not found.")

        # Load Engagement Dataset
        if os.path.exists(engagement_csv):
            print(f"Loading {engagement_csv} into 'engagement' table...")
            df_engagement = pd.read_csv(engagement_csv)
            df_engagement.to_sql('engagement', conn, if_exists='replace', index=False)
            print(f"Successfully loaded {len(df_engagement)} records into 'engagement'.")
        else:
            print(f"Error: {engagement_csv} not found.")

        # Users Table
        print("Creating 'users' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        
        # Add default users if table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            print("Populating default users...")
            default_users = [
                ('admin', hash_password('admin'), 'Admin/Instructor'),
                ('student', hash_password('student'), 'Student')
            ]
            cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", default_users)
            conn.commit()

        # Interventions Table (outreach flag log) — reuses the same idempotent
        # creator analytics.py calls on every app start, so the schema lives in one place
        print("Creating 'interventions' table...")
        ensure_interventions_table()

        # Verification
        print("\nVerifying database creation...")
        
        cursor.execute("SELECT count(*) FROM behavior")
        behavior_count = cursor.fetchone()[0]
        print(f"Records in 'behavior' table: {behavior_count}")

        cursor.execute("SELECT count(*) FROM engagement")
        engagement_count = cursor.fetchone()[0]
        print(f"Records in 'engagement' table: {engagement_count}")

        cursor.execute("SELECT count(*) FROM users")
        users_count = cursor.fetchone()[0]
        print(f"Records in 'users' table: {users_count}")

        cursor.execute("SELECT count(*) FROM interventions")
        interventions_count = cursor.fetchone()[0]
        print(f"Records in 'interventions' table: {interventions_count}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    setup_database()