import requests
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
PLACES_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

RADIUS = 10000  # 10 km
TYPE = 'hardware_store'

# Known contact information for major hardware chains
KNOWN_CHAINS = {
    'leroy merlin': {
        'website': 'https://www.leroymerlin.fr',
        'phone': '+33 892 23 23 23',
        'email': 'contact@leroymerlin.fr'
    },
    'castorama': {
        'website': 'https://www.castorama.fr',
        'phone': '+33 892 23 23 23',
        'email': 'contact@castorama.fr'
    },
    'home depot': {
        'website': 'https://www.homedepot.com',
        'phone': '+1-800-466-3337',
        'email': 'customerservice@homedepot.com'
    },
    'lowes': {
        'website': 'https://www.lowes.com',
        'phone': '+1-800-445-6937',
        'email': 'customerservice@lowes.com'
    },
    'ace hardware': {
        'website': 'https://www.acehardware.com',
        'phone': '+1-888-827-4223',
        'email': 'customerservice@acehardware.com'
    },
    'harbor freight': {
        'website': 'https://www.harborfreight.com',
        'phone': '+1-800-444-3353',
        'email': 'customerservice@harborfreight.com'
    }
}


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
    all_results = []
    params = {
        'location': f'{lat},{lng}',
        'radius': RADIUS,
        'type': TYPE,
        'key': API_KEY
    }
    next_page_token = None
    while True:
        if next_page_token:
            params['pagetoken'] = next_page_token
            time.sleep(2)  # Google requires a short delay before using next_page_token
        resp = requests.get(PLACES_URL, params=params)
        data = resp.json()
        results = data.get('results', [])
        all_results.extend(results)
        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break
    return all_results


def get_place_details(place_id):
    # Request all available fields for better data
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_phone_number,website,formatted_address,email,types,opening_hours,price_level,rating,user_ratings_total,international_phone_number',
        'key': API_KEY
    }
    resp = requests.get(DETAILS_URL, params=params)
    return resp.json().get('result', {})


def get_contact_info(name, details):
    """Get contact information from API or known chains"""
    name_lower = name.lower()
    
    # Check if it's a known chain
    for chain, info in KNOWN_CHAINS.items():
        if chain in name_lower:
            return {
                'website': info['website'],
                'phone': info['phone'],
                'email': info['email']
            }
    
    # Try to get from API details
    website = details.get('website', 'N/A')
    phone = details.get('formatted_phone_number') or details.get('international_phone_number') or 'N/A'
    email = details.get('email', 'N/A')
    
    # If no email from API, try to construct from website
    if email == 'N/A' and website != 'N/A':
        domain = website.replace('https://', '').replace('http://', '').replace('www.', '')
        if domain and '.' in domain:
            email = f"info@{domain}"
    
    return {
        'website': website,
        'phone': phone,
        'email': email
    }


def main():
    location = input("Enter a location (address, city, etc.): ").strip()
    lat, lng = geocode_location(location)
    if lat is None or lng is None:
        print("Could not geocode the location. Exiting.")
        return

    print(f"\nSearching for hardware stores near {location}...\n")
    stores = find_hardware_stores(lat, lng)
    if not stores:
        print("No hardware stores found in this area.")
        return

    # Create simplified results list
    simplified_results = []
    
    for i, store in enumerate(stores, 1):
        name = store.get('name', 'N/A')
        place_id = store.get('place_id')
        
        # Get detailed information
        details = get_place_details(place_id)
        
        # Get contact information
        contact_info = get_contact_info(name, details)
        
        # Extract address
        address = details.get('formatted_address', store.get('vicinity', 'N/A'))
        
        # Extract category/type
        types = details.get('types', [])
        category = ', '.join(types) if types else 'Hardware Store'

        # Create simplified store info
        store_info = {
            'name': name,
            'category': category,
            'email': contact_info['email'],
            'location': address,
            'website': contact_info['website'],
            'phone': contact_info['phone']
        }
        
        simplified_results.append(store_info)

        # Print simplified output
        print(f"{i}. {name}")
        print(f"   分类: {category}")
        print(f"   邮箱: {contact_info['email']}")
        print(f"   地点: {address}")
        print(f"   网站: {contact_info['website']}")
        print(f"   电话: {contact_info['phone']}")
        print()
        
        # Small delay to avoid hitting API limits
        time.sleep(0.1)

    # Save results to JSON file
    json_filename = f'../output/raw/hardware_stores_by_location.json'
    with open(json_filename, 'w') as f:
        json.dump({
            'location': location,
            'total_stores': len(stores),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'stores': simplified_results
        }, f, indent=2)
    
    print(f"Results saved to '{json_filename}'")
    print("\nNote: For stores without contact info, you can:")
    print("- Search the business name on Google")
    print("- Check their website for contact details")
    print("- Call the store directly if phone number is available")


if __name__ == "__main__":
    main() 