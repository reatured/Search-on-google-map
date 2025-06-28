import requests
import json

# Replace with your own API key
API_KEY = 'AIzaSyDElHwsa5R4Be53h6mJWEanOzmChyjNwt4'
# Virginia coordinates (centered around Richmond, VA)
LOCATION = '37.5407,-77.4360'  # Richmond, VA
RADIUS = 50000  # in meters (50 km) - increased to cover more of Virginia
TYPE = 'hardware_store'

# Step 1: Get nearby hardware stores
url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={LOCATION}&radius={RADIUS}&type={TYPE}&key={API_KEY}"
response = requests.get(url)
data = response.json()

print(f"Searching for hardware stores in Virginia...")
print(f"Found {len(data.get('results', []))} hardware stores\n")

# Step 2: Print basic info for each place
for i, place in enumerate(data.get('results', []), 1):
    name = place.get('name')
    address = place.get('vicinity')
    place_id = place.get('place_id')
    rating = place.get('rating', 'N/A')
    user_ratings_total = place.get('user_ratings_total', 'N/A')

    # Get detailed info using Place Details API
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number,website,opening_hours&key={API_KEY}"
    details_response = requests.get(details_url)
    details = details_response.json().get('result', {})

    phone = details.get('formatted_phone_number', 'N/A')
    website = details.get('website', 'N/A')
    opening_hours = details.get('opening_hours', {}).get('weekday_text', 'N/A')

    print(f"=== Hardware Store #{i} ===")
    print("Name:", name)
    print("Address:", address)
    print("Phone:", phone)
    print("Website:", website)
    print("Rating:", rating)
    print("Total Ratings:", user_ratings_total)
    if opening_hours != 'N/A':
        print("Hours:")
        for day in opening_hours:
            print(f"  {day}")
    print("---")

# Save results to a JSON file for reference
with open('virginia_hardware_stores.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\nResults saved to 'virginia_hardware_stores.json'") 