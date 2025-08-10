import csv
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from database.database import DatabaseManager

CSV_FILE = os.path.join(os.path.dirname(__file__), '..', 'Nodes.csv')

COLUMNS = [
    'node_id', 'node_type', 'name', 'description', 'start_date', 'end_date', 'metadata'
]

def get_existing_node_ids():
    if not os.path.exists(CSV_FILE):
        return set()
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return set(row['node_id'] for row in reader if row['node_id'])

def node_to_csv_row(node):
    # Only write if node_id and title are present
    if not node.get('node_id') or not node.get('title'):
        return None
    return {
        'node_id': node['node_id'],
        'node_type': node['node_type'],
        'name': node['title'],
        'description': node.get('description', ''),
        'start_date': node.get('start_date', ''),
        'end_date': node.get('end_date', ''),
        'metadata': json.dumps(json.loads(node.get('metadata', '{}')), ensure_ascii=False)
            if node.get('metadata') else '{}',
    }

def append_new_nodes_to_csv():
    db = DatabaseManager()
    all_nodes = db.get_all_nodes()
    existing_ids = get_existing_node_ids()
    new_nodes = [n for n in all_nodes if n.get('node_id') and n['node_id'] not in existing_ids]
    if not new_nodes:
        print('No new nodes to append.')
        return
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        count = 0
        for node in new_nodes:
            row = node_to_csv_row(node)
            if row:
                writer.writerow(row)
                count += 1
    print(f'Appended {count} new nodes to {CSV_FILE}')

if __name__ == '__main__':
    append_new_nodes_to_csv() 