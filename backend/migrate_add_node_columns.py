import sqlite3
import os

def add_column_if_not_exists(cursor, table, column, coltype):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), "database/wikipedia_extraction.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    add_column_if_not_exists(cursor, "nodes", "node_id", "TEXT")
    add_column_if_not_exists(cursor, "nodes", "description", "TEXT")
    add_column_if_not_exists(cursor, "nodes", "start_date", "TEXT")
    add_column_if_not_exists(cursor, "nodes", "end_date", "TEXT")
    add_column_if_not_exists(cursor, "nodes", "metadata", "TEXT")
    conn.commit()
    conn.close()
    print("Migration complete. All required columns are present.")

if __name__ == "__main__":
    migrate() 