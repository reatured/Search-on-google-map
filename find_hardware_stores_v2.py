import requests
import json
import time

# Replace with your own API key
API_KEY = 'AIzaSyDElHwsa5R4Be53h6mJWEanOzmChyjNwt4'

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
TYPE = 'hardware_store'

all_stores = []
seen_place_ids = set()

print("Searching for hardware stores across Virginia...")
print("=" * 60)

for coords, location_name in VIRGINIA_LOCATIONS:
    print(f"\nSearching in {location_name}...")
    
    # Use the newer Places API format
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': coords,
        'radius': RADIUS,
        'type': TYPE,
        'key': API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') == 'OK':
            stores_found = len(data.get('results', []))
            print(f"Found {stores_found} hardware stores in {location_name}")
            
            for place in data.get('results', []):
                place_id = place.get('place_id')
                
                # Avoid duplicates
                if place_id not in seen_place_ids:
                    seen_place_ids.add(place_id)
                    all_stores.append(place)
                    
                    # Get detailed info
                    details_url = f"https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        'place_id': place_id,
                        'fields': 'name,formatted_phone_number,website,opening_hours,formatted_address',
                        'key': API_KEY
                    }
                    
                    details_response = requests.get(details_url, params=details_params)
                    details = details_response.json().get('result', {})
                    
                    # Add details to the place data
                    place['details'] = details
                    
                    # Print store info
                    name = place.get('name')
                    address = place.get('vicinity')
                    phone = details.get('formatted_phone_number', 'N/A')
                    website = details.get('website', 'N/A')
                    rating = place.get('rating', 'N/A')
                    
                    print(f"  - {name}")
                    print(f"    Address: {address}")
                    print(f"    Phone: {phone}")
                    print(f"    Website: {website}")
                    print(f"    Rating: {rating}")
                    print()
                    
                    # Small delay to avoid hitting API limits
                    time.sleep(0.1)
        else:
            print(f"Error in {location_name}: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error searching in {location_name}: {str(e)}")
    
    # Delay between locations
    time.sleep(1)

print(f"\n" + "=" * 60)
print(f"TOTAL UNIQUE HARDWARE STORES FOUND: {len(all_stores)}")
print("=" * 60)

# Save all results to JSON file
with open('virginia_hardware_stores_complete.json', 'w') as f:
    json.dump({
        'total_stores': len(all_stores),
        'stores': all_stores
    }, f, indent=2)

print(f"\nComplete results saved to 'virginia_hardware_stores_complete.json'")

# Also create a simple text summary
with open('virginia_hardware_stores_summary.txt', 'w') as f:
    f.write("VIRGINIA HARDWARE STORES SUMMARY\n")
    f.write("=" * 40 + "\n\n")
    
    for i, store in enumerate(all_stores, 1):
        name = store.get('name')
        address = store.get('vicinity')
        phone = store.get('details', {}).get('formatted_phone_number', 'N/A')
        website = store.get('details', {}).get('website', 'N/A')
        rating = store.get('rating', 'N/A')
        
        f.write(f"{i}. {name}\n")
        f.write(f"   Address: {address}\n")
        f.write(f"   Phone: {phone}\n")
        f.write(f"   Website: {website}\n")
        f.write(f"   Rating: {rating}\n")
        f.write(f"   {'-' * 30}\n")

print("Text summary saved to 'virginia_hardware_stores_summary.txt'") 