import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.database import DatabaseManager

def print_session_list():
    """Print all extraction sessions"""
    db = DatabaseManager()
    sessions = db.get_all_sessions()
    
    print("=== Extraction Sessions ===")
    print(f"{'ID':<5} {'Name':<30} {'Status':<12} {'Nodes':<8} {'Created':<20}")
    print("-" * 80)
    
    for session in sessions:
        session_id = session[0]
        name = session[1][:28] + ".." if len(session[1]) > 30 else session[1]
        status = session[5]
        total_nodes = session[4] or 0
        created = session[7][:19] if session[7] else "N/A"
        
        print(f"{session_id:<5} {name:<30} {status:<12} {total_nodes:<8} {created:<20}")

def print_session_details(session_id: int):
    """Print detailed information about a specific session"""
    db = DatabaseManager()
    summary = db.get_session_summary(session_id)
    
    if not summary:
        print(f"Session {session_id} not found.")
        return
    
    session_info = summary['session']
    print(f"\n=== Session {session_id} Details ===")
    print(f"Name: {session_info[1]}")
    print(f"Seed URL: {session_info[2]}")
    print(f"Max Degree: {session_info[3]}")
    print(f"Total Nodes: {session_info[4]}")
    print(f"Status: {session_info[5]}")
    print(f"Started: {session_info[6]}")
    print(f"Completed: {session_info[7]}")
    
    print(f"\n=== Nodes by Degree ===")
    degree_counts = summary['degree_counts']
    for degree in sorted(degree_counts.keys()):
        events = degree_counts[degree].get('Event', 0)
        people = degree_counts[degree].get('Person', 0)
        print(f"Degree {degree}: {events} Events, {people} People")

def print_session_nodes(session_id: int, degree: int = None):
    """Print nodes for a specific session"""
    db = DatabaseManager()
    
    if degree is not None:
        nodes = db.get_nodes_by_degree(session_id, degree)
        print(f"\n=== Session {session_id} - Degree {degree} Nodes ===")
    else:
        nodes = db.get_session_nodes(session_id)
        print(f"\n=== Session {session_id} - All Nodes ===")
    
    print(f"{'Type':<8} {'Degree':<8} {'Title':<50} {'URL':<60}")
    print("-" * 130)
    
    for node in nodes:
        node_type = node['node_type']
        degree = node['degree']
        title = node['title'][:48] + ".." if len(node['title']) > 50 else node['title']
        url = node['url'][:58] + ".." if len(node['url']) > 60 else node['url']
        
        print(f"{node_type:<8} {degree:<8} {title:<50} {url:<60}")

def export_session_to_json(session_id: int, filename: str = None):
    """Export session data to JSON file"""
    db = DatabaseManager()
    nodes = db.get_session_nodes(session_id)
    summary = db.get_session_summary(session_id)
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{session_id}_{timestamp}.json"
    
    export_data = {
        'session_info': summary['session'] if summary else None,
        'nodes': nodes,
        'exported_at': datetime.now().isoformat()
    }
    
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"Session {session_id} exported to {filename}")

def main():
    """Main function for database queries"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python database_query.py list                    # List all sessions")
        print("  python database_query.py details <session_id>    # Show session details")
        print("  python database_query.py nodes <session_id>      # Show all nodes")
        print("  python database_query.py nodes <session_id> <degree>  # Show nodes by degree")
        print("  python database_query.py export <session_id> [filename]  # Export to JSON")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        print_session_list()
    
    elif command == "details":
        if len(sys.argv) < 3:
            print("Please provide session ID")
            return
        session_id = int(sys.argv[2])
        print_session_details(session_id)
    
    elif command == "nodes":
        if len(sys.argv) < 3:
            print("Please provide session ID")
            return
        session_id = int(sys.argv[2])
        degree = int(sys.argv[3]) if len(sys.argv) > 3 else None
        print_session_nodes(session_id, degree)
    
    elif command == "export":
        if len(sys.argv) < 3:
            print("Please provide session ID")
            return
        session_id = int(sys.argv[2])
        filename = sys.argv[3] if len(sys.argv) > 3 else None
        export_session_to_json(session_id, filename)
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main() 