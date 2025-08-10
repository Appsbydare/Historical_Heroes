# 📖 Wikipedia Extraction Manager

A modern desktop application for extracting structured data (events, people, metadata) from Wikipedia, starting from a user-defined event page. Features an interactive network visualization and real-time extraction management.

## 🚀 Features

### Core Functionality
- **Wikipedia Data Extraction**: Extract events and people from Wikipedia pages
- **Network Visualization**: Interactive D3.js-powered network graph
- **Session Management**: Track and manage multiple extraction sessions
- **Real-time Progress**: Monitor extraction progress with live updates
- **Database Storage**: SQLite database with session tracking
- **CSV Export**: Export data to CSV files

### Modern Frontend
- **React 18** with TypeScript for type safety
- **D3.js** for interactive network visualization
- **Tailwind CSS** for modern, responsive design
- **Real-time API** communication with backend
- **Mobile-responsive** design

## 🛠️ Technology Stack

### Backend
- **Python 3.8+** with Flask API
- **SQLite** database with session management
- **Wikipedia API** integration
- **BeautifulSoup** for HTML parsing

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **D3.js** for network visualization
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Axios** for API communication

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd wikipedia-extraction-manager
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Start the application**:
   ```bash
   python start_app.py
   ```

5. **Open your browser**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## 🎯 How It Works

### Data Extraction Process

1. **Seed Event** 🌱
   - Start with a Wikipedia event page (e.g., Korean War)
   - Extract basic event information and metadata

2. **Traversal Logic** 🔗
   - **Degree 0**: Seed event
   - **Degree 1**: People from the event (commanders, leaders)
   - **Degree 2**: Events from those people (battles, wars)
   - **Degree 3**: People from those events, etc.

3. **Data Collection** 📦
   - **node_id**: Unique identifier (e1, p1, etc.)
   - **node_type**: "Event" or "Person"
   - **name**: Name of the event or person
   - **description**: Description from infobox
   - **start_date/end_date**: Extracted dates
   - **metadata**: Additional structured data

### Network Visualization

- **Interactive Graph**: Click nodes to see details
- **Force-directed Layout**: Automatic positioning
- **Node Types**: Different colors for Events (red) and People (green)
- **Drill-down**: Expand network by clicking nodes
- **Session Selection**: Choose which extraction to visualize

## 🏗️ Project Structure

```
wikipedia-extraction-manager/
├── backend/                 # Python backend
│   ├── api/                # Flask API server
│   ├── database/           # Database management
│   ├── models/             # Data models
│   ├── utils/              # Utility functions
│   └── extraction_manager.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   └── ...
│   ├── package.json
│   └── ...
├── data/                   # Generated data
│   ├── Nodes.csv
│   └── wikipedia_extraction.db
├── start_app.py           # Startup script
└── README.md
```

## 🎮 Usage

### Starting a New Extraction

1. **Navigate to Extraction Manager**
   - Click "Extraction Manager" in the navigation

2. **Configure Settings**
   - **Output Type**: Choose SQL Database or CSV File
   - **Seed URL**: Enter Wikipedia event page URL
   - **Max Degree**: Set traversal depth (1-10)

3. **Start Extraction**
   - Click "Start Extraction"
   - Monitor progress in real-time
   - View logs for detailed information

### Viewing Network Visualization

1. **Navigate to Network View**
   - Click "Network View" in the navigation

2. **Select Session**
   - Choose from available extraction sessions
   - View network statistics

3. **Interact with Network**
   - Hover over nodes for tooltips
   - Click nodes for detailed information
   - Use "Expand Network" to drill down

### Managing Sessions

1. **Navigate to Sessions**
   - Click "Sessions" in the navigation

2. **View Session List**
   - See all extraction sessions
   - Check status and progress
   - View session statistics

## 🔧 Development

### Backend Development

```bash
cd backend
python api/app.py
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/dist/
```

## 📊 Data Output

### Database Schema

- **nodes**: Individual events and people
- **extraction_sessions**: Session metadata
- **session_nodes**: Links sessions to nodes

### CSV Format

```csv
node_id,node_type,name,description,start_date,end_date,metadata
e1,Event,Korean War,Part of the Cold War...,25 June 1950,27 July 1953,{...}
p1,Person,Syngman Rhee,이승만,...,1875-03-26,1965-07-19,{...}
```

## 🎨 Customization

### Frontend Styling
- Edit `frontend/tailwind.config.js` for color schemes
- Modify `frontend/src/index.css` for custom styles
- Update component styles in individual files

### Backend Configuration
- Modify `backend/config/` for database settings
- Update extraction logic in `backend/extraction_manager.py`
- Customize API endpoints in `backend/api/app.py`

## 🐛 Troubleshooting

### Common Issues

1. **Frontend won't start**
   - Check Node.js version (16+ required)
   - Run `npm install` in frontend directory
   - Check for port conflicts (3000)

2. **Backend API errors**
   - Ensure Python 3.8+ is installed
   - Install dependencies: `pip install -r requirements.txt`
   - Check database permissions

3. **Network visualization issues**
   - Check browser console for errors
   - Ensure D3.js is properly loaded
   - Verify API endpoints are accessible

### Debug Mode

```bash
# Backend debug
cd backend
FLASK_DEBUG=1 python api/app.py

# Frontend debug
cd frontend
npm run dev
```

## 📈 Performance

### Optimization Tips

- **Extraction**: Use lower max_degree for faster results
- **Visualization**: Limit nodes for better performance
- **Database**: Regular cleanup of old sessions
- **Frontend**: Use production build for better performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Wikipedia for providing the data source
- D3.js for network visualization
- React team for the frontend framework
- Flask team for the backend framework

---

**🌟 Happy extracting!** # Updated for deployment
