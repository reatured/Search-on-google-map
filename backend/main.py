import os
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
PLACES_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

app = FastAPI()

# Allow all origins for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search_hardware_stores(location: str = Query(..., description="Address, city, or place to search")):
    # Geocode location
    geo_params = {'address': location, 'key': API_KEY}
    geo_resp = requests.get(GEOCODE_URL, params=geo_params)
    geo_data = geo_resp.json()
    if geo_data['status'] != 'OK' or not geo_data['results']:
        return {"error": f"Geocoding failed: {geo_data.get('status')}"}
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
        resp = requests.get(PLACES_URL, params=params)
        data = resp.json()
        results = data.get('results', [])
        all_results.extend(results)
        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break

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
        details_resp = requests.get(DETAILS_URL, params=details_params)
        details = details_resp.json().get('result', {})
        stores.append({
            'name': name,
            'address': details.get('formatted_address', store.get('vicinity', 'N/A')),
            'website': details.get('website', None),
            'phone': details.get('formatted_phone_number') or details.get('international_phone_number'),
            'email': None  # Email not available from Google Places API
        })
    return {"location": location, "stores": stores} 