# Wikipedia Extraction Manager - Frontend

A modern React TypeScript frontend for the Wikipedia Extraction Manager, featuring interactive network visualization and real-time extraction management.

## 🚀 Features

- **Interactive Network Visualization**: D3.js-powered network graph showing events and people relationships
- **Real-time Extraction Management**: Start, monitor, and stop Wikipedia data extractions
- **Session Management**: View and manage all extraction sessions
- **Modern UI**: Built with React, TypeScript, Tailwind CSS, and Lucide React icons
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Technology Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **D3.js** for network visualization
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Axios** for API communication
- **React Router** for navigation

## 📦 Installation

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Build for Production**:
   ```bash
   npm run build
   ```

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Layout.tsx      # Main layout with navigation
│   │   ├── NetworkView.tsx # Interactive network visualization
│   │   ├── ExtractionManager.tsx # Extraction control panel
│   │   └── SessionList.tsx # Session management
│   ├── services/           # API services
│   │   └── api.ts         # API communication
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts       # Data types
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # React entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── package.json           # Dependencies and scripts
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

## 🎯 Key Features

### Network Visualization
- **Interactive Graph**: Click nodes to see details and expand network
- **Force-directed Layout**: Automatic positioning using D3.js force simulation
- **Node Types**: Different colors and sizes for Events (red) and People (green)
- **Tooltips**: Hover over nodes for quick information
- **Session Selection**: Choose which extraction session to visualize

### Extraction Manager
- **Configuration Panel**: Set output type, seed URL, and max degree
- **Real-time Progress**: Live progress bar and status updates
- **Log Streaming**: Real-time extraction logs
- **Start/Stop Controls**: Control extraction process

### Session Management
- **Session List**: View all extraction sessions in a table
- **Status Tracking**: See running, completed, and failed sessions
- **Statistics**: Summary stats across all sessions
- **Details View**: Click to see session details

## 🔧 API Integration

The frontend communicates with the backend API at `/api` endpoints:

- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details
- `GET /api/sessions/{id}/network` - Get network data for visualization
- `POST /api/extract` - Start new extraction
- `GET /api/extract/{id}/status` - Get extraction status

## 🎨 Customization

### Colors
The app uses a custom color scheme defined in `tailwind.config.js`:
- **Primary**: Blue shades for main UI elements
- **Events**: Red shades for event nodes
- **People**: Green shades for people nodes

### Styling
- Uses Tailwind CSS utility classes
- Custom component classes in `index.css`
- Responsive design with mobile-first approach

## 🚀 Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Development Tips
1. The development server runs on `http://localhost:3000`
2. API requests are proxied to `http://localhost:5000`
3. Hot module replacement is enabled for fast development
4. TypeScript strict mode is enabled for better type safety

## 📱 Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## 🔗 Backend Integration

This frontend is designed to work with the Wikipedia Extraction Manager backend. Make sure the backend API server is running on port 5000 before using the frontend.

## 📄 License

This project is part of the Wikipedia Extraction Manager tool. 