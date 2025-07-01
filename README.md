# Find Hardware Store Web App

A full-stack web application to search for hardware stores by location using Google Places API. The backend is built with FastAPI (Python), and the frontend is a React app. Batch data collection scripts are also included for advanced use.

---

## 🚀 Quick Start

### Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-dotenv requests
# Add your Google Maps API key to .env
echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env
uvicorn main:app --reload
# API: http://localhost:8000 | Docs: http://localhost:8000/docs
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
# App: http://localhost:3000
```

### Usage
- Enter a location and search for hardware stores.
- Results show name, address, phone, and website.

---

## 📁 Project Structure
```
Find Hardware Store/
├── backend/    # FastAPI backend
├── frontend/   # React frontend
├── src/        # Python scripts for batch data collection
├── output/     # Data output from scripts
└── README.md   # This file
```

---

## 📦 Scripts (Optional)
- Batch scripts for searching hardware stores in various regions (see `src/`).
- Output saved in `output/` as CSV/JSON.
- Requires Google Maps API key in `.env`.

---

For more details, see code comments or the interactive API docs at `/docs` when the backend is running.
