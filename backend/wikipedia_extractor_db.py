import requests
import time
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
import csv

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.database import DatabaseManager

CSV_FILE = os.path.join(os.path.dirname(__file__), 'database', 'Nodes.csv')
CSV_COLUMNS = [
    'node_id', 'node_type', 'name', 'description', 'start_date', 'end_date', 'metadata'
]

def append_or_update_csv(node):
    """Append or update a node in the CSV file, avoiding duplicates by node_id."""
    if not node.get('node_id') or not node.get('title'):
        return
    row = {
        'node_id': node['node_id'],
        'node_type': node['node_type'],
        'name': node['title'],
        'description': node.get('description', ''),
        'start_date': node.get('start_date', ''),
        'end_date': node.get('end_date', ''),
        'metadata': json.dumps(node.get('metadata', {}), ensure_ascii=False) if node.get('metadata') else '{}',
    }
    # Read all existing rows
    rows = []
    found = False
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r['node_id'] == row['node_id']:
                    rows.append(row)
                    found = True
                else:
                    rows.append(r)
    if not found:
        rows.append(row)
    # Write back all rows
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

@dataclass
class ExtractedNode:
    """Represents a node (Event or Person) extracted from Wikipedia"""
    title: str
    url: str
    node_type: str  # 'Event' or 'Person'
    degree: int
    parent_url: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

class WikipediaExtractorDB:
    def __init__(self, base_url: str = "https://en.wikipedia.org", db_path: str = "database/wikipedia_extraction.db"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.extracted_nodes: List[ExtractedNode] = []
        self.visited_urls: Set[str] = set()
        self.max_degree = 3
        self.db_manager = DatabaseManager(db_path)
        self.session_id = None
        
    def log_status(self, message: str):
        """Print status message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        sys.stdout.flush()
    
    def get_wikipedia_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a Wikipedia page"""
        try:
            self.log_status(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            self.log_status(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_infobox_data(self, soup: BeautifulSoup) -> Dict[str, any]:
        """Extract data from Wikipedia infobox, including description, dates, and metadata."""
        infobox_data = {}
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return infobox_data
        rows = infobox.find_all('tr')
        # Extract description (first caption or summary row)
        description = None
        if infobox.find('caption'):
            description = infobox.find('caption').get_text(strip=True)
        else:
            for row in rows:
                td = row.find('td')
                if td and not row.find('th'):
                    description = td.get_text(strip=True)
                    break
        infobox_data['description'] = description
        # Extract dates and metadata
        for i, row in enumerate(rows):
            th = row.find('th')
            if th:
                header_text = th.get_text(strip=True)
                td = row.find('td')
                # Dates
                if header_text.lower() in ['born', 'date', 'start date', 'started', 'begin', 'birth'] and td:
                    infobox_data['start_date'] = td.get_text(strip=True)
                if header_text.lower() in ['died', 'end date', 'ended', 'death'] and td:
                    infobox_data['end_date'] = td.get_text(strip=True)
                # For events, look for start/end in 'Date' row
                if header_text.lower() == 'date' and td:
                    date_text = td.get_text(strip=True)
                    # Try to split start/end
                    if '–' in date_text:
                        parts = date_text.split('–')
                        infobox_data['start_date'] = parts[0].strip()
                        infobox_data['end_date'] = parts[1].strip() if len(parts) > 1 else None
                    else:
                        infobox_data['start_date'] = date_text
                # Metadata
                if header_text in ['Commanders and leaders', 'Battles/wars']:
                    # Already handled elsewhere
                    continue
                # Add other interesting fields to metadata
                if td and header_text not in ['Commanders and leaders', 'Battles/wars']:
                    if 'metadata' not in infobox_data:
                        infobox_data['metadata'] = {}
                    infobox_data['metadata'][header_text] = td.get_text(strip=True)
        return infobox_data
    
    def is_event_page(self, soup: BeautifulSoup) -> bool:
        """Determine if the page is an event page"""
        # Check for event-related categories or templates
        categories = soup.find_all('a', href=re.compile(r'/wiki/Category:'))
        category_texts = [cat.get_text(strip=True).lower() for cat in categories]
        
        event_indicators = ['wars', 'battles', 'conflicts', 'campaigns', 'operations']
        return any(indicator in ' '.join(category_texts) for indicator in event_indicators)
    
    def is_person_page(self, soup: BeautifulSoup) -> bool:
        """Determine if the page is a person page"""
        # Check for person-related categories or templates
        categories = soup.find_all('a', href=re.compile(r'/wiki/Category:'))
        category_texts = [cat.get_text(strip=True).lower() for cat in categories]
        
        person_indicators = ['people', 'person', 'military', 'generals', 'commanders', 'leaders']
        return any(indicator in ' '.join(category_texts) for indicator in person_indicators)
    
    def get_page_title(self, soup: BeautifulSoup) -> str:
        """Extract the page title"""
        title_elem = soup.find('h1', id='firstHeading')
        if title_elem:
            return title_elem.get_text(strip=True)
        return "Unknown Title"
    
    def extract_related_nodes(self, url: str, degree: int) -> List[ExtractedNode]:
        """Extract related nodes based on the current page type"""
        soup = self.get_wikipedia_page(url)
        if not soup:
            return []
        
        title = self.get_page_title(soup)
        infobox_data = self.extract_infobox_data(soup)
        
        # Determine page type
        is_event = self.is_event_page(soup)
        is_person = self.is_person_page(soup)
        
        if is_event:
            self.log_status(f"Processing EVENT: {title} (Degree {degree})")
            return self.extract_people_from_event(url, title, infobox_data, degree)
        elif is_person:
            self.log_status(f"Processing PERSON: {title} (Degree {degree})")
            return self.extract_events_from_person(url, title, infobox_data, degree)
        else:
            self.log_status(f"Unknown page type for: {title}")
            return []
    
    def extract_people_from_event(self, event_url: str, event_title: str, infobox_data: Dict, degree: int) -> List[ExtractedNode]:
        people = []
        # Use description, dates, and metadata for the event node
        self.update_node_extra_fields(event_url, infobox_data)
        if 'Commanders and leaders' in infobox_data:
            for person_name in infobox_data['Commanders and leaders']:
                person_url = f"{self.base_url}/wiki/{person_name.replace(' ', '_')}"
                if person_url not in self.visited_urls:
                    self.visited_urls.add(person_url)
                    # Fetch person page for extra fields
                    person_soup = self.get_wikipedia_page(person_url)
                    person_infobox = self.extract_infobox_data(person_soup) if person_soup else {}
                    people.append(ExtractedNode(
                        title=person_name,
                        url=person_url,
                        node_type='Person',
                        degree=degree + 1,
                        parent_url=event_url
                    ))
                    self.update_node_extra_fields(person_url, person_infobox)
                    self.log_status(f"  -> Found PERSON: {person_name}")
        return people

    def extract_events_from_person(self, person_url: str, person_title: str, infobox_data: Dict, degree: int) -> List[ExtractedNode]:
        events = []
        # Use description, dates, and metadata for the person node
        self.update_node_extra_fields(person_url, infobox_data)
        if 'Battles/wars' in infobox_data:
            for event_name in infobox_data['Battles/wars']:
                event_url = f"{self.base_url}/wiki/{event_name.replace(' ', '_')}"
                if event_url not in self.visited_urls:
                    self.visited_urls.add(event_url)
                    # Fetch event page for extra fields
                    event_soup = self.get_wikipedia_page(event_url)
                    event_infobox = self.extract_infobox_data(event_soup) if event_soup else {}
                    events.append(ExtractedNode(
                        title=event_name,
                        url=event_url,
                        node_type='Event',
                        degree=degree + 1,
                        parent_url=person_url
                    ))
                    self.update_node_extra_fields(event_url, event_infobox)
                    self.log_status(f"  -> Found EVENT: {event_name}")
        return events

    def update_node_extra_fields(self, url: str, infobox_data: Dict):
        """Update the extra fields for a node in self.extracted_nodes by url."""
        for node in self.extracted_nodes:
            if node.url == url:
                node.description = infobox_data.get('description')
                node.start_date = infobox_data.get('start_date')
                node.end_date = infobox_data.get('end_date')
                node.metadata = infobox_data.get('metadata', {})
                break

    def save_node_to_db(self, node: ExtractedNode):
        node_data = {
            'title': node.title,
            'url': node.url,
            'node_type': node.node_type,
            'degree': node.degree,
            'parent_url': node.parent_url,
            'description': getattr(node, 'description', None),
            'start_date': getattr(node, 'start_date', None),
            'end_date': getattr(node, 'end_date', None),
            'metadata': getattr(node, 'metadata', {})
        }
        try:
            node_id = self.db_manager.save_node(node_data, self.session_id)
            # Add node_id to node_data for CSV
            node_data['node_id'] = node_id
            append_or_update_csv(node_data)
        except Exception as e:
            self.log_status(f"Error saving node to database/CSV: {str(e)}")
    
    def extract_data(self, seed_url: str, session_name: str = None) -> List[ExtractedNode]:
        """Main extraction method with depth limiting and database storage"""
        if not session_name:
            session_name = f"Extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.log_status("Starting Wikipedia data extraction...")
        self.log_status(f"Session Name: {session_name}")
        self.log_status(f"Seed URL: {seed_url}")
        self.log_status(f"Max depth: {self.max_degree} degrees")
        self.log_status("-" * 50)
        
        # Create database session
        self.session_id = self.db_manager.create_extraction_session(
            session_name, seed_url, self.max_degree
        )
        self.log_status(f"Database session created with ID: {self.session_id}")
        
        # Initialize with seed event
        seed_node = ExtractedNode(
            title="Korean War",
            url=seed_url,
            node_type='Event',
            degree=0
        )
        self.extracted_nodes.append(seed_node)
        self.visited_urls.add(seed_url)
        
        # Save seed node to database
        self.save_node_to_db(seed_node)
        
        # Process nodes by degree
        for degree in range(self.max_degree + 1):
            self.log_status(f"\n=== Processing Degree {degree} ===")
            
            # Get all nodes at current degree
            current_degree_nodes = [node for node in self.extracted_nodes if node.degree == degree]
            
            if not current_degree_nodes:
                self.log_status(f"No nodes found at degree {degree}, stopping extraction.")
                break
            
            for node in current_degree_nodes:
                self.log_status(f"\nProcessing: {node.title} ({node.node_type})")
                
                # Extract related nodes
                related_nodes = self.extract_related_nodes(node.url, degree)
                
                # Add new nodes to the list and save to database
                for related_node in related_nodes:
                    if related_node.degree <= self.max_degree:
                        self.extracted_nodes.append(related_node)
                        self.save_node_to_db(related_node)
                
                # Add delay to be respectful to Wikipedia servers
                time.sleep(1)
            
            # Update session status with current progress
            self.db_manager.update_session_status(
                self.session_id, 'running', len(self.extracted_nodes)
            )
            
            self.log_status(f"Completed Degree {degree}. Total nodes so far: {len(self.extracted_nodes)}")
        
        # Mark session as completed
        self.db_manager.update_session_status(
            self.session_id, 'completed', len(self.extracted_nodes)
        )
        
        self.log_status("\n" + "=" * 50)
        self.log_status("EXTRACTION COMPLETED")
        self.log_status(f"Total nodes extracted: {len(self.extracted_nodes)}")
        self.log_status(f"Session ID: {self.session_id}")
        
        return self.extracted_nodes
    
    def print_summary(self):
        """Print a summary of the extraction results"""
        if not self.session_id:
            self.log_status("No active session to summarize")
            return
        
        summary = self.db_manager.get_session_summary(self.session_id)
        if not summary:
            self.log_status("Could not retrieve session summary")
            return
        
        self.log_status("\n" + "=" * 50)
        self.log_status("EXTRACTION SUMMARY")
        self.log_status("=" * 50)
        
        session_info = summary['session']
        self.log_status(f"Session ID: {session_info[0]}")
        self.log_status(f"Session Name: {session_info[1]}")
        self.log_status(f"Status: {session_info[5]}")
        self.log_status(f"Total Nodes: {session_info[4]}")
        
        degree_counts = summary['degree_counts']
        for degree in sorted(degree_counts.keys()):
            events = degree_counts[degree].get('Event', 0)
            people = degree_counts[degree].get('Person', 0)
            
            self.log_status(f"\nDegree {degree}:")
            self.log_status(f"  Events: {events}")
            self.log_status(f"  People: {people}")

def main():
    """Main function to run the Wikipedia extraction with database storage"""
    # Seed URL for Korean War
    seed_url = "https://en.wikipedia.org/wiki/Korean_War"
    
    # Initialize extractor
    extractor = WikipediaExtractorDB()
    
    try:
        # Run extraction
        extracted_nodes = extractor.extract_data(seed_url)
        
        # Print summary
        extractor.print_summary()
        
        print("\nExtraction completed successfully!")
        print(f"Data saved to database. Session ID: {extractor.session_id}")
        
    except KeyboardInterrupt:
        print("\nExtraction interrupted by user.")
        if extractor.session_id:
            extractor.db_manager.update_session_status(extractor.session_id, 'interrupted')
    except Exception as e:
        print(f"\nError during extraction: {str(e)}")
        if extractor.session_id:
            extractor.db_manager.update_session_status(extractor.session_id, 'error')

if __name__ == "__main__":
    main() 