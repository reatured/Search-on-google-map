import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Test the API key
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

print("Testing Google Places API Key...")
print("=" * 50)

# Test 1: Basic Places API call
print("\n1. Testing basic Places API...")
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
params = {
    'location': '37.5407,-77.4360',  # Richmond, VA
    'radius': 5000,
    'type': 'hardware_store',
    'key': API_KEY
}

try:
    response = requests.get(url, params=params)
    data = response.json()
    
    print(f"Status: {data.get('status')}")
    if 'error_message' in data:
        print(f"Error: {data.get('error_message')}")
    else:
        print(f"Results found: {len(data.get('results', []))}")
        
except Exception as e:
    print(f"Request failed: {str(e)}")

# Test 2: Try the newer Places API format
print("\n2. Testing newer Places API format...")
url = "https://places.googleapis.com/v1/places:searchNearby"
headers = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': API_KEY,
    'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.phoneNumbers,places.websiteUri'
}

payload = {
    "locationRestriction": {
        "circle": {
            "center": {
                "latitude": 37.5407,
                "longitude": -77.4360
            },
            "radius": 5000.0
        }
    },
    "includedTypes": ["hardware_store"]
}

try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Results found: {len(data.get('places', []))}")
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Request failed: {str(e)}")

print("\n" + "=" * 50)
print("API KEY SETUP INSTRUCTIONS:")
print("=" * 50)
print("""
To get a working Google Places API key:

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Places API
   - Maps JavaScript API
   - Geocoding API
4. Go to "Credentials" and create an API key
5. Restrict the API key to only the APIs you need
6. Replace the API_KEY variable in the script with your new key

The current API key appears to be using a legacy API that's not enabled.
You need to enable the Places API in your Google Cloud project.
""") 