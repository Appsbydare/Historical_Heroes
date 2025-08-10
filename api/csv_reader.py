import pandas as pd
import json
import os
from flask import Flask, jsonify

app = Flask(__name__)

# Cache the CSV data to avoid reading it multiple times
_csv_data = None

def read_csv_data():
    """Read data from Nodes.csv file with caching"""
    global _csv_data
    
    if _csv_data is not None:
        return _csv_data
    
    try:
        # Path to the CSV file
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'Nodes.csv')
        
        # Read CSV file with optimized settings
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Convert to list of dictionaries and cache
        _csv_data = df.to_dict('records')
        
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    try:
        if session_id != 1:
            return jsonify({'error': 'Session not found'}), 404
        
        csv_data = read_csv_data()
        
        # Count nodes by degree and type
        degree_counts = {}
        for node in csv_data:
            degree = node.get('degree', 0)
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/nodes', methods=['GET'])
def get_session_nodes(session_id):
    """Get nodes for a session"""
    try:
        if session_id != 1:
            return jsonify({'error': 'Session not found'}), 404
        
        csv_data = read_csv_data()
        
        # Transform data to match frontend expectations
        nodes = []
        for node in csv_data:
            transformed_node = {
                'id': node.get('node_id', ''),
                'node_id': node.get('node_id', ''),
                'name': node.get('name', ''),
                'url': '',  # CSV doesn't have URLs
                'node_type': node.get('node_type', ''),
                'degree': node.get('degree', 0),
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/network', methods=['GET'])
def get_network_data(session_id):
    """Get network data for visualization"""
    try:
        if session_id != 1:
            return jsonify({'error': 'Session not found'}), 404
        
        csv_data = read_csv_data()
        
        # Transform to network format
        network_nodes = []
        for node in csv_data:
            network_node = {
                'id': node.get('node_id', ''),
                'title': node.get('name', ''),
                'node_type': node.get('node_type', ''),
                'degree': node.get('degree', 0),
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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 