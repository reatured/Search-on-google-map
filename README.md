# Find Hardware Store Web App

A full-stack web application to search for hardware stores by location using Google Places API. The backend is built with FastAPI (Python), and the frontend is a React app. Batch data collection scripts are also included for advanced use.

---

## 🚀 Deployment

### Frontend (React) on GitHub Pages
1. In `frontend/package.json`, set:
   ```json
   "homepage": "https://<your-github-username>.github.io/<repo-name>"
   ```
2. Install gh-pages:
   ```bash
   cd frontend
   npm install --save gh-pages
   ```
3. Add to `frontend/package.json` scripts:
   ```json
   "predeploy": "npm run build",
   "deploy": "gh-pages -d build"
   ```
4. Deploy:
   ```bash
   npm run deploy
   ```
5. Your app will be live at `https://<your-github-username>.github.io/<repo-name>`

### Backend (FastAPI) on AWS EC2
1. Launch an Ubuntu EC2 instance (t2.micro, open ports 22 & 8000).
2. SSH in:
   ```bash
   ssh -i /path/to/key.pem ubuntu@<ec2-public-dns>
   ```
3. Install Python and git:
   ```bash
   sudo apt update && sudo apt install python3-pip python3-venv git
   ```
4. Clone your repo and set up backend:
   ```bash
   git clone https://github.com/<your-github-username>/<repo-name>.git
   cd <repo-name>/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn python-dotenv requests
   echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
5. Your API will be at `http://<ec2-public-dns>:8000`

### Connect Frontend to Backend
- In your React code, change the API URL to your EC2 backend URL.
- In FastAPI, set CORS to allow your GitHub Pages domain.

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
