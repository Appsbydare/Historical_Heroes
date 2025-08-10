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
    """Expand a node - show related events for people, related people for events"""
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
        
        # Get current network data (all nodes that are already visible)
        current_nodes = []
        current_links = []
        
        # Get all nodes that should be visible
        visible_node_ids = set()
        
        # Always include Korean War and key people
        visible_node_ids.update(['e1', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10'])
        
        # Add the clicked node
        visible_node_ids.add(node_id)
        
        # If expanding a person, add their related events
        if target_node.get('node_type') == 'Person':
            if node_id == 'p3':  # Truman
                visible_node_ids.update(['e1', 'e4', 'e5'])  # Korean War, WWI, WWII
            elif node_id == 'p4':  # Eisenhower
                visible_node_ids.update(['e1', 'e4', 'e5', 'e15', 'e16'])  # Korean War, WWI, WWII, Overlord, Normandy
            elif node_id == 'p5':  # MacArthur
                visible_node_ids.update(['e1', 'e4', 'e5', 'e35', 'e36', 'e51', 'e52'])  # Korean War, WWI, WWII, Philippines campaigns
            elif node_id == 'p6':  # Ridgway
                visible_node_ids.update(['e1', 'e4', 'e5', 'e15', 'e16'])  # Korean War, WWI, WWII, Overlord, Normandy
            elif node_id == 'p7':  # Walker
                visible_node_ids.update(['e1', 'e4', 'e5', 'e15', 'e16'])  # Korean War, WWI, WWII, Overlord, Normandy
            elif node_id == 'p8':  # Van Fleet
                visible_node_ids.update(['e1', 'e4', 'e5', 'e15', 'e16'])  # Korean War, WWI, WWII, Overlord, Normandy
            elif node_id == 'p9':  # Stratemeyer
                visible_node_ids.update(['e1', 'e4', 'e5'])  # Korean War, WWI, WWII
            elif node_id == 'p10':  # Joy
                visible_node_ids.update(['e1', 'e4', 'e5'])  # Korean War, WWI, WWII
            elif node_id == 'p1':  # Syngman Rhee
                visible_node_ids.update(['e1'])  # Korean War
            elif node_id == 'p2':  # Paik Sun-yup
                visible_node_ids.update(['e1'])  # Korean War
        
        # If expanding an event, add related people
        elif target_node.get('node_type') == 'Event':
            if node_id == 'e1':  # Korean War
                visible_node_ids.update(['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10'])
            elif node_id in ['e4', 'e5']:  # WWI, WWII
                visible_node_ids.update(['p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10'])
            elif node_id in ['e15', 'e16']:  # Overlord, Normandy
                visible_node_ids.update(['p4', 'p5', 'p6', 'p7', 'p8'])
            elif node_id in ['e35', 'e36', 'e51', 'e52']:  # Philippines campaigns
                visible_node_ids.update(['p5'])
        
        # Build nodes and links for visible nodes
        for node in csv_data:
            if node.get('node_id') in visible_node_ids:
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
                current_nodes.append(network_node)
        
        # Create links between visible nodes
        for source_id in visible_node_ids:
            for target_id in visible_node_ids:
                if source_id != target_id:
                    # Create logical connections based on Korean War relationships
                    if source_id == 'e1' and target_id.startswith('p'):  # Korean War to people
                        current_links.append({
                            'source': source_id,
                            'target': target_id,
                            'type': 'involvement'
                        })
                    elif source_id.startswith('p') and target_id == 'e1':  # People to Korean War
                        current_links.append({
                            'source': source_id,
                            'target': target_id,
                            'type': 'involvement'
                        })
                    elif source_id.startswith('p') and target_id.startswith('e'):  # People to events
                        # Add specific relationships
                        if (source_id in ['p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10'] and 
                            target_id in ['e4', 'e5']):  # Key people to WWI/WWII
                            current_links.append({
                                'source': source_id,
                                'target': target_id,
                                'type': 'involvement'
                            })
                        elif (source_id in ['p4', 'p5', 'p6', 'p7', 'p8'] and 
                              target_id in ['e15', 'e16']):  # Military leaders to Overlord/Normandy
                            current_links.append({
                                'source': source_id,
                                'target': target_id,
                                'type': 'involvement'
                            })
                        elif source_id == 'p5' and target_id in ['e35', 'e36', 'e51', 'e52']:  # MacArthur to Philippines
                            current_links.append({
                                'source': source_id,
                                'target': target_id,
                                'type': 'involvement'
                            })
        
        return jsonify({
            'nodes': current_nodes,
            'links': current_links,
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
    """Get network data for visualization - start with Korean War and key people"""
    try:
        if session_id != 1:
            return jsonify({'error': 'Session not found'}), 404
        
        csv_data = read_csv_data()
        
        if not csv_data:
            return jsonify({'error': 'No CSV data found'}), 500
        
        # Start with only Korean War and key people
        initial_nodes = []
        initial_links = []
        
        # Find Korean War (e1)
        korean_war = None
        key_people = []
        
        for node in csv_data:
            if node.get('node_id') == 'e1':  # Korean War
                korean_war = node
            elif node.get('node_id') in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10']:  # Key people
                key_people.append(node)
        
        # Add Korean War
        if korean_war:
            initial_nodes.append({
                'id': korean_war.get('node_id', ''),
                'title': korean_war.get('name', ''),
                'node_type': korean_war.get('node_type', ''),
                'degree': int(korean_war.get('degree', 0)),
                'description': korean_war.get('description', ''),
                'start_date': korean_war.get('start_date', ''),
                'end_date': korean_war.get('end_date', ''),
                'metadata': korean_war.get('metadata', {})
            })
        
        # Add key people and their connections to Korean War
        for person in key_people:
            initial_nodes.append({
                'id': person.get('node_id', ''),
                'title': person.get('name', ''),
                'node_type': person.get('node_type', ''),
                'degree': int(person.get('degree', 0)),
                'description': person.get('description', ''),
                'start_date': person.get('start_date', ''),
                'end_date': person.get('end_date', ''),
                'metadata': person.get('metadata', {})
            })
            
            # Connect to Korean War
            initial_links.append({
                'source': person.get('node_id', ''),
                'target': 'e1',
                'type': 'involvement'
            })
        
        return jsonify({
            'nodes': initial_nodes,
            'links': initial_links
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