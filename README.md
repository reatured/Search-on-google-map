# 🔧 Hardware Store Finder

A modern web application that helps users find hardware stores near any location using Google Maps API. Built with a React frontend and FastAPI backend, deployed on GitHub Pages and Railway with PostgreSQL database integration.

## ✨ Features

### 🎯 **Smart Search**
- **Location-based search** - Find hardware stores near any address, city, or place
- **Real-time results** - Get instant results with store details
- **Comprehensive data** - Store names, addresses, phone numbers, and websites
- **Intelligent caching** - Results cached for 1 month to improve performance
- **Deduplication by name** - Option to hide repeated stores with the same name (e.g., only one "Home Depot" shown)

### 🏪 **Store Information**
- **Store names** and **addresses**
- **Phone numbers** for easy contact
- **Website links** for more information
- **Distance-based results** (within 10km radius)
- **Geographic coordinates** for mapping integration

### 🗺️ **Bulk Search (Streaming)**
- **Interactive map** - Drop a pin and select a radius (up to 20km)
- **Bulk grid search** - Backend streams results for a grid of points within the selected area
- **Live map pins** - See unique stores appear in real time as the search runs
- **Deduplication by name** - Hide repeated stores by name in bulk results
- **City name in history** - Bulk search and history use city names, not just coordinates

### 🎨 **Modern UI/UX**
- **Clean, responsive design** that works on all devices
- **Improved mobile tab visibility** - Unselected tabs are now darker for better readability
- **Loading states** with progress indicators
- **Error handling** with user-friendly messages
- **Beautiful animations** and smooth interactions

### ⚡ **Performance & Analytics**
- **Fast API responses** with optimized Google Places API calls
- **CORS-enabled** for seamless frontend-backend communication
- **Production-ready** deployment
- **Search analytics** - Track popular locations and search patterns
- **Performance monitoring** - Response time tracking and success rates

### 📊 **Data Storage & Analytics**
- **PostgreSQL database** for persistent data storage
- **Search history tracking** - Every search is logged with metadata
- **Store data persistence** - All store information saved to database
- **Analytics endpoints** - Popular searches, statistics, and recent activity
- **Smart caching** - Reduces API calls and improves response times

## 🚀 Live Demo

- **Frontend**: [https://reatured.github.io/Search-on-google-map](https://reatured.github.io/Search-on-google-map)
- **Backend API**: Deployed on Railway with automatic HTTPS
- **Database**: PostgreSQL hosted on Railway

## 🛠️ Tech Stack

### Frontend
- **React** - Modern UI framework
- **Leaflet** - Interactive maps
- **CSS3** - Styling and animations
- **GitHub Pages** - Static hosting

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Relational database
- **Google Maps API** - Geocoding and Places data
- **Railway** - Cloud deployment platform
- **Python 3.11** - Backend runtime

### APIs Used
- **Google Geocoding API** - Convert addresses to coordinates
- **Google Places API** - Find nearby hardware stores
- **Google Place Details API** - Get detailed store information

## 📁 Project Structure

```
Search-on-google-map/
├── frontend/                 # React frontend application
│   ├── index.html           # Main HTML file
│   ├── script.js            # React application logic
│   └── styles.css           # Styling and animations
├── backend/                  # FastAPI backend application
│   ├── main.py              # FastAPI server and API endpoints
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database connection and setup
│   ├── requirements.txt     # Python dependencies
│   ├── Procfile             # Railway deployment configuration
│   ├── runtime.txt          # Python version specification
│   └── alembic.ini          # Database migration configuration
└── README.md                # This file
```

## 🔧 API Endpoints

### Search Endpoints
- `GET /search` - Search for hardware stores near a location
- `GET /bulk_search` - Streaming bulk grid search (center, radius, spacing)

### Analytics Endpoints
- `GET /analytics/popular-searches` - Get most searched locations
- `GET /analytics/search-stats` - Get search statistics
- `GET /analytics/recent-searches` - Get recent search history
- `GET /analytics/cached-searches` - Get all cached searches

### Example Bulk Search Usage
```
GET /bulk_search?center=35.681236,139.767125&radius=20000&spacing=2000
```
- Streams results for a grid of points within a 20km radius of the center.

### Example Response (streamed)
```json
{
  "lat": 35.68,
  "lng": 139.76,
  "stores": [
    { "name": "Home Depot", "address": "...", ... }
  ],
  "city": "Tokyo"
}
```

## 🚀 Deployment

### Frontend (GitHub Pages)
- Automatically deployed from GitHub repository
- Static hosting with HTTPS
- Custom domain support

### Backend (Railway)
- Cloud deployment with automatic scaling
- Environment variable management
- HTTPS endpoint with CORS support
- Automatic deployments from GitHub
- PostgreSQL database integration

## 🔑 Environment Variables

### Backend (Railway)
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key
- `DATABASE_URL`: PostgreSQL connection string (automatically set by Railway)

## 🏃‍♂️ Local Development

### Frontend
1. Clone the repository
2. Open `frontend/index.html` in your browser
3. Or serve with a local server:
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Backend
1. Navigate to backend directory:
   ```bash
   cd backend
   ```
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env
   echo "DATABASE_URL=postgresql://localhost/hardware_finder" >> .env
   ```
5. Set up local PostgreSQL database (optional for development)
6. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## 🎯 What I Built

This project demonstrates:

1. **Full-stack development** - React frontend + FastAPI backend
2. **Database integration** - PostgreSQL with SQLAlchemy ORM
3. **API integration** - Google Maps APIs for real-world data
4. **Modern deployment** - GitHub Pages + Railway cloud hosting
5. **Production practices** - CORS, error handling, environment variables
6. **Data analytics** - Search tracking and performance monitoring
7. **User experience** - Responsive design, loading states, error messages
8. **Streaming bulk search** - Real-time results for large area queries

## 🔍 How It Works

1. **User enters a location** in the search box
2. **Frontend sends request** to the FastAPI backend
3. **Backend checks cache** for existing results
4. **If not cached, backend geocodes the location** using Google Geocoding API
5. **Backend searches for hardware stores** using Google Places API
6. **Backend gets detailed information** for each store
7. **Results are saved to database** for analytics and caching
8. **Results are returned** to the frontend
9. **Frontend displays the stores** in a clean, organized list
10. **Bulk search** streams results for a grid of points, deduplicates by name, and shows pins on the map

## 🎉 Future Enhancements

- [ ] Add store ratings and reviews
- [ ] Implement store filtering (by rating, distance, etc.)
- [ ] Add store photos and maps
- [ ] Implement user accounts and favorites
- [ ] Add store hours and availability
- [ ] Mobile app version
