from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import threading
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import DatabaseManager
from extraction_manager import run_extraction
from csv_data_reader import create_network_data_from_csv, get_csv_session_info, read_nodes_from_csv

app = Flask(__name__)
CORS(app)

# Global storage for extraction status
extraction_status = {}

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all extraction sessions (including CSV session)"""
    try:
        # Get CSV session info
        csv_session = get_csv_session_info()
        
        # Get database sessions
        db = DatabaseManager()
        db_sessions = db.get_all_sessions()
        
        # Combine CSV and database sessions
        all_sessions = []
        if csv_session:
            all_sessions.append(csv_session)
        all_sessions.extend(db_sessions)
        
        return jsonify(all_sessions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    try:
        if session_id == 1:  # CSV session
            csv_session = get_csv_session_info()
            if csv_session:
                return jsonify({
                    'session': csv_session,
                    'degree_counts': {
                        0: {'Event': 1, 'Person': 0},
                        1: {'Event': 0, 'Person': 10},
                        2: {'Event': 5, 'Person': 0},
                        3: {'Event': 0, 'Person': 5}
                    }
                })
            else:
                return jsonify({'error': 'CSV session not found'}), 404
        else:
            # Database session
            db = DatabaseManager()
            summary = db.get_session_summary(session_id)
            if not summary:
                return jsonify({'error': 'Session not found'}), 404
            return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/nodes', methods=['GET'])
def get_session_nodes(session_id):
    """Get nodes for a session"""
    try:
        if session_id == 1:  # CSV session
            nodes = read_nodes_from_csv()
            return jsonify(nodes)
        else:
            # Database session
            db = DatabaseManager()
            nodes = db.get_session_nodes(session_id)
            return jsonify(nodes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/network', methods=['GET'])
def get_network_data(session_id):
    """Get network data for visualization"""
    try:
        if session_id == 1:  # CSV session
            # Get network data from CSV
            network_data = create_network_data_from_csv()
            return jsonify(network_data)
        else:
            # Database session
            db = DatabaseManager()
            nodes = db.get_session_nodes(session_id)
            
            # Convert to network format
            network_nodes = []
            for node in nodes:
                network_node = {
                    'id': node['node_id'],
                    'title': node['name'],
                    'node_type': node['node_type'],
                    'degree': node.get('degree', 0),
                    'description': node.get('description', ''),
                    'start_date': node.get('start_date', ''),
                    'end_date': node.get('end_date', ''),
                    'metadata': node.get('metadata', {})
                }
                network_nodes.append(network_node)
            
            # Create simple links (placeholder)
            links = []
            return jsonify({
                'nodes': network_nodes,
                'links': links
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/nodes/<node_id>/expand', methods=['POST'])
def expand_node(session_id, node_id):
    """Expand a node by finding related nodes"""
    try:
        if session_id == 1:  # CSV session
            # Get all nodes from CSV
            all_nodes = read_nodes_from_csv()
            
            # Find the target node
            target_node = None
            for node in all_nodes:
                if node['node_id'] == node_id:
                    target_node = node
                    break
            
            if not target_node:
                return jsonify({'error': 'Node not found'}), 404
            
            # Find related nodes based on node type and metadata
            related_nodes = []
            related_links = []
            
            if target_node['node_type'] == 'Event':
                # For events, find people who participated in related events
                # Look for people with similar metadata (battles, wars, etc.)
                for node in all_nodes:
                    if node['node_type'] == 'Person' and node['node_id'] != node_id:
                        # Check if person has metadata related to the event
                        if has_related_metadata(target_node, node):
                            related_nodes.append({
                                'id': node['node_id'],
                                'title': node['title'],
                                'node_type': node['node_type'],
                                'degree': target_node.get('degree', 0) + 1,
                                'description': node['description'],
                                'start_date': node['start_date'],
                                'end_date': node['end_date'],
                                'metadata': node['metadata']
                            })
                            related_links.append({
                                'source': node_id,
                                'target': node['node_id'],
                                'degree': 1
                            })
            else:
                # For people, find events they participated in
                for node in all_nodes:
                    if node['node_type'] == 'Event' and node['node_id'] != node_id:
                        # Check if event is related to the person
                        if has_related_metadata(node, target_node):
                            related_nodes.append({
                                'id': node['node_id'],
                                'title': node['title'],
                                'node_type': node['node_type'],
                                'degree': target_node.get('degree', 0) + 1,
                                'description': node['description'],
                                'start_date': node['start_date'],
                                'end_date': node['end_date'],
                                'metadata': node['metadata']
                            })
                            related_links.append({
                                'source': node_id,
                                'target': node['node_id'],
                                'degree': 1
                            })
            
            # Limit to first 10 related nodes to avoid overwhelming the visualization
            related_nodes = related_nodes[:10]
            related_links = related_links[:10]
            
            return jsonify({
                'nodes': related_nodes,
                'links': related_links
            })
        else:
            # Database session expansion (placeholder)
            return jsonify({
                'nodes': [],
                'links': []
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def has_related_metadata(event_node, person_node):
    """Check if a person is related to an event based on metadata"""
    try:
        event_metadata = event_node.get('metadata', {})
        person_metadata = person_node.get('metadata', {})
        
        # Check for common battle/war references
        event_desc = event_node.get('description', '').lower()
        person_desc = person_node.get('description', '').lower()
        
        # Simple keyword matching
        war_keywords = ['war', 'battle', 'conflict', 'campaign']
        for keyword in war_keywords:
            if keyword in event_desc and keyword in person_desc:
                return True
        
        # Check metadata for battles/wars
        if 'Battles / wars' in person_metadata:
            battles = person_metadata['Battles / wars']
            if isinstance(battles, str) and any(keyword in battles.lower() for keyword in war_keywords):
                return True
        
        return False
    except:
        return False

@app.route('/api/extract', methods=['POST'])
def start_extraction():
    """Start a new extraction"""
    try:
        data = request.json
        output_type = data.get('output_type', 'sql')
        seed_url = data.get('seed_url')
        max_degree = data.get('max_degree', 3)
        
        if not seed_url:
            return jsonify({'error': 'Seed URL is required'}), 400
        
        # Create session name
        session_name = f"Extraction from {seed_url.split('/')[-1]}"
        
        # Create session in database
        db = DatabaseManager()
        session_id = db.create_extraction_session(session_name, seed_url, max_degree)
        
        # Start extraction in background
        def run_extraction_thread():
            try:
                extraction_status[session_id] = {'status': 'running', 'progress': 0}
                
                def progress_callback(progress, message):
                    extraction_status[session_id] = {
                        'status': 'running',
                        'progress': progress,
                        'message': message
                    }
                
                result = run_extraction(
                    output_type=output_type,
                    seed_url=seed_url,
                    max_degree=max_degree,
                    session_id=session_id,
                    progress_callback=progress_callback
                )
                
                extraction_status[session_id] = {'status': 'completed', 'progress': 100}
                
            except Exception as e:
                extraction_status[session_id] = {'status': 'failed', 'error': str(e)}
        
        thread = threading.Thread(target=run_extraction_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({'session_id': session_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract/<int:session_id>/stop', methods=['POST'])
def stop_extraction(session_id):
    """Stop an extraction"""
    try:
        if session_id in extraction_status:
            extraction_status[session_id]['status'] = 'stopped'
        return jsonify({'message': 'Extraction stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract/<int:session_id>/status', methods=['GET'])
def get_extraction_status(session_id):
    """Get extraction status"""
    try:
        status = extraction_status.get(session_id, {'status': 'unknown', 'progress': 0})
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve frontend static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve the React frontend"""
    if path and os.path.exists(os.path.join('../frontend/dist', path)):
        return send_from_directory('../frontend/dist', path)
    else:
        return send_from_directory('../frontend/dist', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 