# Project Structure

```
01. New Version/
├── frontend/                          # Frontend application (React/Vue/Angular)
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── backend/                           # Backend application
│   ├── api/                          # API endpoints
│   │   ├── __init__.py
│   │   ├── routes.py                 # API routes
│   │   ├── controllers.py            # Request handlers
│   │   └── middleware.py             # Custom middleware
│   │
│   ├── database/                     # Database layer
│   │   ├── __init__.py
│   │   ├── database.py               # Database manager (SQLite)
│   │   ├── models.py                 # Data models
│   │   └── migrations/               # Database migrations
│   │
│   ├── models/                       # Business logic models
│   │   ├── __init__.py
│   │   ├── extractor.py              # Wikipedia extractor
│   │   └── data_processor.py         # Data processing logic
│   │
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py                 # Logging utilities
│   │   └── helpers.py                # Helper functions
│   │
│   ├── config/                       # Configuration files
│   │   ├── __init__.py
│   │   ├── settings.py               # Application settings
│   │   └── database_config.py        # Database configuration
│   │
│   ├── tests/                        # Test files
│   │   ├── __init__.py
│   │   ├── test_extractor.py
│   │   └── test_database.py
│   │
│   ├── wikipedia_extractor_db.py     # Main extraction script with DB
│   ├── database_query.py             # Database query utility
│   ├── requirements.txt              # Python dependencies
│   └── README.md                     # Backend documentation
│
├── database/                         # Database files
│   ├── wikipedia_extraction.db       # SQLite database
│   └── migrations/                   # Database migration files
│
├── wikipedia_extractor.py            # Original extraction script (JSON output)
├── debug_infobox.py                 # Debug script for infobox extraction
├── extraction_results.json           # Sample JSON output
├── requirements.txt                  # Main project dependencies
├── README.md                         # Main project documentation
└── PROJECT_STRUCTURE.md              # This file
```

## Backend Structure Details

### `/backend/api/`
- **routes.py**: Define API endpoints (GET, POST, PUT, DELETE)
- **controllers.py**: Handle business logic for API requests
- **middleware.py**: Custom middleware (authentication, logging, etc.)

### `/backend/database/`
- **database.py**: SQLite database manager with CRUD operations
- **models.py**: Data models and schemas
- **migrations/**: Database schema changes and versioning

### `/backend/models/`
- **extractor.py**: Wikipedia extraction logic
- **data_processor.py**: Data processing and analysis

### `/backend/utils/`
- **logger.py**: Logging configuration and utilities
- **helpers.py**: Common utility functions

### `/backend/config/`
- **settings.py**: Application configuration (environment variables, etc.)
- **database_config.py**: Database connection settings

## Database Schema

### Tables:
1. **nodes**: Stores extracted Wikipedia nodes (events/people)
2. **extraction_sessions**: Tracks extraction sessions
3. **session_nodes**: Links sessions with nodes (many-to-many)

### Key Features:
- Session-based extraction tracking
- Degree-based data organization
- Parent-child relationship tracking
- Timestamp tracking for all operations

## Usage Examples

### Run Extraction with Database Storage:
```bash
cd backend
python wikipedia_extractor_db.py
```

### Query Database:
```bash
cd backend
python database_query.py list                    # List all sessions
python database_query.py details 1              # Show session details
python database_query.py nodes 1                # Show all nodes
python database_query.py nodes 1 2              # Show degree 2 nodes
python database_query.py export 1               # Export to JSON
```

### Frontend Integration:
The frontend can connect to the backend API to:
- Start new extractions
- View extraction progress
- Display extracted data
- Export results
- Manage sessions 