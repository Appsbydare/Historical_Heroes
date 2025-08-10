import csv
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wikipedia_extractor import WikipediaExtractor, ExtractedNode

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # Running as bundled exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_data_dir():
    base_dir = get_base_dir()
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_csv_path():
    return os.path.join(get_data_dir(), 'Nodes.csv')

def get_db_path():
    return os.path.join(get_data_dir(), 'wikipedia_extraction.db')

def generate_node_ids(nodes):
    """Assign node_id to each node in the format eN/pN based on type and order."""
    event_count = 0
    person_count = 0
    for node in nodes:
        if node.node_type == 'Event':
            event_count += 1
            node.node_id = f'e{event_count}'
        elif node.node_type == 'Person':
            person_count += 1
            node.node_id = f'p{person_count}'
        else:
            node.node_id = ''
    return nodes

CSV_COLUMNS = [
    'node_id', 'node_type', 'name', 'description', 'start_date', 'end_date', 'metadata'
]

def get_existing_name_parent_pairs(filename=None):
    if filename is None:
        filename = get_csv_path()
    pairs = set()
    if not os.path.exists(filename):
        return pairs
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pairs.add((row['name'], row.get('parent_url', '')))
    return pairs

def save_nodes_to_csv(nodes, filename=None):
    """Append only new nodes to CSV, checking for duplicates by (name, parent_url)."""
    if filename is None:
        filename = get_csv_path()
    file_exists = os.path.exists(filename)
    existing_pairs = get_existing_name_parent_pairs(filename) if file_exists else set()
    rows_to_write = []
    for node in nodes:
        pair = (node.title, getattr(node, 'parent_url', ''))
        if pair not in existing_pairs:
            rows_to_write.append({
                'node_id': getattr(node, 'node_id', ''),
                'node_type': node.node_type,
                'name': node.title,
                'description': getattr(node, 'description', ''),
                'start_date': getattr(node, 'start_date', ''),
                'end_date': getattr(node, 'end_date', ''),
                'metadata': json.dumps(getattr(node, 'metadata', {}), ensure_ascii=False)
            })
            existing_pairs.add(pair)
    mode = 'a' if file_exists else 'w'
    with open(filename, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        for row in rows_to_write:
            writer.writerow(row)

def run_extraction(output_type='sql', seed_url=None, max_degree=3, stop_flag=None, log_callback=None, session_id=None, progress_callback=None):
    """Run extraction and save results based on output_type ('sql' or 'csv')."""
    if not seed_url:
        seed_url = 'https://en.wikipedia.org/wiki/Korean_War'
    
    # Import database manager here to avoid circular imports
    from database.database import DatabaseManager
    db = DatabaseManager()
    
    extractor = WikipediaExtractor()
    extractor.max_degree = max_degree
    
    # Custom log callback that also updates progress
    def combined_callback(message):
        if log_callback:
            log_callback(message)
        
        # Estimate progress based on degree
        if progress_callback and 'degree' in message.lower():
            try:
                # Extract degree from message
                degree_match = message.split('degree')[0].strip().split()[-1]
                if degree_match.isdigit():
                    degree = int(degree_match)
                    progress = min(90, (degree / max_degree) * 90)  # Reserve 10% for completion
                    progress_callback(progress, message)
            except:
                pass
    
    nodes = extractor.extract_data(seed_url, stop_flag=stop_flag, log_callback=combined_callback)
    
    # Ensure all nodes have required attributes
    for node in nodes:
        if not hasattr(node, 'description'):
            node.description = ''
        if not hasattr(node, 'start_date'):
            node.start_date = ''
        if not hasattr(node, 'end_date'):
            node.end_date = ''
        if not hasattr(node, 'metadata'):
            node.metadata = {}
    
    if output_type == 'csv':
        generate_node_ids(nodes)
        save_nodes_to_csv(nodes)
        
        if session_id:
            # Update session status
            db.update_session_status(session_id, 'completed', len(nodes))
        
        if progress_callback:
            progress_callback(100, f'Extraction completed. {len(nodes)} nodes saved to CSV.')
        
        return f'Extraction completed. {len(nodes)} new nodes appended to Nodes.csv.'
    else:
        # Save to database with session tracking
        total_nodes = 0
        for node in nodes:
            node_data = {
                'title': node.title,
                'url': getattr(node, 'url', ''),
                'node_type': node.node_type,
                'degree': getattr(node, 'degree', 0),
                'parent_url': getattr(node, 'parent_url', ''),
                'description': node.description,
                'start_date': node.start_date,
                'end_date': node.end_date,
                'metadata': node.metadata
            }
            
            if session_id:
                db.save_node(node_data, session_id)
                total_nodes += 1
        
        if session_id:
            # Update session status
            db.update_session_status(session_id, 'completed', total_nodes)
        
        if progress_callback:
            progress_callback(100, f'Extraction completed. {total_nodes} nodes saved to database.')
        
        return f'Extraction completed and saved to SQL database. {total_nodes} nodes processed.' 