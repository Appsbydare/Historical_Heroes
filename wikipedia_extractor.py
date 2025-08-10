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

@dataclass
class ExtractedNode:
    """Represents a node (Event or Person) extracted from Wikipedia"""
    title: str
    url: str
    node_type: str  # 'Event' or 'Person'
    degree: int
    parent_url: Optional[str] = None
    description: Optional[str] = ''
    start_date: Optional[str] = ''
    end_date: Optional[str] = ''
    metadata: dict = field(default_factory=dict)

class WikipediaExtractor:
    def __init__(self, base_url: str = "https://en.wikipedia.org"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.extracted_nodes: List[ExtractedNode] = []
        self.visited_urls: Set[str] = set()
        self.max_degree = 3

    def log_status(self, message: str, log_callback=None):
        """Print status message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg)
        sys.stdout.flush()
        if log_callback:
            log_callback(msg)

    def get_wikipedia_page(self, url: str, log_callback=None) -> Optional[BeautifulSoup]:
        """Fetch and parse a Wikipedia page"""
        try:
            self.log_status(f"Fetching: {url}", log_callback)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            self.log_status(f"Error fetching {url}: {str(e)}", log_callback)
            return None

    def extract_infobox_data(self, soup: BeautifulSoup) -> Dict[str, any]:
        infobox_data = {}
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return infobox_data
        rows = infobox.find_all('tr')
        # Description: from caption or first summary row
        description = None
        if infobox.find('caption'):
            description = infobox.find('caption').get_text(strip=True)
        else:
            for row in rows:
                td = row.find('td')
                if td and not row.find('th'):
                    description = td.get_text(strip=True)
                    break
        infobox_data['description'] = description or ''
        # Dates and metadata
        metadata = {}
        for i, row in enumerate(rows):
            th = row.find('th')
            if th:
                header_text = th.get_text(strip=True)
                td = row.find('td')
                if not td:
                    continue
                # Dates
                if header_text.lower() in ['born', 'date', 'start date', 'started', 'begin', 'birth']:
                    infobox_data['start_date'] = td.get_text(strip=True)
                elif header_text.lower() in ['died', 'end date', 'ended', 'death']:
                    infobox_data['end_date'] = td.get_text(strip=True)
                elif header_text.lower() == 'date':
                    date_text = td.get_text(strip=True)
                    if '–' in date_text:
                        parts = date_text.split('–')
                        infobox_data['start_date'] = parts[0].strip()
                        infobox_data['end_date'] = parts[1].strip() if len(parts) > 1 else ''
                    else:
                        infobox_data['start_date'] = date_text
                # Metadata
                elif header_text not in ['Commanders and leaders', 'Battles/wars']:
                    metadata[header_text] = td.get_text(strip=True)
        infobox_data['metadata'] = metadata
        # --- Restore original logic for extracting links for traversal ---
        sections_to_find = ['Commanders and leaders', 'Battles/wars']
        for i, row in enumerate(rows):
            th = row.find('th')
            if th:
                header_text = th.get_text(strip=True)
                if header_text in sections_to_find:
                    td = row.find('td')
                    if not td and i + 1 < len(rows):
                        next_row = rows[i + 1]
                        td = next_row.find('td')
                    if td:
                        links = td.find_all('a')
                        values = []
                        for link in links:
                            href = link.get('href')
                            if href and href.startswith('/wiki/'):
                                title = link.get_text(strip=True)
                                if title:
                                    values.append(title)
                        if values:
                            infobox_data[header_text] = values
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

    def extract_related_nodes(self, url: str, degree: int, log_callback=None, stop_flag=None) -> List[ExtractedNode]:
        """Extract related nodes based on the current page type"""
        if stop_flag and stop_flag.is_set():
            return []
        soup = self.get_wikipedia_page(url, log_callback)
        if not soup:
            return []

        title = self.get_page_title(soup)
        infobox_data = self.extract_infobox_data(soup)

        # Determine page type
        is_event = self.is_event_page(soup)
        is_person = self.is_person_page(soup)

        nodes = []
        if is_event:
            self.log_status(f"Processing EVENT: {title} (Degree {degree})", log_callback)
            # Extract people from event
            if 'Commanders and leaders' in infobox_data:
                for person_name in infobox_data['Commanders and leaders']:
                    # Construct Wikipedia URL for the person
                    person_url = f"{self.base_url}/wiki/{person_name.replace(' ', '_')}"

                    if person_url not in self.visited_urls:
                        self.visited_urls.add(person_url)
                        # Fetch person page for extra fields
                        person_soup = self.get_wikipedia_page(person_url, log_callback)
                        person_infobox = self.extract_infobox_data(person_soup) if person_soup else {}
                        node = ExtractedNode(
                            title=person_name,
                            url=person_url,
                            node_type='Person',
                            degree=degree + 1,
                            parent_url=url,
                            description=person_infobox.get('description', ''),
                            start_date=person_infobox.get('start_date', ''),
                            end_date=person_infobox.get('end_date', ''),
                            metadata=person_infobox.get('metadata', {})
                        )
                        nodes.append(node)
                        self.log_status(f"  -> Found PERSON: {person_name}", log_callback)
        elif is_person:
            self.log_status(f"Processing PERSON: {title} (Degree {degree})", log_callback)
            # Extract events from person
            if 'Battles/wars' in infobox_data:
                for event_name in infobox_data['Battles/wars']:
                    # Construct Wikipedia URL for the event
                    event_url = f"{self.base_url}/wiki/{event_name.replace(' ', '_')}"

                    if event_url not in self.visited_urls:
                        self.visited_urls.add(event_url)
                        # Fetch event page for extra fields
                        event_soup = self.get_wikipedia_page(event_url, log_callback)
                        event_infobox = self.extract_infobox_data(event_soup) if event_soup else {}
                        node = ExtractedNode(
                            title=event_name,
                            url=event_url,
                            node_type='Event',
                            degree=degree + 1,
                            parent_url=url,
                            description=event_infobox.get('description', ''),
                            start_date=event_infobox.get('start_date', ''),
                            end_date=event_infobox.get('end_date', ''),
                            metadata=event_infobox.get('metadata', {})
                        )
                        nodes.append(node)
                        self.log_status(f"  -> Found EVENT: {event_name}", log_callback)
        return nodes

    def extract_data(self, seed_url: str, stop_flag=None, log_callback=None) -> List[ExtractedNode]:
        """Main extraction method with depth limiting"""
        self.log_status("Starting Wikipedia data extraction...", log_callback)
        self.log_status(f"Seed URL: {seed_url}", log_callback)
        self.log_status(f"Max depth: {self.max_degree} degrees", log_callback)
        self.log_status("-" * 50, log_callback)

        # Initialize with seed event
        seed_soup = self.get_wikipedia_page(seed_url, log_callback)
        seed_infobox = self.extract_infobox_data(seed_soup) if seed_soup else {}
        seed_node = ExtractedNode(
            title="Korean War",
            url=seed_url,
            node_type='Event',
            degree=0,
            description=seed_infobox.get('description', ''),
            start_date=seed_infobox.get('start_date', ''),
            end_date=seed_infobox.get('end_date', ''),
            metadata=seed_infobox.get('metadata', {})
        )
        self.extracted_nodes.append(seed_node)
        self.visited_urls.add(seed_url)

        # Process nodes by degree
        for degree in range(self.max_degree + 1):
            if stop_flag and stop_flag.is_set():
                self.log_status('Extraction stopped by user.', log_callback)
                break
            self.log_status(f"\n=== Processing Degree {degree} ===", log_callback)

            # Get all nodes at current degree
            current_degree_nodes = [node for node in self.extracted_nodes if node.degree == degree]

            if not current_degree_nodes:
                self.log_status(f"No nodes found at degree {degree}, stopping extraction.", log_callback)
                break

            for node in current_degree_nodes:
                if stop_flag and stop_flag.is_set():
                    self.log_status('Extraction stopped by user.', log_callback)
                    break
                self.log_status(f"\nProcessing: {node.title} ({node.node_type})", log_callback)

                # Extract related nodes
                related_nodes = self.extract_related_nodes(node.url, degree, log_callback, stop_flag)

                # Add new nodes to the list
                for related_node in related_nodes:
                    if related_node.degree <= self.max_degree:
                        self.extracted_nodes.append(related_node)

                # Add delay to be respectful to Wikipedia servers
                time.sleep(1)

            self.log_status(f"Completed Degree {degree}. Total nodes so far: {len(self.extracted_nodes)}", log_callback)

        self.log_status("\n" + "=" * 50, log_callback)
        self.log_status("EXTRACTION COMPLETED", log_callback)
        self.log_status(f"Total nodes extracted: {len(self.extracted_nodes)}", log_callback)

        return self.extracted_nodes

    def save_results(self, filename: str = "extraction_results.json"):
        """Save extraction results to JSON file"""
        results = []
        for node in self.extracted_nodes:
            results.append({
                'title': node.title,
                'url': node.url,
                'node_type': node.node_type,
                'degree': node.degree,
                'parent_url': node.parent_url,
                'description': node.description,
                'start_date': node.start_date,
                'end_date': node.end_date,
                'metadata': node.metadata
            })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.log_status(f"Results saved to: {filename}")

    def print_summary(self):
        """Print a summary of the extraction results"""
        self.log_status("\n" + "=" * 50)
        self.log_status("EXTRACTION SUMMARY")
        self.log_status("=" * 50)

        for degree in range(self.max_degree + 1):
            nodes_at_degree = [node for node in self.extracted_nodes if node.degree == degree]
            events = [node for node in nodes_at_degree if node.node_type == 'Event']
            people = [node for node in nodes_at_degree if node.node_type == 'Person']

            self.log_status(f"\nDegree {degree}:")
            self.log_status(f"  Events: {len(events)}")
            for event in events:
                self.log_status(f"    - {event.title}")

            self.log_status(f"  People: {len(people)}")
            for person in people:
                self.log_status(f"    - {person.title}")

def main():
    """Main function to run the Wikipedia extraction"""
    # Seed URL for Korean War
    seed_url = "https://en.wikipedia.org/wiki/Korean_War"

    # Initialize extractor
    extractor = WikipediaExtractor()

    try:
        # Run extraction
        extracted_nodes = extractor.extract_data(seed_url)

        # Print summary
        extractor.print_summary()

        # Save results
        extractor.save_results()

        print("\nExtraction completed successfully!")

    except KeyboardInterrupt:
        print("\nExtraction interrupted by user.")
    except Exception as e:
        print(f"\nError during extraction: {str(e)}")

if __name__ == "__main__":
    main() 