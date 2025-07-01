# 🔧 Hardware Store Finder

A modern web application that helps users find hardware stores near any location using Google Maps API. Built with a React frontend and FastAPI backend, deployed on GitHub Pages and Railway.

## ✨ Features

### 🎯 **Smart Search**
- **Location-based search** - Find hardware stores near any address, city, or place
- **Real-time results** - Get instant results with store details
- **Comprehensive data** - Store names, addresses, phone numbers, and websites

### 🏪 **Store Information**
- **Store names** and **addresses**
- **Phone numbers** for easy contact
- **Website links** for more information
- **Distance-based results** (within 10km radius)

### 🎨 **Modern UI/UX**
- **Clean, responsive design** that works on all devices
- **Loading states** with progress indicators
- **Error handling** with user-friendly messages
- **Beautiful animations** and smooth interactions

### ⚡ **Performance**
- **Fast API responses** with optimized Google Places API calls
- **CORS-enabled** for seamless frontend-backend communication
- **Production-ready** deployment

## 🚀 Live Demo

- **Frontend**: [https://reatured.github.io/Search-on-google-map](https://reatured.github.io/Search-on-google-map)
- **Backend API**: Deployed on Railway with automatic HTTPS

## 🛠️ Tech Stack

### Frontend
- **React** - Modern UI framework
- **CSS3** - Styling and animations
- **GitHub Pages** - Static hosting

### Backend
- **FastAPI** - High-performance Python web framework
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
│   ├── requirements.txt     # Python dependencies
│   ├── Procfile             # Railway deployment configuration
│   └── runtime.txt          # Python version specification
└── README.md                # This file
```

## 🔧 API Endpoints

### `GET /search`
Search for hardware stores near a location.

**Parameters:**
- `location` (string, required): Address, city, or place to search

**Response:**
```json
{
  "location": "Tokyo, Japan",
  "stores": [
    {
      "name": "Hardware Store Name",
      "address": "123 Main St, Tokyo, Japan",
      "website": "https://example.com",
      "phone": "+81-3-1234-5678",
      "email": null
    }
  ]
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

## 🔑 Environment Variables

### Backend (Railway)
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key

## 🏃‍♂️ Local Development

### Frontend
1. Clone the repository
2. Open `frontend/index.html` in your browser
3. Or serve with a local server:
   ```bash
   cd frontend
   python -m http.server 8000
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
   ```

5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## 🎯 What I Built

This project demonstrates:

1. **Full-stack development** - React frontend + FastAPI backend
2. **API integration** - Google Maps APIs for real-world data
3. **Modern deployment** - GitHub Pages + Railway cloud hosting
4. **Production practices** - CORS, error handling, environment variables
5. **User experience** - Responsive design, loading states, error messages

## 🔍 How It Works

1. **User enters a location** in the search box
2. **Frontend sends request** to the FastAPI backend
3. **Backend geocodes the location** using Google Geocoding API
4. **Backend searches for hardware stores** using Google Places API
5. **Backend gets detailed information** for each store
6. **Results are returned** to the frontend
7. **Frontend displays the stores** in a clean, organized list

## 🎉 Future Enhancements

- [ ] Add store ratings and reviews
- [ ] Implement store filtering (by rating, distance, etc.)
- [ ] Add store photos and maps
- [ ] Implement user accounts and favorites
- [ ] Add store hours and availability
- [ ] Mobile app version

---

**Built with ❤️ using modern web technologies and deployed for the world to use!**
