import os
import time
from typing import List, Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is required")

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

app = FastAPI(
    title="Hardware Store Finder API",
    description="Search for hardware stores using Google Places API."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/search",
    response_model=SearchResponse,
    summary="Search hardware stores by location",
    tags=["Search"]
)
def search_hardware_stores(
    location: str = Query(
        ..., 
        description="Address, city, or place to search for hardware stores"
    )
):
    """
    Search for hardware stores near a given location using the Google Places API.
    Returns a list of stores with name, address, website, and phone number.
    """
    try:
        lat, lng = _geocode_location(location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Geocoding API request failed: {e}")

    try:
        all_results = _search_nearby_stores(lat, lng)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Places API request failed: {e}")
    
    if not all_results:
        return SearchResponse(location=location, stores=[])

    stores = _get_store_details(all_results)
    return SearchResponse(location=location, stores=stores)


def _geocode_location(location: str) -> tuple[float, float]:
    """Geocode a location string to lat/lng coordinates."""
    geo_params = {'address': location, 'key': API_KEY}
    geo_resp = requests.get(GEOCODE_URL, params=geo_params, timeout=10)
    geo_resp.raise_for_status()
    
    geo_data = geo_resp.json()
    if geo_data.get('status') != 'OK' or not geo_data.get('results'):
        raise ValueError(f"Geocoding failed: {geo_data.get('status')}")
    
    loc = geo_data['results'][0]['geometry']['location']
    return loc['lat'], loc['lng']


def _search_nearby_stores(lat: float, lng: float) -> List[dict]:
    """Search for nearby hardware stores using Google Places API."""
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
            time.sleep(2)  # Required delay for pagination
        
        resp = requests.get(PLACES_URL, params=params, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        if data.get('status') not in ['OK', 'ZERO_RESULTS']:
            raise requests.RequestException(f"Places API error: {data.get('status')}")
        
        results = data.get('results', [])
        all_results.extend(results)
        
        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break
    
    return all_results


def _get_store_details(stores_data: List[dict]) -> List[Store]:
    """Get detailed information for each store."""
    stores = []
    
    for store in stores_data:
        name = store.get('name', 'N/A')
        place_id = store.get('place_id')
        
        if not place_id:
            continue
        
        details_params = {
            'place_id': place_id,
            'fields': 'name,formatted_phone_number,website,formatted_address,international_phone_number',
            'key': API_KEY
        }
        
        try:
            details_resp = requests.get(DETAILS_URL, params=details_params, timeout=10)
            details_resp.raise_for_status()
            details = details_resp.json().get('result', {})
        except requests.RequestException:
            details = {}
        
        stores.append(Store(
            name=name,
            address=details.get('formatted_address', store.get('vicinity', 'N/A')),
            website=details.get('website'),
            phone=(
                details.get('formatted_phone_number') or 
                details.get('international_phone_number')
            ),
            email=None
        ))
    
    return stores 