import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
PLACES_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

RADIUS = 10000  # 10 km
TYPE = 'hardware_store'


def geocode_location(location):
    params = {
        'address': location,
        'key': API_KEY
    }
    resp = requests.get(GEOCODE_URL, params=params)
    data = resp.json()
    if data['status'] == 'OK' and data['results']:
        loc = data['results'][0]['geometry']['location']
        return loc['lat'], loc['lng']
    else:
        print(f"Geocoding failed: {data.get('status')} - {data.get('error_message', '')}")
        return None, None


def find_hardware_stores(lat, lng):
    params = {
        'location': f'{lat},{lng}',
        'radius': RADIUS,
        'type': TYPE,
        'key': API_KEY
    }
    resp = requests.get(PLACES_URL, params=params)
    data = resp.json()
    return data.get('results', [])


def get_place_details(place_id):
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_phone_number,website,formatted_address,rating,user_ratings_total',
        'key': API_KEY
    }
    resp = requests.get(DETAILS_URL, params=params)
    return resp.json().get('result', {})


def main():
    location = input("Enter a location (address, city, etc.): ").strip()
    lat, lng = geocode_location(location)
    if lat is None or lng is None:
        print("Could not geocode the location. Exiting.")
        return

    print(f"\nSearching for hardware stores near {location} ({lat}, {lng})...\n")
    stores = find_hardware_stores(lat, lng)
    if not stores:
        print("No hardware stores found in this area.")
        return

    for i, store in enumerate(stores, 1):
        name = store.get('name')
        address = store.get('vicinity')
        place_id = store.get('place_id')
        rating = store.get('rating', 'N/A')
        user_ratings_total = store.get('user_ratings_total', 'N/A')

        details = get_place_details(place_id)
        phone = details.get('formatted_phone_number', 'N/A')
        website = details.get('website', 'N/A')
        full_address = details.get('formatted_address', address)

        print(f"=== Hardware Store #{i} ===")
        print(f"Name: {name}")
        print(f"Address: {full_address}")
        print(f"Phone: {phone}")
        print(f"Website: {website}")
        print(f"Rating: {rating} ({user_ratings_total} reviews)")
        print("---")

    # Optionally, save results
    with open('hardware_stores_by_location.json', 'w') as f:
        json.dump(stores, f, indent=2)
    print("\nResults saved to 'hardware_stores_by_location.json'")


if __name__ == "__main__":
    main() 