import csv
import json
import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cache the CSV data to avoid reading it multiple times
_csv_data = None

def read_csv_data():
    """Read data from Nodes.csv file with caching"""
    global _csv_data
    
    if _csv_data is not None:
        return _csv_data
    
    try:
        # Try multiple possible paths for the CSV file
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'Nodes.csv'),
            os.path.join(os.getcwd(), 'Nodes.csv'),
            'Nodes.csv'
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if csv_path is None:
            print("CSV file not found in any of the expected locations")
            return []
        
        print(f"Reading CSV from: {csv_path}")
        
        # Read CSV file using built-in csv module
        data = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data.append(row)
        
        _csv_data = data
        print(f"Successfully loaded {len(_csv_data)} nodes from CSV")
        return _csv_data
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions (for prototype, return a single CSV session)"""
    try:
        # For prototype, we'll create a single session representing the CSV data
        csv_data = read_csv_data()
        
        if not csv_data:
            return jsonify({'error': 'No CSV data found'}), 500
        
        # Count nodes by type
        events_count = len([node for node in csv_data if node.get('node_type') == 'Event'])
        people_count = len([node for node in csv_data if node.get('node_type') == 'Person'])
        
        session = {
            'id': 1,
            'name': 'Korean War Data (CSV)',
            'seed_url': 'https://en.wikipedia.org/wiki/Korean_War',
            'max_degree': 3,
            'total_nodes': len(csv_data),
            'status': 'completed',
            'started_at': '2024-01-01T00:00:00',
            'completed_at': '2024-01-01T00:00:00',
            'events_count': events_count,
            'people_count': people_count
        }
        
        return jsonify([session])
        
    except Exception as e:
        print(f"Error in get_sessions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    try:
        if session_id != 1:
            return jsonify({'error': 'Session not found'}), 404
        
        csv_data = read_csv_data()
        
        if not csv_data:
            return jsonify({'error': 'No CSV data found'}), 500
        
        # Count nodes by degree and type
        degree_counts = {}
        for node in csv_data:
            degree = int(node.get('degree', 0))
            node_type = node.get('node_type', 'Unknown')
            
            if degree not in degree_counts:
                degree_counts[degree] = {'Event': 0, 'Person': 0}
            
            if node_type in degree_counts[degree]:
                degree_counts[degree][node_type] += 1
        
        session = {
            'id': 1,
            'name': 'Korean War Data (CSV)',
            'seed_url': 'https://en.wikipedia.org/wiki/Korean_War',
            'max_degree': 3,
            'total_nodes': len(csv_data),
            'status': 'completed',
            'started_at': '2024-01-01T00:00:00',
            'completed_at': '2024-01-01T00:00:00'
        }
        
        return jsonify({
            'session': session,
            'degree_counts': degree_counts
        })
        
    except Exception as e:
        print(f"Error in get_session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/nodes', methods=['GET'])
def get_session_nodes(session_id):
    """Get nodes for a session"""
    try:
        if session_id != 1:
            return jsonify({'error': 'Session not found'}), 404
        
        csv_data = read_csv_data()
        
        if not csv_data:
            return jsonify({'error': 'No CSV data found'}), 500
        
        # Transform data to match frontend expectations
        nodes = []
        for node in csv_data:
            transformed_node = {
                'id': node.get('node_id', ''),
                'node_id': node.get('node_id', ''),
                'name': node.get('name', ''),
                'url': '',  # CSV doesn't have URLs
                'node_type': node.get('node_type', ''),
                'degree': int(node.get('degree', 0)),
                'parent_url': '',  # CSV doesn't have parent URLs
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00',
                'description': node.get('description', ''),
                'start_date': node.get('start_date', ''),
                'end_date': node.get('end_date', ''),
                'metadata': node.get('metadata', {})
            }
            nodes.append(transformed_node)
        
        return jsonify(nodes)
        
    except Exception as e:
        print(f"Error in get_session_nodes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/nodes/<node_id>/expand', methods=['POST'])
def expand_node(session_id, node_id):
    """Expand a node (for prototype, return the same network data)"""
    try:
        if session_id != 1:
            return jsonify({'error': 'Session not found'}), 404
        
        csv_data = read_csv_data()
        
        if not csv_data:
            return jsonify({'error': 'No CSV data found'}), 500
        
        # Find the specific node
        target_node = None
        for node in csv_data:
            if node.get('node_id') == node_id:
                target_node = node
                break
        
        if not target_node:
            return jsonify({'error': 'Node not found'}), 404
        
        # For prototype, return the same network data
        # In a real implementation, this would fetch related nodes
        network_nodes = []
        for node in csv_data:
            network_node = {
                'id': node.get('node_id', ''),
                'title': node.get('name', ''),
                'node_type': node.get('node_type', ''),
                'degree': int(node.get('degree', 0)),
                'description': node.get('description', ''),
                'start_date': node.get('start_date', ''),
                'end_date': node.get('end_date', ''),
                'metadata': node.get('metadata', {})
            }
            network_nodes.append(network_node)
        
        # Create simple links (placeholder - could be enhanced later)
        links = []
        
        return jsonify({
            'nodes': network_nodes,
            'links': links,
            'expanded_node': {
                'id': target_node.get('node_id', ''),
                'title': target_node.get('name', ''),
                'node_type': target_node.get('node_type', ''),
                'description': target_node.get('description', '')
            }
        })
        
    except Exception as e:
        print(f"Error in expand_node: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/network', methods=['GET'])
def get_network_data(session_id):
    """Get network data for visualization"""
    try:
        if session_id != 1:
            return jsonify({'error': 'Session not found'}), 404
        
        csv_data = read_csv_data()
        
        if not csv_data:
            return jsonify({'error': 'No CSV data found'}), 500
        
        # Transform to network format
        network_nodes = []
        for node in csv_data:
            network_node = {
                'id': node.get('node_id', ''),
                'title': node.get('name', ''),
                'node_type': node.get('node_type', ''),
                'degree': int(node.get('degree', 0)),
                'description': node.get('description', ''),
                'start_date': node.get('start_date', ''),
                'end_date': node.get('end_date', ''),
                'metadata': node.get('metadata', {})
            }
            network_nodes.append(network_node)
        
        # Create simple links (placeholder - could be enhanced later)
        links = []
        
        return jsonify({
            'nodes': network_nodes,
            'links': links
        })
        
    except Exception as e:
        print(f"Error in get_network_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def start_extraction():
    """Start extraction (for prototype, just return success)"""
    try:
        # For prototype, we don't actually run extraction
        # Just return a success response
        return jsonify({
            'session_id': 1,
            'message': 'Prototype mode - using existing CSV data'
        })
        
    except Exception as e:
        print(f"Error in start_extraction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract/<int:session_id>/status', methods=['GET'])
def get_extraction_status(session_id):
    """Get extraction status (for prototype, always completed)"""
    try:
        return jsonify({
            'status': 'completed',
            'progress': 100,
            'message': 'Using existing CSV data'
        })
        
    except Exception as e:
        print(f"Error in get_extraction_status: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 