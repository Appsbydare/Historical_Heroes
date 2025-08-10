import sqlite3
import os

def backfill_node_ids(db_path="database/wikipedia_extraction.db"):
    db_path = os.path.join(os.path.dirname(__file__), db_path) if not os.path.isabs(db_path) else db_path
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Get all nodes without a node_id, ordered by id
    cursor.execute("SELECT id, node_type FROM nodes WHERE node_id IS NULL OR node_id = '' ORDER BY id")
    rows = cursor.fetchall()
    type_counters = {"Event": 0, "Person": 0}
    # Get current max for each type
    cursor.execute("SELECT node_type, MAX(CAST(SUBSTR(node_id, 2) AS INTEGER)) FROM nodes WHERE node_id IS NOT NULL AND node_id != '' GROUP BY node_type")
    for t, max_id in cursor.fetchall():
        type_counters[t] = max_id or 0
    for node_id, node_type in rows:
        type_counters[node_type] += 1
        new_node_id = f"{'e' if node_type == 'Event' else 'p'}{type_counters[node_type]}"
        cursor.execute("UPDATE nodes SET node_id = ? WHERE id = ?", (new_node_id, node_id))
    conn.commit()
    conn.close()
    print(f"Backfilled {len(rows)} node_id values.")

if __name__ == "__main__":
    backfill_node_ids() 