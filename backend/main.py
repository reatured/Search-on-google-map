import os
import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel
import time

load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
print("Loaded API KEY:", API_KEY)

GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
PLACES_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

class Store(BaseModel):
    name: str
    address: str
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class SearchResponse(BaseModel):
    location: str
    stores: List[Store]

app = FastAPI(title="Hardware Store Finder API", description="Search for hardware stores using Google Places API.")

# Allow all origins for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search", response_model=SearchResponse, summary="Search hardware stores by location", tags=["Search"])
def search_hardware_stores(
    location: str = Query(..., description="Address, city, or place to search for hardware stores")
):
    """
    Search for hardware stores near a given location using the Google Places API.
    Returns a list of stores with name, address, website, and phone number.
    """
    # Geocode location
    geo_params = {'address': location, 'key': API_KEY}
    try:
        geo_resp = requests.get(GEOCODE_URL, params=geo_params, timeout=10)
        geo_resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Geocoding API request failed: {e}")
    geo_data = geo_resp.json()
    if geo_data.get('status') != 'OK' or not geo_data.get('results'):
        raise HTTPException(status_code=400, detail=f"Geocoding failed: {geo_data.get('status')}")
    loc = geo_data['results'][0]['geometry']['location']
    lat, lng = loc['lat'], loc['lng']

    # Find hardware stores
    params = {
        'location': f'{lat},{lng}',
        'radius': 10000,
        'type': 'hardware_store',
        'key': API_KEY
    }
    all_results = []
    next_page_token = None
    while True:
        if next_page_token:
            params['pagetoken'] = next_page_token
            time.sleep(2)
        try:
            resp = requests.get(PLACES_URL, params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Places API request failed: {e}")
        data = resp.json()
        if data.get('status') not in ['OK', 'ZERO_RESULTS']:
            raise HTTPException(status_code=502, detail=f"Places API error: {data.get('status')}")
        results = data.get('results', [])
        all_results.extend(results)
        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break
    if not all_results:
        return SearchResponse(location=location, stores=[])

    # Get details for each store
    stores = []
    for store in all_results:
        name = store.get('name', 'N/A')
        place_id = store.get('place_id')
        details_params = {
            'place_id': place_id,
            'fields': 'name,formatted_phone_number,website,formatted_address,types,international_phone_number',
            'key': API_KEY
        }
        try:
            details_resp = requests.get(DETAILS_URL, params=details_params, timeout=10)
            details_resp.raise_for_status()
        except requests.RequestException:
            details = {}
        else:
            details = details_resp.json().get('result', {})
        stores.append(Store(
            name=name,
            address=details.get('formatted_address', store.get('vicinity', 'N/A')),
            website=details.get('website'),
            phone=details.get('formatted_phone_number') or details.get('international_phone_number'),
            email=None  # Email not available from Google Places API
        ))
    return SearchResponse(location=location, stores=stores) 