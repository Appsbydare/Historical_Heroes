#!/usr/bin/env python3
"""
CSV Data Reader for Wikipedia Extraction Manager
Reads data from Nodes.csv and converts to network format
"""

import csv
import json
import os
import sys
from pathlib import Path

def get_csv_path():
    """Get the path to Nodes.csv in the project root"""
    project_root = Path(__file__).parent.parent
    return project_root / "Nodes.csv"

def read_nodes_from_csv():
    """Read all nodes from Nodes.csv file"""
    csv_path = get_csv_path()
    
    if not csv_path.exists():
        print(f"❌ Error: Nodes.csv not found at {csv_path}")
        return []
    
    nodes = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse metadata JSON if it exists
                metadata = {}
                if row.get('metadata'):
                    try:
                        metadata = json.loads(row['metadata'])
                    except json.JSONDecodeError:
                        metadata = {}
                
                node = {
                    'node_id': row.get('node_id', ''),
                    'title': row.get('name', row.get('title', '')),
                    'node_type': row.get('node_type', ''),
                    'description': row.get('description', ''),
                    'start_date': row.get('start_date', ''),
                    'end_date': row.get('end_date', ''),
                    'metadata': metadata,
                    'degree': 0,  # We'll calculate this based on relationships
                    'url': '',  # Not in CSV, will be empty
                    'parent_url': ''  # Not in CSV, will be empty
                }
                nodes.append(node)
        
        print(f"✅ Loaded {len(nodes)} nodes from {csv_path}")
        return nodes
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return []

def create_network_data_from_csv():
    """Create network data structure from CSV nodes"""
    nodes = read_nodes_from_csv()
    
    if not nodes:
        return {'nodes': [], 'links': []}
    
    # Create network nodes
    network_nodes = []
    for node in nodes:
        network_node = {
            'id': node['node_id'],
            'title': node['title'],
            'node_type': node['node_type'],
            'degree': node['degree'],
            'description': node['description'],
            'start_date': node['start_date'],
            'end_date': node['end_date'],
            'metadata': node['metadata']
        }
        network_nodes.append(network_node)
    
    # Create simple links based on node type relationships
    # For now, we'll create a simple hierarchical structure
    links = []
    events = [n for n in network_nodes if n['node_type'] == 'Event']
    people = [n for n in network_nodes if n['node_type'] == 'Person']
    
    # Connect first event to first few people (simplified relationship)
    if events and people:
        main_event = events[0]
        for i, person in enumerate(people[:5]):  # Connect first 5 people to main event
            links.append({
                'source': main_event['id'],
                'target': person['id'],
                'degree': 1
            })
    
    return {
        'nodes': network_nodes,
        'links': links
    }

def get_csv_session_info():
    """Get session information for the CSV data"""
    csv_path = get_csv_path()
    
    if not csv_path.exists():
        return None
    
    # Get file stats
    stat = csv_path.stat()
    node_count = len(read_nodes_from_csv())
    
    return {
        'id': 1,  # Use ID 1 for CSV session
        'session_name': 'CSV Data Session',
        'seed_url': 'https://en.wikipedia.org/wiki/Korean_War',
        'max_degree': 3,
        'total_nodes': node_count,
        'status': 'completed',
        'started_at': stat.st_ctime,
        'completed_at': stat.st_mtime,
        'created_at': stat.st_ctime
    }

if __name__ == "__main__":
    # Test the CSV reader
    print("Testing CSV Data Reader...")
    network_data = create_network_data_from_csv()
    print(f"Network nodes: {len(network_data['nodes'])}")
    print(f"Network links: {len(network_data['links'])}")
    
    session_info = get_csv_session_info()
    if session_info:
        print(f"Session info: {session_info['session_name']} - {session_info['total_nodes']} nodes") 