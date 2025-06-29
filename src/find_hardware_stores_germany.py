#!/usr/bin/env python3
"""
Script to find hardware stores across Germany using Google Places API with pagination
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Get current timestamp for file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Multiple Germany locations to search - comprehensive list
GERMANY_LOCATIONS = [
    # Major cities
    ('52.5200,13.4050', 'Berlin, Germany'),
    ('53.5511,9.9937', 'Hamburg, Germany'),
    ('50.9375,6.9603', 'Cologne, Germany'),
    ('48.1351,11.5820', 'Munich, Germany'),
    ('50.1109,8.6821', 'Frankfurt, Germany'),
    ('51.3397,12.3731', 'Leipzig, Germany'),
    ('51.4556,7.0116', 'Essen, Germany'),
    ('51.5136,7.4653', 'Dortmund, Germany'),
    ('51.2277,6.7735', 'Düsseldorf, Germany'),
    ('53.0793,8.8017', 'Bremen, Germany'),
    
    # Additional major cities
    ('49.4521,11.0767', 'Nuremberg, Germany'),
    ('50.9375,6.9603', 'Bonn, Germany'),
    ('48.1351,11.5820', 'Augsburg, Germany'),
    ('50.1109,8.6821', 'Wiesbaden, Germany'),
    ('51.3397,12.3731', 'Dresden, Germany'),
    ('51.4556,7.0116', 'Duisburg, Germany'),
    ('51.5136,7.4653', 'Bochum, Germany'),
    ('51.2277,6.7735', 'Wuppertal, Germany'),
    ('53.0793,8.8017', 'Hannover, Germany'),
    ('49.4521,11.0767', 'Fürth, Germany'),
    
    # Regional centers
    ('48.7758,9.1829', 'Stuttgart, Germany'),
    ('49.0069,8.4037', 'Karlsruhe, Germany'),
    ('49.4521,11.0767', 'Erlangen, Germany'),
    ('50.1109,8.6821', 'Mannheim, Germany'),
    ('51.3397,12.3731', 'Chemnitz, Germany'),
    ('51.4556,7.0116', 'Oberhausen, Germany'),
    ('51.5136,7.4653', 'Hagen, Germany'),
    ('51.2277,6.7735', 'Mönchengladbach, Germany'),
    ('53.0793,8.8017', 'Braunschweig, Germany'),
    ('49.4521,11.0767', 'Würzburg, Germany'),
    
    # Additional regional cities
    ('48.7758,9.1829', 'Heilbronn, Germany'),
    ('49.0069,8.4037', 'Pforzheim, Germany'),
    ('49.4521,11.0767', 'Bamberg, Germany'),
    ('50.1109,8.6821', 'Ludwigshafen, Germany'),
    ('51.3397,12.3731', 'Zwickau, Germany'),
    ('51.4556,7.0116', 'Mülheim, Germany'),
    ('51.5136,7.4653', 'Hamm, Germany'),
    ('51.2277,6.7735', 'Leverkusen, Germany'),
    ('53.0793,8.8017', 'Oldenburg, Germany'),
    ('49.4521,11.0767', 'Regensburg, Germany'),
    
    # German states (Bundesländer) - major cities
    ('52.5200,13.4050', 'Berlin State, Germany'),
    ('53.5511,9.9937', 'Hamburg State, Germany'),
    ('48.1351,11.5820', 'Bavaria, Germany'),
    ('50.1109,8.6821', 'Hesse, Germany'),
    ('51.3397,12.3731', 'Saxony, Germany'),
    ('51.4556,7.0116', 'North Rhine-Westphalia, Germany'),
    ('53.0793,8.8017', 'Lower Saxony, Germany'),
    ('49.4521,11.0767', 'Baden-Württemberg, Germany'),
    ('48.7758,9.1829', 'Baden-Württemberg South, Germany'),
    ('49.0069,8.4037', 'Baden-Württemberg North, Germany'),
    ('51.2277,6.7735', 'North Rhine-Westphalia West, Germany'),
    ('51.5136,7.4653', 'North Rhine-Westphalia East, Germany'),
    ('53.5511,9.9937', 'Schleswig-Holstein, Germany'),
    ('54.3233,10.1228', 'Schleswig-Holstein North, Germany'),
    ('52.5200,13.4050', 'Brandenburg, Germany'),
    ('51.3397,12.3731', 'Saxony-Anhalt, Germany'),
    ('50.9375,6.9603', 'Rhineland-Palatinate, Germany'),
    ('49.4521,11.0767', 'Thuringia, Germany'),
    ('51.2277,6.7735', 'Saarland, Germany'),
    ('53.0793,8.8017', 'Mecklenburg-Vorpommern, Germany'),
    
    # Border regions and international areas
    ('47.5579,7.5886', 'Freiburg, Germany'),
    ('49.0069,8.4037', 'Heidelberg, Germany'),
    ('49.4521,11.0767', 'Bayreuth, Germany'),
    ('50.1109,8.6821', 'Mainz, Germany'),
    ('51.3397,12.3731', 'Halle, Germany'),
    ('51.4556,7.0116', 'Gelsenkirchen, Germany'),
    ('51.5136,7.4653', 'Herne, Germany'),
    ('51.2277,6.7735', 'Krefeld, Germany'),
    ('53.0793,8.8017', 'Osnabrück, Germany'),
    ('49.4521,11.0767', 'Hof, Germany'),
    
    # Additional cities for comprehensive coverage
    ('48.7758,9.1829', 'Tübingen, Germany'),
    ('49.0069,8.4037', 'Heidelberg, Germany'),
    ('49.4521,11.0767', 'Coburg, Germany'),
    ('50.1109,8.6821', 'Offenbach, Germany'),
    ('51.3397,12.3731', 'Plauen, Germany'),
    ('51.4556,7.0116', 'Bottrop, Germany'),
    ('51.5136,7.4653', 'Recklinghausen, Germany'),
    ('51.2277,6.7735', 'Neuss, Germany'),
    ('53.0793,8.8017', 'Wolfsburg, Germany'),
    ('49.4521,11.0767', 'Hof, Germany')
]

RADIUS = 25000  # 25 km radius

all_stores = []
seen_place_ids = set()

print("Searching for hardware stores across Germany with pagination...")
print("=" * 60)

def search_location_with_pagination(lat, lng, location_name):
    """Search a location with pagination to get up to 60 results"""
    location_stores = []
    next_page_token = None
    page_count = 0
    
    while page_count < 3 and (next_page_token is not None or page_count == 0):
        # Use the newer Places API format with correct field names
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': API_KEY,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.types'
        }
        
        payload = {
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": RADIUS
                }
            },
            "includedTypes": ["hardware_store"],
            "maxResultCount": 20
        }
        
        # Add next page token if available
        if next_page_token:
            payload["pageToken"] = next_page_token
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                places = data.get('places', [])
                stores_found = len(places)
                page_count += 1
                
                print(f"  Page {page_count}: Found {stores_found} hardware stores")
                
                for place in places:
                    place_id = place.get('id')
                    
                    # Avoid duplicates
                    if place_id not in seen_place_ids:
                        seen_place_ids.add(place_id)
                        location_stores.append(place)
                        all_stores.append(place)
                        
                        # Extract information
                        display_name = place.get('displayName', {})
                        name = display_name.get('text', 'Unknown')
                        
                        address = place.get('formattedAddress', 'N/A')
                        phone = place.get('nationalPhoneNumber', 'N/A')
                        website = place.get('websiteUri', 'N/A')
                        rating = place.get('rating', 'N/A')
                        user_rating_count = place.get('userRatingCount', 'N/A')
                        
                        # Print store info (only for first few stores to avoid spam)
                        if len(location_stores) <= 5:
                            print(f"    - {name}")
                            print(f"      Address: {address}")
                            print(f"      Phone: {phone}")
                            print(f"      Website: {website}")
                            print(f"      Rating: {rating} ({user_rating_count} reviews)")
                            print()
                        
                        # Small delay to avoid hitting API limits
                        time.sleep(0.1)
                
                # Get next page token
                next_page_token = data.get('nextPageToken')
                
                # Wait 2 seconds before next page (API requirement)
                if next_page_token:
                    time.sleep(2)
                    
            else:
                error_data = response.json()
                print(f"Error in {location_name}: {response.status_code}")
                if 'error' in error_data:
                    print(f"  {error_data['error'].get('message', 'Unknown error')}")
                break
                
        except Exception as e:
            print(f"Error searching in {location_name}: {str(e)}")
            break
    
    return location_stores

for coords, location_name in GERMANY_LOCATIONS:
    print(f"\nSearching in {location_name}...")
    
    # Parse coordinates
    lat, lng = map(float, coords.split(','))
    
    # Search with pagination
    location_stores = search_location_with_pagination(lat, lng, location_name)
    total_found = len(location_stores)
    
    print(f"Total unique stores found in {location_name}: {total_found}")
    
    # Delay between locations
    time.sleep(1)

print(f"\n" + "=" * 60)
print(f"TOTAL UNIQUE HARDWARE STORES FOUND: {len(all_stores)}")
print("=" * 60)

# Save all results to JSON file with timestamp
json_filename = f'germany_hardware_stores_{timestamp}.json'
with open(json_filename, 'w') as f:
    json.dump({
        'total_stores': len(all_stores),
        'search_locations': GERMANY_LOCATIONS,
        'timestamp': timestamp,
        'stores': all_stores
    }, f, indent=2)

print(f"\nComplete results saved to '{json_filename}'")

# Create a simple text summary with timestamp
summary_filename = f'germany_hardware_stores_summary_{timestamp}.txt'
with open(summary_filename, 'w') as f:
    f.write("GERMANY HARDWARE STORES - FINAL SUMMARY (WITH PAGINATION)\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Search timestamp: {timestamp}\n")
    f.write(f"Total stores found: {len(all_stores)}\n")
    f.write(f"Search radius: {RADIUS/1000:.1f} km\n")
    f.write(f"Locations searched: {len(GERMANY_LOCATIONS)}\n")
    f.write(f"Max results per location: 60 (3 pages × 20 results)\n\n")
    
    for i, store in enumerate(all_stores, 1):
        display_name = store.get('displayName', {})
        name = display_name.get('text', 'Unknown')
        address = store.get('formattedAddress', 'N/A')
        phone = store.get('nationalPhoneNumber', 'N/A')
        website = store.get('websiteUri', 'N/A')
        rating = store.get('rating', 'N/A')
        user_rating_count = store.get('userRatingCount', 'N/A')
        
        f.write(f"{i}. {name}\n")
        f.write(f"   Address: {address}\n")
        f.write(f"   Phone: {phone}\n")
        f.write(f"   Website: {website}\n")
        f.write(f"   Rating: {rating} ({user_rating_count} reviews)\n")
        f.write(f"   {'-' * 40}\n")

print(f"Text summary saved to '{summary_filename}'")

# Print final summary to console
if all_stores:
    print(f"\n🎉 SUCCESS! Found {len(all_stores)} hardware stores across Germany!")
    print(f"📅 Search completed at: {timestamp}")
    print(f"🔍 Used pagination to get up to 60 results per location")
    print("\nTop stores by rating:")
    
    # Sort by rating (if available)
    rated_stores = [s for s in all_stores if s.get('rating') is not None]
    rated_stores.sort(key=lambda x: x.get('rating', 0), reverse=True)
    
    for i, store in enumerate(rated_stores[:5], 1):
        name = store.get('displayName', {}).get('text', 'Unknown')
        rating = store.get('rating', 'N/A')
        address = store.get('formattedAddress', 'N/A')
        print(f"{i}. {name} - Rating: {rating}")
        print(f"   {address}")
else:
    print("\n❌ No hardware stores found. Please check:")
    print("   1. API key is correct")
    print("   2. Places API (New) is enabled")
    print("   3. Search radius and locations are appropriate") 