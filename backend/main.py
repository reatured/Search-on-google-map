import os
import requests
from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel
import time
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, create_tables
from models import SearchHistory, Store as StoreModel, LocationCache
import hashlib
from datetime import datetime, timedelta
from fastapi.responses import StreamingResponse
import json
import math

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
    place_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SearchResponse(BaseModel):
    location: str
    stores: List[Store]

class AnalyticsResponse(BaseModel):
    total_searches: int
    successful_searches: int
    total_stores_found: int
    success_rate: float

app = FastAPI(title="Hardware Store Finder API", description="Search for hardware stores using Google Places API.")

# Allow all origins for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/search", response_model=SearchResponse, summary="Search hardware stores by location", tags=["Search"])
def search_hardware_stores(
    location: str = Query(..., description="Address, city, or place to search for hardware stores"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Search for hardware stores near a given location using the Google Places API.
    Returns a list of stores with name, address, website, and phone number.
    Saves search history and store data to database.
    """
    start_time = time.time()
    
    # Create search history record
    search_record = SearchHistory(
        location=location,
        user_ip=request.client.host if request else None,
        search_status='processing'
    )
    db.add(search_record)
    db.commit()
    
    try:
        # Check cache first
        location_hash = hashlib.md5(location.lower().encode()).hexdigest()
        cached_result = db.query(LocationCache).filter(
            LocationCache.location_hash == location_hash,
            LocationCache.expires_at > datetime.utcnow()
        ).first()
        
        if cached_result:
            # Return cached result
            search_record.search_status = 'success'
            search_record.store_count = len(cached_result.results.get('stores', []))
            search_record.response_time_ms = int((time.time() - start_time) * 1000)
            db.commit()
            return SearchResponse(**cached_result.results)
        
        # Geocode location
        geo_params = {'address': location, 'key': API_KEY}
        try:
            geo_resp = requests.get(GEOCODE_URL, params=geo_params, timeout=10)
            geo_resp.raise_for_status()
        except requests.RequestException as e:
            search_record.search_status = 'error'
            db.commit()
            raise HTTPException(status_code=502, detail=f"Geocoding API request failed: {e}")
        
        geo_data = geo_resp.json()
        if geo_data.get('status') != 'OK' or not geo_data.get('results'):
            search_record.search_status = 'error'
            db.commit()
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
                search_record.search_status = 'error'
                db.commit()
                raise HTTPException(status_code=502, detail=f"Places API request failed: {e}")
            
            data = resp.json()
            if data.get('status') not in ['OK', 'ZERO_RESULTS']:
                search_record.search_status = 'error'
                db.commit()
                raise HTTPException(status_code=502, detail=f"Places API error: {data.get('status')}")
            
            results = data.get('results', [])
            all_results.extend(results)
            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break
        
        if not all_results:
            search_record.search_status = 'no_results'
            search_record.store_count = 0
            search_record.response_time_ms = int((time.time() - start_time) * 1000)
            db.commit()
            return SearchResponse(location=location, stores=[])

        # Get details for each store
        stores = []
        for store_data in all_results:
            name = store_data.get('name', 'N/A')
            place_id = store_data.get('place_id')
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
            
            store = Store(
                name=name,
                address=details.get('formatted_address', store_data.get('vicinity', 'N/A')),
                website=details.get('website'),
                phone=details.get('formatted_phone_number') or details.get('international_phone_number'),
                email=None,  # Email not available from Google Places API
                place_id=place_id,
                latitude=store_data.get('geometry', {}).get('location', {}).get('lat'),
                longitude=store_data.get('geometry', {}).get('location', {}).get('lng')
            )
            stores.append(store)
            
            # Save store to database
            db_store = StoreModel(
                search_id=search_record.id,
                name=store.name,
                address=store.address,
                website=store.website,
                phone=store.phone,
                place_id=store.place_id,
                latitude=store.latitude,
                longitude=store.longitude
            )
            db.add(db_store)
        
        # Update search record with results
        search_record.search_status = 'success'
        search_record.store_count = len(stores)
        search_record.response_time_ms = int((time.time() - start_time) * 1000)
        
        # Cache the results for 1 month
        cache_result = LocationCache(
            location_hash=location_hash,
            location=location,
            results={'location': location, 'stores': [store.dict() for store in stores]},
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.add(cache_result)
        
        db.commit()
        return SearchResponse(location=location, stores=stores)
        
    except Exception as e:
        search_record.search_status = 'error'
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/popular-searches", summary="Get most searched locations", tags=["Analytics"])
def get_popular_searches(db: Session = Depends(get_db)):
    """Get most searched locations"""
    popular = db.query(SearchHistory.location, 
                      func.count(SearchHistory.id).label('search_count'))\
                .group_by(SearchHistory.location)\
                .order_by(func.count(SearchHistory.id).desc())\
                .limit(10)\
                .all()
    return [{"location": item.location, "search_count": item.search_count} for item in popular]

@app.get("/analytics/search-stats", response_model=AnalyticsResponse, summary="Get search statistics", tags=["Analytics"])
def get_search_stats(db: Session = Depends(get_db)):
    """Get search statistics"""
    total_searches = db.query(SearchHistory).count()
    successful_searches = db.query(SearchHistory)\
                           .filter(SearchHistory.search_status == 'success')\
                           .count()
    total_stores = db.query(StoreModel).count()
    
    success_rate = (successful_searches / total_searches * 100) if total_searches > 0 else 0
    
    return AnalyticsResponse(
        total_searches=total_searches,
        successful_searches=successful_searches,
        total_stores_found=total_stores,
        success_rate=round(success_rate, 2)
    )

@app.get("/analytics/recent-searches", summary="Get recent searches", tags=["Analytics"])
def get_recent_searches(db: Session = Depends(get_db)):
    """Get recent search history"""
    recent = db.query(SearchHistory)\
               .order_by(SearchHistory.search_timestamp.desc())\
               .limit(20)\
               .all()
    
    return [{
        "id": item.id,
        "location": item.location,
        "search_timestamp": item.search_timestamp,
        "search_status": item.search_status,
        "store_count": item.store_count,
        "response_time_ms": item.response_time_ms
    } for item in recent]

@app.get("/analytics/cached-searches", summary="Get all cached searches", tags=["Analytics"])
def get_cached_searches(db: Session = Depends(get_db)):
    """Get all cached search results from the cache table."""
    cached = db.query(LocationCache).order_by(LocationCache.cached_at.desc()).all()
    return [
        {
            "location": item.location,
            "cached_at": item.cached_at,
            "expires_at": item.expires_at,
            "store_count": len(item.results.get('stores', [])),
            "results": item.results
        }
        for item in cached
    ]

@app.get("/bulk_search", summary="Bulk grid search with streaming results", tags=["Bulk"])
def bulk_search(
    center: List[float] = Query(..., description="[lat, lng] center of search"),
    radius: float = Query(5000, description="Radius in meters (default 5000m)"),
    spacing: float = Query(2000, description="Grid spacing in meters (default 2000m)"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Streams hardware store search results for a grid of points within a circle.
    Deduplicates stores by place_id. Uses city name for search history.
    """
    def generate_grid_points(center, radius, spacing):
        points = []
        R = 6371000
        clat, clng = center
        dLat = spacing / R * (180 / math.pi)
        dLng = spacing / (R * math.cos((math.pi * clat) / 180)) * (180 / math.pi)
        for lat in frange(clat - radius / R * (180 / math.pi), clat + radius / R * (180 / math.pi), dLat):
            for lng in frange(clng - radius / (R * math.cos((math.pi * clat) / 180)) * (180 / math.pi), clng + radius / (R * math.cos((math.pi * clat) / 180)) * (180 / math.pi), dLng):
                d = R * math.acos(
                    math.sin(clat * math.pi / 180) * math.sin(lat * math.pi / 180) +
                    math.cos(clat * math.pi / 180) * math.cos(lat * math.pi / 180) * math.cos((lng - clng) * math.pi / 180)
                )
                if d <= radius:
                    points.append((lat, lng))
        return points
    def frange(start, stop, step):
        while start <= stop:
            yield start
            start += step
    def stream():
        seen_place_ids = set()
        city_name = None
        points = generate_grid_points(center, radius, spacing)
        for idx, (lat, lng) in enumerate(points):
            # Reverse geocode for city name (only once, at center)
            if idx == 0:
                geo_params = {'latlng': f'{lat},{lng}', 'key': API_KEY}
                try:
                    geo_resp = requests.get(GEOCODE_URL, params=geo_params, timeout=10)
                    geo_resp.raise_for_status()
                    geo_data = geo_resp.json()
                    if geo_data.get('status') == 'OK' and geo_data.get('results'):
                        for comp in geo_data['results'][0].get('address_components', []):
                            if 'locality' in comp['types']:
                                city_name = comp['long_name']
                                break
                        if not city_name:
                            city_name = geo_data['results'][0].get('formatted_address', f'{lat},{lng}')
                    else:
                        city_name = f'{lat},{lng}'
                except Exception:
                    city_name = f'{lat},{lng}'
            # Search for hardware stores at this point
            params = {
                'location': f'{lat},{lng}',
                'radius': 10000,
                'type': 'hardware_store',
                'key': API_KEY
            }
            try:
                resp = requests.get(PLACES_URL, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                stores = []
                for store_data in data.get('results', []):
                    place_id = store_data.get('place_id')
                    if place_id and place_id not in seen_place_ids:
                        seen_place_ids.add(place_id)
                        stores.append({
                            'name': store_data.get('name', 'N/A'),
                            'address': store_data.get('vicinity', ''),
                            'place_id': place_id,
                            'latitude': store_data.get('geometry', {}).get('location', {}).get('lat'),
                            'longitude': store_data.get('geometry', {}).get('location', {}).get('lng')
                        })
                yield f"data: {json.dumps({'lat': lat, 'lng': lng, 'stores': stores, 'city': city_name})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'lat': lat, 'lng': lng, 'stores': [], 'error': str(e), 'city': city_name})}\n\n"
            time.sleep(0.5)  # Throttle to avoid API rate limits
    return StreamingResponse(stream(), media_type="text/event-stream") 