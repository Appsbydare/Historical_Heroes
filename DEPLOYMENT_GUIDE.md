# Vercel Deployment Guide for Wikipedia Extraction Prototype

This guide will help you deploy your Wikipedia extraction prototype to Vercel.

## 🎯 What This Prototype Does

- **Frontend**: React + TypeScript application with network visualization
- **Backend**: Simple Python API that reads from your existing `Nodes.csv` file
- **Data Source**: Uses your pre-extracted Korean War data from Wikipedia
- **No Database**: Everything runs from the CSV file for simplicity

## 📁 Project Structure

```
├── frontend/           # React application
├── api/               # Vercel serverless functions
│   ├── csv_reader.py  # Main API that reads CSV
│   └── requirements.txt
├── Nodes.csv          # Your extracted data
├── vercel.json        # Vercel configuration
└── .gitignore         # Git ignore rules
```

## 🚀 Deployment Steps

### 1. Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Vercel deployment"
   ```

2. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the configuration
5. Click "Deploy"

### 3. Configuration Details

The `vercel.json` file tells Vercel:
- Build the React frontend from `frontend/package.json`
- Serve Python API functions from `api/` directory
- Route `/api/*` requests to Python functions
- Route everything else to the React app

## 🔧 How It Works

### API Endpoints

- `GET /api/sessions` - Returns a single session representing your CSV data
- `GET /api/sessions/1` - Returns session details with degree counts
- `GET /api/sessions/1/nodes` - Returns all nodes from CSV
- `GET /api/sessions/1/network` - Returns network data for visualization
- `POST /api/extract` - Simulates extraction (returns success)
- `GET /api/extract/1/status` - Returns completed status

### Data Flow

1. **CSV Reading**: The Python API reads `Nodes.csv` using pandas
2. **Data Transformation**: Converts CSV data to match frontend expectations
3. **Network Visualization**: Frontend displays nodes as an interactive graph
4. **Session Management**: Shows your data as a completed extraction session

## 📊 Your Data

The prototype will display:
- **326 nodes** from your Korean War extraction
- **Events** (red nodes) and **People** (green nodes)
- **Interactive network visualization** using D3.js
- **Session statistics** and degree counts

## 🎨 Frontend Features

- **Network View**: Interactive graph visualization
- **Session List**: Shows your CSV data as a session
- **Extraction Manager**: Simulated extraction interface
- **Responsive Design**: Works on desktop and mobile

## 🔄 Future Development

When you're ready for the full application:

1. **Replace CSV with Database**: Use PostgreSQL or MongoDB
2. **Add Real Extraction**: Implement the full Wikipedia extraction logic
3. **Separate Services**: Deploy backend to Railway/Render/Heroku
4. **Add Authentication**: User management and session tracking
5. **Enhanced Features**: Real-time extraction, progress tracking, etc.

## 🐛 Troubleshooting

### Common Issues

1. **Build Fails**: Check that `frontend/package.json` exists and has correct scripts
2. **API Errors**: Verify `Nodes.csv` is in the root directory
3. **CORS Issues**: The API includes CORS headers for frontend communication
4. **Python Dependencies**: Make sure `api/requirements.txt` includes pandas

### Debug Commands

```bash
# Test locally
cd frontend && npm run dev
cd api && python csv_reader.py

# Check Vercel logs
vercel logs
```

## 📝 Notes

- **Prototype Only**: This is designed for demonstration purposes
- **No Real Extraction**: The extraction feature is simulated
- **Static Data**: Uses your existing CSV file
- **Free Tier**: Vercel's free tier should be sufficient for this prototype

## 🎉 Success!

Once deployed, you'll have:
- A live URL (e.g., `https://your-app.vercel.app`)
- Interactive network visualization of your Korean War data
- Professional-looking prototype for demos and presentations
- Foundation for future development

Your prototype will showcase the network visualization capabilities while using your existing extracted data! 