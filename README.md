# Hardware Store Finder

A modern web application that helps users find hardware stores near any location using Google Maps API. Built with a React frontend and FastAPI backend, deployed on GitHub Pages and Railway with PostgreSQL database integration.

## Features

### Smart Search
- **Location-based search** - Find hardware stores near any address, city, or place
- **Real-time results** - Get instant results with store details
- **Comprehensive data** - Store names, addresses, phone numbers, and websites
- **Intelligent caching** - Results cached for 1 month to improve performance
- **Deduplication by name** - Option to hide repeated stores with the same name (e.g., only one "Home Depot" shown)

### Store Information
- **Store names** and **addresses**
- **Phone numbers** for easy contact
- **Website links** for more information
- **Distance-based results** (within 10km radius)
- **Geographic coordinates** for mapping integration

### Bulk Search (Streaming)
- **Interactive map** - Drop a pin and select a radius (up to 20km)
- **Bulk grid search** - Backend streams results for a grid of points within the selected area
- **Live map pins** - See unique stores appear in real time as the search runs
- **Deduplication by name** - Hide repeated stores by name in bulk results
- **City name in history** - Bulk search and history use city names, not just coordinates

### Modern UI/UX
- **Tailwind UI Design System** - Professional, modern interface with consistent styling
- **Clean, responsive design** that works on all devices
- **Improved mobile tab visibility** - Unselected tabs are now darker for better readability
- **Enhanced Modal Experience** - Independent scrolling sections for analysis and email
- **Consistent Button Design** - Uniform language buttons with proper dimensions
- **Real-time Visual Feedback** - Loading states with grayed-out sections during AI processing
- **Global API Toggle** - Centralized API endpoint selection in top-right corner
- **Two-line Headers** - Clean typography with proper hierarchy
- **Loading states** with progress indicators
- **Error handling** with user-friendly messages
- **Beautiful animations** and smooth interactions

### Performance & Analytics
- **Fast API responses** with optimized Google Places API calls
- **CORS-enabled** for seamless frontend-backend communication
- **Production-ready** deployment
- **Search analytics** - Track popular locations and search patterns
- **Performance monitoring** - Response time tracking and success rates
- **Streaming search results** - Real-time results appear as stores are found (2-3 seconds vs 10+ seconds)

### AI-Powered Features
- **Company Analysis** - AI-powered analysis of hardware stores using Perplexity API
- **Multi-language Support** - Analysis available in English and Chinese (中文)
- **Smart Email Generation** - Personalized cold emails based on company analysis
- **Email Language Selection** - Generate emails in English or Chinese independently
- **Regenerate Email** - Refresh AI-generated content with new variations
- **Real-time Loading States** - Visual feedback during AI processing
- **Global API Management** - Centralized API endpoint selection (Production/Local)
- **Intelligent Fallbacks** - Works with static templates when AI endpoints are unavailable
- **Dynamic Content** - Analysis and emails adapt to each specific store

### Data Storage & Analytics
- **PostgreSQL database** for persistent data storage
- **Search history tracking** - Every search is logged with metadata
- **Store data persistence** - All store information saved to database
- **Analytics endpoints** - Popular searches, statistics, and recent activity
- **Smart caching** - Reduces API calls and improves response times

## Live Demo

- **Frontend**: [https://reatured.github.io/Search-on-google-map](https://reatured.github.io/Search-on-google-map)
- **Backend API**: Deployed on Railway with automatic HTTPS
- **Database**: PostgreSQL hosted on Railway

## Recent Updates (Latest)

### UI/UX Enhancements
- **Tailwind UI Design System** - Complete design overhaul for professional appearance
- **Enhanced Modal Interface** - Independent scrolling for analysis and email sections
- **Global API Management** - Centralized API endpoint selection with persistent settings
- **Improved Typography** - Two-line headers with proper visual hierarchy
- **Consistent Button Design** - Uniform language toggles with standardized dimensions

### AI Features Improvements
- **Multi-language Support** - Analysis and email generation in English and Chinese
- **Email Regeneration** - Ability to regenerate AI content with different variations
- **Real-time Loading States** - Visual feedback with grayed-out sections during processing
- **Language Independence** - Separate language selection for analysis and emails

### Technical Improvements
- **Context API Integration** - Global state management for API endpoints
- **Enhanced Scrolling** - Vertical-only scrolling with proper content boundaries
- **Form Validation** - Improved input handling with disabled states during loading
- **Performance Optimization** - Better memory management and state handling

## Tech Stack

### Frontend
- **React** - Modern UI framework with TypeScript
- **Context API** - Global state management for API endpoints
- **Tailwind UI** - Professional design system for consistent styling
- **CSS3** - Advanced styling with CSS custom properties
- **Leaflet** - Interactive maps
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
- **Perplexity API** - AI-powered company analysis and email generation

## Project Structure

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

## API Endpoints

### Search Endpoints
- `GET /search` - Search for hardware stores near a location
- `GET /search/stream` - Streaming search with real-time results
- `GET /bulk_search` - Streaming bulk grid search (center, radius, spacing)

### AI-Powered Endpoints
- `POST /api/analyze-company` - Generate AI analysis of a hardware store
- `POST /api/generate-email` - Generate personalized cold emails based on analysis

### Analytics Endpoints
- `GET /analytics/popular-searches` - Get most searched locations
- `GET /analytics/search-stats` - Get search statistics
- `GET /analytics/recent-searches` - Get recent search history
- `GET /analytics/cached-searches` - Get all cached searches

### Example AI Analysis Usage
```
POST /api/analyze-company
Content-Type: application/json

{
  "name": "Home Depot",
  "address": "123 Main St, New York, NY",
  "phone": "(555) 123-4567",
  "website": "https://homedepot.com"
}
```

### Example Analysis Response
```json
{
  "basicInfo": {
    "name": "Home Depot",
    "address": "123 Main St, New York, NY",
    "phone": "(555) 123-4567",
    "website": "https://homedepot.com"
  },
  "analysisPoints": [
    "Large retail chain with established market presence",
    "Strong brand recognition and customer base",
    "Multiple product categories suitable for partnerships"
  ],
  "nextSteps": [
    "Contact regional procurement team",
    "Prepare product samples and catalog",
    "Schedule partnership meeting"
  ],
  "perplexityAnalysis": "AI-generated detailed analysis..."
}
```

### Example Email Generation Usage
```
POST /api/generate-email
Content-Type: application/json

{
  "store": {
    "name": "Home Depot",
    "address": "123 Main St, New York, NY",
    "phone": "(555) 123-4567",
    "website": "https://homedepot.com"
  },
  "analysis": { /* analysis data from company analysis */ }
}
```

### Example Email Response
```json
{
  "subject": "Partnership Opportunity - Quality Hardware Solutions for Home Depot",
  "body": "Dear Home Depot Team,\n\nI hope this email finds you well..."
}
```

## Deployment

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

## Environment Variables

### Backend (Railway)
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key
- `DATABASE_URL`: PostgreSQL connection string (automatically set by Railway)

## Local Development

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

## What I Built

This project demonstrates:

1. **Full-stack development** - React frontend + FastAPI backend
2. **Database integration** - PostgreSQL with SQLAlchemy ORM
3. **API integration** - Google Maps APIs for real-world data
4. **Modern deployment** - GitHub Pages + Railway cloud hosting
5. **Production practices** - CORS, error handling, environment variables
6. **Data analytics** - Search tracking and performance monitoring
7. **User experience** - Responsive design, loading states, error messages
8. **Streaming bulk search** - Real-time results for large area queries

## How It Works

### Store Search Flow
1. **User enters a location** in the search box
2. **Frontend sends streaming request** to the FastAPI backend
3. **Backend checks cache** for existing results
4. **If not cached, backend geocodes the location** using Google Geocoding API
5. **Backend searches for hardware stores** using Google Places API
6. **Results stream back in real-time** as each store is processed
7. **Frontend displays stores immediately** as they are received
8. **Results are saved to database** for analytics and caching

### AI Analysis & Email Flow
1. **User clicks "Analyze Company"** for any store
2. **Frontend calls company analysis API** with store details
3. **Backend uses Perplexity API** to generate intelligent analysis
4. **AI analysis is displayed** in the modal with insights and next steps
5. **User clicks "Generate Cold Email"** within the analysis modal
6. **Backend uses store + analysis data** to generate personalized email
7. **AI-generated email appears** in the email composition section
8. **User can edit and send** the personalized email

### Fallback System
- **When AI endpoints are unavailable**, system uses static templates
- **Seamless user experience** with no interruption to functionality
- **Graceful degradation** ensures app works in all scenarios

## Future Enhancements

- [ ] Add store ratings and reviews
- [ ] Implement store filtering (by rating, distance, etc.)
- [ ] Add store photos and maps
- [ ] Implement user accounts and favorites
- [ ] Add store hours and availability
- [ ] Mobile app version
