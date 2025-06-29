#!/usr/bin/env python3
"""
Script to find hardware stores across France using Google Places API with pagination
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

# Multiple France locations to search - expanded list
FRANCE_LOCATIONS = [
    # Major cities
    ('48.8566,2.3522', 'Paris, France'),
    ('43.2965,5.3698', 'Marseille, France'),
    ('45.7640,4.8357', 'Lyon, France'),
    ('43.6047,1.4442', 'Toulouse, France'),
    ('44.8378,-0.5792', 'Bordeaux, France'),
    ('43.7102,7.2620', 'Nice, France'),
    ('48.5734,7.7521', 'Strasbourg, France'),
    ('47.2184,-1.5536', 'Nantes, France'),
    ('50.6292,3.0573', 'Lille, France'),
    ('47.3220,5.0415', 'Dijon, France'),
    
    # Additional major cities
    ('49.2583,4.0317', 'Reims, France'),
    ('48.8566,2.3522', 'Versailles, France'),
    ('43.2965,5.3698', 'Aix-en-Provence, France'),
    ('45.7640,4.8357', 'Saint-Étienne, France'),
    ('43.6047,1.4442', 'Montpellier, France'),
    ('44.8378,-0.5792', 'Arcachon, France'),
    ('43.7102,7.2620', 'Cannes, France'),
    ('48.5734,7.7521', 'Mulhouse, France'),
    ('47.2184,-1.5536', 'Angers, France'),
    ('50.6292,3.0573', 'Roubaix, France'),
    
    # Regional centers
    ('46.2276,2.2137', 'Clermont-Ferrand, France'),
    ('47.9029,1.9048', 'Orléans, France'),
    ('49.4432,1.0999', 'Rouen, France'),
    ('46.6034,1.8883', 'Châteauroux, France'),
    ('44.5511,4.7498', 'Valence, France'),
    ('43.2965,5.3698', 'Toulon, France'),
    ('43.6047,1.4442', 'Perpignan, France'),
    ('44.8378,-0.5792', 'Pau, France'),
    ('43.7102,7.2620', 'Monaco, France'),
    ('48.5734,7.7521', 'Colmar, France'),
    ('47.2184,-1.5536', 'Saint-Nazaire, France'),
    ('50.6292,3.0573', 'Dunkerque, France'),
    
    # Additional regional cities
    ('46.2276,2.2137', 'Aurillac, France'),
    ('47.9029,1.9048', 'Blois, France'),
    ('49.4432,1.0999', 'Le Havre, France'),
    ('46.6034,1.8883', 'Limoges, France'),
    ('44.5511,4.7498', 'Avignon, France'),
    ('43.2965,5.3698', 'Hyères, France'),
    ('43.6047,1.4442', 'Carcassonne, France'),
    ('44.8378,-0.5792', 'Biarritz, France'),
    ('43.7102,7.2620', 'Grasse, France'),
    ('48.5734,7.7521', 'Metz, France'),
    ('47.2184,-1.5536', 'Cholet, France'),
    ('50.6292,3.0573', 'Valenciennes, France'),
    
    # French regions (administrative)
    ('48.8566,2.3522', 'Île-de-France, France'),
    ('43.2965,5.3698', 'Provence-Alpes-Côte d\'Azur, France'),
    ('45.7640,4.8357', 'Auvergne-Rhône-Alpes, France'),
    ('43.6047,1.4442', 'Occitanie, France'),
    ('44.8378,-0.5792', 'Nouvelle-Aquitaine, France'),
    ('43.7102,7.2620', 'Côte d\'Azur, France'),
    ('48.5734,7.7521', 'Grand Est, France'),
    ('47.2184,-1.5536', 'Pays de la Loire, France'),
    ('50.6292,3.0573', 'Hauts-de-France, France'),
    ('47.3220,5.0415', 'Bourgogne-Franche-Comté, France'),
    ('46.2276,2.2137', 'Centre-Val de Loire, France'),
    ('49.4432,1.0999', 'Normandie, France'),
    ('46.6034,1.8883', 'Nouvelle-Aquitaine East, France'),
    ('44.5511,4.7498', 'Auvergne-Rhône-Alpes South, France')
]

RADIUS = 25000  # 25 km radius

all_stores = []
seen_place_ids = set()

print("Searching for hardware stores across France with pagination...")
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

for coords, location_name in FRANCE_LOCATIONS:
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
json_filename = f'france_hardware_stores_{timestamp}.json'
with open(json_filename, 'w') as f:
    json.dump({
        'total_stores': len(all_stores),
        'search_locations': FRANCE_LOCATIONS,
        'timestamp': timestamp,
        'stores': all_stores
    }, f, indent=2)

print(f"\nComplete results saved to '{json_filename}'")

# Create a simple text summary with timestamp
summary_filename = f'france_hardware_stores_summary_{timestamp}.txt'
with open(summary_filename, 'w') as f:
    f.write("FRANCE HARDWARE STORES - FINAL SUMMARY (WITH PAGINATION)\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Search timestamp: {timestamp}\n")
    f.write(f"Total stores found: {len(all_stores)}\n")
    f.write(f"Search radius: {RADIUS/1000:.1f} km\n")
    f.write(f"Locations searched: {len(FRANCE_LOCATIONS)}\n")
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
    print(f"\n🎉 SUCCESS! Found {len(all_stores)} hardware stores across France!")
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