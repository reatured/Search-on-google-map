import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Multiple Virginia locations to search
VIRGINIA_LOCATIONS = [
    ('37.5407,-77.4360', 'Richmond, VA'),
    ('38.8977,-77.0365', 'Arlington, VA'),
    ('38.9072,-77.0369', 'Washington DC area, VA'),
    ('36.8508,-76.2859', 'Norfolk, VA'),
    ('37.2707,-79.9414', 'Roanoke, VA'),
    ('38.0293,-78.4767', 'Charlottesville, VA'),
    ('37.2296,-80.4139', 'Blacksburg, VA'),
    ('38.4496,-78.8689', 'Harrisonburg, VA'),
    ('39.1857,-78.1633', 'Winchester, VA'),
    ('37.4138,-79.1422', 'Lynchburg, VA')
]

RADIUS = 25000  # 25 km radius

all_stores = []
seen_place_ids = set()

print("Searching for hardware stores across Virginia...")
print("=" * 60)

for coords, location_name in VIRGINIA_LOCATIONS:
    print(f"\nSearching in {location_name}...")
    
    # Parse coordinates
    lat, lng = map(float, coords.split(','))
    
    # Use the newer Places API format
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.phoneNumbers,places.websiteUri,places.rating,places.userRatingCount,places.types'
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
                    
                    phone_numbers = place.get('phoneNumbers', [])
                    phone = phone_numbers[0].get('number', 'N/A') if phone_numbers else 'N/A'
                    
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

# Save all results to JSON file
with open('virginia_hardware_stores_final.json', 'w') as f:
    json.dump({
        'total_stores': len(all_stores),
        'search_locations': VIRGINIA_LOCATIONS,
        'stores': all_stores
    }, f, indent=2)

print(f"\nComplete results saved to 'virginia_hardware_stores_final.json'")

# Create a simple text summary
with open('virginia_hardware_stores_final_summary.txt', 'w') as f:
    f.write("VIRGINIA HARDWARE STORES - FINAL SUMMARY\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Total stores found: {len(all_stores)}\n")
    f.write(f"Search radius: {RADIUS/1000:.1f} km\n")
    f.write(f"Locations searched: {len(VIRGINIA_LOCATIONS)}\n\n")
    
    for i, store in enumerate(all_stores, 1):
        display_name = store.get('displayName', {})
        name = display_name.get('text', 'Unknown')
        address = store.get('formattedAddress', 'N/A')
        
        phone_numbers = store.get('phoneNumbers', [])
        phone = phone_numbers[0].get('number', 'N/A') if phone_numbers else 'N/A'
        
        website = store.get('websiteUri', 'N/A')
        rating = store.get('rating', 'N/A')
        user_rating_count = store.get('userRatingCount', 'N/A')
        
        f.write(f"{i}. {name}\n")
        f.write(f"   Address: {address}\n")
        f.write(f"   Phone: {phone}\n")
        f.write(f"   Website: {website}\n")
        f.write(f"   Rating: {rating} ({user_rating_count} reviews)\n")
        f.write(f"   {'-' * 40}\n")

print("Text summary saved to 'virginia_hardware_stores_final_summary.txt'")

# Print final summary to console
if all_stores:
    print(f"\n🎉 SUCCESS! Found {len(all_stores)} hardware stores across Virginia!")
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