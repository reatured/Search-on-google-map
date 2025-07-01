# Hardware Store Finder API

A FastAPI backend for finding hardware stores using Google Places API.

## Railway Deployment

This backend is configured for Railway deployment.

### Environment Variables

Set the following environment variable in Railway:
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key

### API Endpoints

- `GET /search?location={location}`: Search for hardware stores near a location

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API key
   ```

3. Run the server:
   ```bash
   uvicorn main:app --reload
   ``` 