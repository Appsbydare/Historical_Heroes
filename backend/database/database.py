import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_data_dir():
    base_dir = get_base_dir()
    data_dir = os.path.join(base_dir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_db_path():
    return os.path.join(get_data_dir(), 'wikipedia_extraction.db')

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = get_db_path()
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create nodes table (with new columns)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                node_type TEXT NOT NULL,
                degree INTEGER NOT NULL,
                parent_url TEXT,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create extraction_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extraction_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                seed_url TEXT NOT NULL,
                max_degree INTEGER NOT NULL,
                total_nodes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create session_nodes table to link sessions with nodes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_nodes (
                session_id INTEGER,
                node_id INTEGER,
                FOREIGN KEY (session_id) REFERENCES extraction_sessions (id),
                FOREIGN KEY (node_id) REFERENCES nodes (id),
                PRIMARY KEY (session_id, node_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_extraction_session(self, session_name: str, seed_url: str, max_degree: int) -> int:
        """Create a new extraction session and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO extraction_sessions (session_name, seed_url, max_degree)
            VALUES (?, ?, ?)
        ''', (session_name, seed_url, max_degree))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def save_node(self, node_data: Dict, session_id: int) -> int:
        """Save a node to the database and return its ID. Handles new fields."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if node already exists
        cursor.execute('SELECT id, node_id FROM nodes WHERE url = ?', (node_data['url'],))
        existing_node = cursor.fetchone()
        
        # Generate node_id if not present
        if existing_node:
            node_id_db = existing_node[1]
        else:
            # Count existing nodes of this type to generate next id
            cursor.execute('SELECT COUNT(*) FROM nodes WHERE node_type = ?', (node_data['node_type'],))
            count = cursor.fetchone()[0] + 1
            node_id_db = f"{'e' if node_data['node_type'] == 'Event' else 'p'}{count}"
        
        if existing_node:
            node_id = existing_node[0]
            # Update the existing node
            cursor.execute('''
                UPDATE nodes 
                SET node_id = ?, title = ?, node_type = ?, degree = ?, parent_url = ?, description = ?, start_date = ?, end_date = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (node_id_db, node_data['title'], node_data['node_type'], node_data['degree'], 
                  node_data.get('parent_url'), node_data.get('description'), node_data.get('start_date'), node_data.get('end_date'),
                  json.dumps(node_data.get('metadata', {})), node_id))
        else:
            # Insert new node
            cursor.execute('''
                INSERT INTO nodes (node_id, title, url, node_type, degree, parent_url, description, start_date, end_date, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (node_id_db, node_data['title'], node_data['url'], node_data['node_type'], 
                  node_data['degree'], node_data.get('parent_url'), node_data.get('description'), node_data.get('start_date'), node_data.get('end_date'),
                  json.dumps(node_data.get('metadata', {}))))
            node_id = cursor.lastrowid
        
        # Link node to session
        cursor.execute('''
            INSERT OR IGNORE INTO session_nodes (session_id, node_id)
            VALUES (?, ?)
        ''', (session_id, node_id))
        
        conn.commit()
        conn.close()
        
        return node_id_db
    
    def update_session_status(self, session_id: int, status: str, total_nodes: int = None):
        """Update the status of an extraction session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status == 'completed':
            cursor.execute('''
                UPDATE extraction_sessions 
                SET status = ?, total_nodes = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, total_nodes, session_id))
        else:
            cursor.execute('''
                UPDATE extraction_sessions 
                SET status = ?, total_nodes = ?
                WHERE id = ?
            ''', (status, total_nodes, session_id))
        
        conn.commit()
        conn.close()
    
    def get_session_nodes(self, session_id: int) -> List[Dict]:
        """Get all nodes for a specific session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.* FROM nodes n
            JOIN session_nodes sn ON n.id = sn.node_id
            WHERE sn.session_id = ?
            ORDER BY n.degree, n.node_type, n.title
        ''', (session_id,))
        
        columns = [description[0] for description in cursor.description]
        nodes = []
        
        for row in cursor.fetchall():
            node_dict = dict(zip(columns, row))
            nodes.append(node_dict)
        
        conn.close()
        return nodes
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all extraction sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM extraction_sessions
            ORDER BY created_at DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        sessions = []
        
        for row in cursor.fetchall():
            session_dict = dict(zip(columns, row))
            sessions.append(session_dict)
        
        conn.close()
        return sessions
    
    def get_nodes_by_degree(self, session_id: int, degree: int) -> List[Dict]:
        """Get nodes for a specific session and degree"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.* FROM nodes n
            JOIN session_nodes sn ON n.id = sn.node_id
            WHERE sn.session_id = ? AND n.degree = ?
            ORDER BY n.node_type, n.title
        ''', (session_id, degree))
        
        columns = [description[0] for description in cursor.description]
        nodes = []
        
        for row in cursor.fetchall():
            node_dict = dict(zip(columns, row))
            nodes.append(node_dict)
        
        conn.close()
        return nodes
    
    def get_session_summary(self, session_id: int) -> Dict:
        """Get a summary of a specific session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute('SELECT * FROM extraction_sessions WHERE id = ?', (session_id,))
        session = cursor.fetchone()
        
        if not session:
            conn.close()
            return None
        
        # Get degree-wise counts
        cursor.execute('''
            SELECT n.degree, n.node_type, COUNT(*) as count
            FROM nodes n
            JOIN session_nodes sn ON n.id = sn.node_id
            WHERE sn.session_id = ?
            GROUP BY n.degree, n.node_type
            ORDER BY n.degree, n.node_type
        ''', (session_id,))
        
        degree_counts = {}
        for row in cursor.fetchall():
            degree, node_type, count = row
            if degree not in degree_counts:
                degree_counts[degree] = {'Event': 0, 'Person': 0}
            degree_counts[degree][node_type] = count
        
        conn.close()
        
        return {
            'session': session,
            'degree_counts': degree_counts
        } 

    def get_all_nodes(self) -> List[Dict]:
        """Get all nodes in the database (for CSV export)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM nodes ORDER BY id')
        columns = [description[0] for description in cursor.description]
        nodes = []
        for row in cursor.fetchall():
            node_dict = dict(zip(columns, row))
            nodes.append(node_dict)
        conn.close()
        return nodes 