# Backend - Wikipedia Data Extraction

This is the backend component of the Wikipedia Data Extraction project. It handles data extraction from Wikipedia and stores results in a SQLite database.

## Features

- **Database Storage**: SQLite database with session tracking
- **Real-time Extraction**: Live status updates during extraction
- **Session Management**: Track multiple extraction sessions
- **Data Querying**: Query and export extracted data
- **API Ready**: Structured for REST API integration

## Project Structure

```
backend/
├── api/                    # API endpoints (future)
├── database/              # Database layer
│   └── database.py        # SQLite database manager
├── models/                # Business logic models
├── utils/                 # Utility functions
├── config/                # Configuration files
├── tests/                 # Test files
├── wikipedia_extractor_db.py  # Main extraction script
├── database_query.py      # Database query utility
└── requirements.txt       # Python dependencies
```

## Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Database Setup**:
The database will be automatically created when you run the extraction script for the first time.

## Usage

### 1. Run Wikipedia Extraction

```bash
python wikipedia_extractor_db.py
```

This will:
- Start extraction from Korean War Wikipedia page
- Save all extracted data to SQLite database
- Display real-time progress in terminal
- Create a new extraction session

### 2. Query Database

List all extraction sessions:
```bash
python database_query.py list
```

View session details:
```bash
python database_query.py details <session_id>
```

View all nodes in a session:
```bash
python database_query.py nodes <session_id>
```

View nodes by degree:
```bash
python database_query.py nodes <session_id> <degree>
```

Export session to JSON:
```bash
python database_query.py export <session_id> [filename]
```

## Database Schema

### Tables

1. **nodes**: Stores extracted Wikipedia nodes
   - `id`: Primary key
   - `title`: Node title
   - `url`: Wikipedia URL
   - `node_type`: 'Event' or 'Person'
   - `degree`: Extraction depth (0-3)
   - `parent_url`: Parent node URL
   - `created_at`: Creation timestamp
   - `updated_at`: Last update timestamp

2. **extraction_sessions**: Tracks extraction sessions
   - `id`: Primary key
   - `session_name`: Session name
   - `seed_url`: Starting Wikipedia URL
   - `max_degree`: Maximum extraction depth
   - `total_nodes`: Total nodes extracted
   - `status`: 'running', 'completed', 'error', 'interrupted'
   - `started_at`: Session start time
   - `completed_at`: Session completion time

3. **session_nodes**: Links sessions with nodes (many-to-many)
   - `session_id`: Foreign key to extraction_sessions
   - `node_id`: Foreign key to nodes

## API Integration (Future)

The backend is structured to easily add REST API endpoints:

- `GET /api/sessions` - List all sessions
- `GET /api/sessions/<id>` - Get session details
- `POST /api/extract` - Start new extraction
- `GET /api/sessions/<id>/nodes` - Get session nodes
- `GET /api/sessions/<id>/export` - Export session data

## Configuration

Database path can be configured in `database/database.py`:
```python
db_path = "database/wikipedia_extraction.db"
```

## Error Handling

- Network timeouts are handled gracefully
- Database errors are logged
- Extraction can be interrupted with Ctrl+C
- Session status is updated on interruption

## Performance

- Respectful scraping with 1-second delays
- Efficient database operations with proper indexing
- Memory-efficient processing for large extractions
- Session-based data organization

## Troubleshooting

### Common Issues

1. **Database not found**: Run extraction script once to create database
2. **Network errors**: Check internet connection and Wikipedia availability
3. **Memory issues**: Large extractions may require more RAM

### Debug Mode

Use the debug script to examine Wikipedia page structure:
```bash
python debug_infobox.py
```

## Development

### Adding New Features

1. **New Extraction Rules**: Modify `extract_infobox_data()` method
2. **Database Schema**: Add migrations in `database/migrations/`
3. **API Endpoints**: Create new routes in `api/routes.py`

### Testing

Run tests (when implemented):
```bash
python -m pytest tests/
```

## License

This project is part of the Wikipedia Data Extraction system. 