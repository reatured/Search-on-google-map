# Progress Report

**Project Progress:**

```
[■■■■■■■■■■■■■■■■□□□□□□] 60%
```

**Done:**
- [x] Archive old script in `src/`
- [x] Update README and DEV_PLAN for new architecture
- [x] Scaffold backend directory and virtual environment
- [x] Install FastAPI, Uvicorn, requests, python-dotenv in backend
- [x] Create FastAPI app with `/search` endpoint (Google Places integration)
- [x] Enable CORS for frontend integration
- [x] Test backend endpoint with real data

**To Do:**
- [ ] Add error handling and validation to backend
- [ ] Add API documentation/comments
- [ ] Scaffold React frontend in `frontend/`
- [ ] Build search UI in React
- [ ] Connect React frontend to FastAPI backend
- [ ] Add loading/error states to frontend
- [ ] Prepare for deployment (backend & frontend)
- [ ] Write deployment instructions
- [ ] (Optional) Add stretch goals: authentication, favorites, export, map view

---

# Development Plan: Find Hardware Store (Modern Web App)

## Overview
We are upgrading the project from a script-based tool to a full-stack web application with a FastAPI backend and a React frontend.

---

## 1. Archive Old Script
- Move legacy scripts to `src/` for reference and batch data collection.
- Update documentation to point users to the new web app.

---

## 2. Backend: FastAPI
- [ ] Scaffold FastAPI project in `backend/`
- [ ] Implement `/search` endpoint to query Google Places API for hardware stores
- [ ] Use environment variable for Google Maps API key
- [ ] Add CORS support for frontend integration
- [ ] Write tests for API endpoint
- [ ] Document API usage

### Example Endpoint
- `GET /search?location=Tokyo,Japan`
- Returns: List of hardware stores with name, address, website, phone, email (if available)

---

## 3. Frontend: React
- [ ] Scaffold React app in `frontend/`
- [ ] Build search UI for user to enter location
- [ ] Display results in a modern, responsive table or card layout
- [ ] Show store name, address, website, phone, email
- [ ] Add loading and error states
- [ ] Connect to FastAPI backend

---

## 4. Integration
- [ ] Connect React frontend to FastAPI backend (local/dev)
- [ ] Test end-to-end search flow
- [ ] Add environment variable/config for backend API URL

---

## 5. Deployment
- [ ] Prepare production build for React
- [ ] Deploy FastAPI backend (e.g., on Render, Heroku, or similar)
- [ ] Deploy frontend (e.g., Vercel, Netlify, or similar)
- [ ] Update documentation with deployment instructions

---

## 6. Stretch Goals
- [ ] User authentication (optional)
- [ ] Save favorite stores (optional)
- [ ] Export results (CSV, JSON)
- [ ] Map view of results

---

## 7. Timeline
- Week 1: Scaffold backend & frontend, basic search working
- Week 2: UI polish, error handling, integration
- Week 3: Deployment, documentation, stretch goals 