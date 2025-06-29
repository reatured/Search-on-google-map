#!/usr/bin/env python3
"""
Script to find hardware stores across Washington State using Google Places API
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

# Multiple Washington State locations to search
WASHINGTON_LOCATIONS = [
    ('47.6062,-122.3321', 'Seattle, WA'),
    ('47.2529,-122.4443', 'Tacoma, WA'),
    ('47.6588,-122.2960', 'Bellevue, WA'),
    ('47.2394,-122.4594', 'Puyallup, WA'),
    ('47.3223,-122.3122', 'Federal Way, WA'),
    ('47.6101,-122.3420', 'Seattle Downtown, WA'),
    ('47.6739,-122.1215', 'Kirkland, WA'),
    ('47.7511,-122.3420', 'Everett, WA'),
    ('47.9789,-122.2021', 'Marysville, WA'),
    ('47.2394,-122.4594', 'Tacoma Area, WA'),
    ('47.7511,-122.3420', 'Snohomish County, WA'),
    ('47.6101,-122.3420', 'King County, WA'),
    ('46.7298,-117.1817', 'Pullman, WA'),
    ('46.2807,-119.2912', 'Kennewick, WA'),
    ('46.2087,-119.1372', 'Pasco, WA'),
    ('46.2312,-119.1773', 'Richland, WA'),
    ('46.6021,-120.5059', 'Yakima, WA'),
    ('47.0424,-122.8930', 'Olympia, WA'),
    ('47.7511,-122.3420', 'Bellingham, WA'),
    ('47.7511,-122.3420', 'Vancouver, WA')
]

RADIUS = 25000  # 25 km radius

all_stores = []
seen_place_ids = set()

print("Searching for hardware stores across Washington State...")
print("=" * 60)

for coords, location_name in WASHINGTON_LOCATIONS:
    print(f"\nSearching in {location_name}...")
    
    # Parse coordinates
    lat, lng = map(float, coords.split(','))
    
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
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            places = data.get('places', [])
            stores_found = len(places)
            print(f"Found {stores_found} hardware stores in {location_name}")
            
            for place in places:
                place_id = place.get('id')
                
                # Avoid duplicates
                if place_id not in seen_place_ids:
                    seen_place_ids.add(place_id)
                    all_stores.append(place)
                    
                    # Extract information
                    display_name = place.get('displayName', {})
                    name = display_name.get('text', 'Unknown')
                    
                    address = place.get('formattedAddress', 'N/A')
                    
                    phone = place.get('nationalPhoneNumber', 'N/A')
                    
                    website = place.get('websiteUri', 'N/A')
                    rating = place.get('rating', 'N/A')
                    user_rating_count = place.get('userRatingCount', 'N/A')
                    
                    # Print store info
                    print(f"  - {name}")
                    print(f"    Address: {address}")
                    print(f"    Phone: {phone}")
                    print(f"    Website: {website}")
                    print(f"    Rating: {rating} ({user_rating_count} reviews)")
                    print()
                    
                    # Small delay to avoid hitting API limits
                    time.sleep(0.1)
        else:
            error_data = response.json()
            print(f"Error in {location_name}: {response.status_code}")
            if 'error' in error_data:
                print(f"  {error_data['error'].get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error searching in {location_name}: {str(e)}")
    
    # Delay between locations
    time.sleep(1)

print(f"\n" + "=" * 60)
print(f"TOTAL UNIQUE HARDWARE STORES FOUND: {len(all_stores)}")
print("=" * 60)

# Save all results to JSON file with timestamp
json_filename = f'washington_hardware_stores_{timestamp}.json'
with open(json_filename, 'w') as f:
    json.dump({
        'total_stores': len(all_stores),
        'search_locations': WASHINGTON_LOCATIONS,
        'timestamp': timestamp,
        'stores': all_stores
    }, f, indent=2)

print(f"\nComplete results saved to '{json_filename}'")

# Create a simple text summary with timestamp
summary_filename = f'washington_hardware_stores_summary_{timestamp}.txt'
with open(summary_filename, 'w') as f:
    f.write("WASHINGTON STATE HARDWARE STORES - FINAL SUMMARY\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Search timestamp: {timestamp}\n")
    f.write(f"Total stores found: {len(all_stores)}\n")
    f.write(f"Search radius: {RADIUS/1000:.1f} km\n")
    f.write(f"Locations searched: {len(WASHINGTON_LOCATIONS)}\n\n")
    
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
    print(f"\n🎉 SUCCESS! Found {len(all_stores)} hardware stores across Washington State!")
    print(f"📅 Search completed at: {timestamp}")
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