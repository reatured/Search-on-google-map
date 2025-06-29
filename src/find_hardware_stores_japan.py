#!/usr/bin/env python3
"""
Script to find hardware stores across Japan using Google Places API with pagination and email search
"""

import requests
import json
import time
import os
import csv
import re
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Get current timestamp for file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create output directories if they don't exist
os.makedirs('output/raw', exist_ok=True)
os.makedirs('output/reports', exist_ok=True)

# Progress file for resume functionality
PROGRESS_FILE = f'output/raw/japan_search_progress_{timestamp}.json'

# CSV file for Excel export
CSV_FILE = f'output/raw/japan_hardware_stores_{timestamp}.csv'

# Extensive Japan locations to search - major cities, prefectures, and regional centers
JAPAN_LOCATIONS = [
    # Tokyo Metropolitan Area (Kanto)
    ('35.6762,139.6503', 'Tokyo, Japan'),
    ('35.4437,139.6380', 'Yokohama, Japan'),
    ('35.8617,139.6455', 'Saitama, Japan'),
    ('35.6762,139.6503', 'Chiba, Japan'),
    ('35.8617,139.6455', 'Kawasaki, Japan'),
    ('35.8617,139.6455', 'Utsunomiya, Japan'),
    ('36.2048,137.2118', 'Matsumoto, Japan'),
    ('36.6485,137.1873', 'Kanazawa, Japan'),
    ('36.6953,137.2117', 'Toyama, Japan'),
    ('36.6485,137.1873', 'Ishikawa, Japan'),
    ('36.6953,137.2117', 'Fukui, Japan'),
    ('35.8617,139.6455', 'Tochigi, Japan'),
    ('36.2048,137.2118', 'Nagano, Japan'),
    ('36.6485,137.1873', 'Niigata, Japan'),
    ('36.6953,137.2117', 'Shizuoka, Japan'),
    ('35.8617,139.6455', 'Gunma, Japan'),
    ('36.2048,137.2118', 'Yamanashi, Japan'),
    ('36.6485,137.1873', 'Fukui, Japan'),
    ('36.6953,137.2117', 'Aichi, Japan'),
    
    # Kansai region
    ('34.6937,135.5023', 'Osaka, Japan'),
    ('35.0116,135.7681', 'Kyoto, Japan'),
    ('34.6901,135.1955', 'Kobe, Japan'),
    ('34.6937,135.5023', 'Nara, Japan'),
    ('34.6901,135.1955', 'Wakayama, Japan'),
    ('34.6937,135.5023', 'Sakai, Japan'),
    ('34.6901,135.1955', 'Himeji, Japan'),
    ('34.6937,135.5023', 'Mie, Japan'),
    ('34.6901,135.1955', 'Hyogo, Japan'),
    ('34.6937,135.5023', 'Shiga, Japan'),
    ('34.6901,135.1955', 'Tottori, Japan'),
    
    # Chubu region
    ('35.1815,136.9066', 'Nagoya, Japan'),
    ('36.2048,137.2118', 'Gifu, Japan'),
    ('36.6953,137.2117', 'Toyama, Japan'),
    ('36.6485,137.1873', 'Ishikawa, Japan'),
    ('36.6953,137.2117', 'Fukui, Japan'),
    ('36.2048,137.2118', 'Matsumoto, Japan'),
    ('36.6485,137.1873', 'Kanazawa, Japan'),
    ('36.6953,137.2117', 'Shizuoka, Japan'),
    ('36.2048,137.2118', 'Yamanashi, Japan'),
    ('36.6485,137.1873', 'Fukui, Japan'),
    ('36.6953,137.2117', 'Aichi, Japan'),
    
    # Tohoku region
    ('38.2688,140.8721', 'Sendai, Japan'),
    ('39.7036,141.1527', 'Morioka, Japan'),
    ('39.7036,141.1527', 'Akita, Japan'),
    ('38.2688,140.8721', 'Yamagata, Japan'),
    ('37.9201,140.1164', 'Fukushima, Japan'),
    ('39.7036,141.1527', 'Aomori, Japan'),
    ('38.2688,140.8721', 'Miyagi, Japan'),
    ('39.7036,141.1527', 'Iwate, Japan'),
    ('39.7036,141.1527', 'Akita, Japan'),
    ('38.2688,140.8721', 'Yamagata, Japan'),
    ('37.9201,140.1164', 'Fukushima, Japan'),
    
    # Kyushu region
    ('33.5902,130.4017', 'Fukuoka, Japan'),
    ('32.7447,129.8736', 'Nagasaki, Japan'),
    ('32.7898,130.7417', 'Kumamoto, Japan'),
    ('31.5602,130.5581', 'Kagoshima, Japan'),
    ('33.5902,130.4017', 'Oita, Japan'),
    ('33.5902,130.4017', 'Kitakyushu, Japan'),
    ('32.7898,130.7417', 'Miyazaki, Japan'),
    ('33.5902,130.4017', 'Saga, Japan'),
    ('32.7898,130.7417', 'Kumamoto, Japan'),
    ('31.5602,130.5581', 'Kagoshima, Japan'),
    ('33.5902,130.4017', 'Fukuoka, Japan'),
    ('32.7447,129.8736', 'Nagasaki, Japan'),
    ('32.7898,130.7417', 'Kumamoto, Japan'),
    ('31.5602,130.5581', 'Kagoshima, Japan'),
    
    # Shikoku region
    ('34.3853,132.4553', 'Hiroshima, Japan'),
    ('34.3853,132.4553', 'Okayama, Japan'),
    ('34.3853,132.4553', 'Matsuyama, Japan'),
    ('34.3853,132.4553', 'Takamatsu, Japan'),
    ('34.3853,132.4553', 'Tokushima, Japan'),
    ('34.3853,132.4553', 'Ehime, Japan'),
    ('34.3853,132.4553', 'Kagawa, Japan'),
    ('34.3853,132.4553', 'Kochi, Japan'),
    ('34.3853,132.4553', 'Hiroshima, Japan'),
    ('34.3853,132.4553', 'Okayama, Japan'),
    
    # Hokkaido region
    ('43.0618,141.3545', 'Sapporo, Japan'),
    ('43.0618,141.3545', 'Hakodate, Japan'),
    ('43.0618,141.3545', 'Asahikawa, Japan'),
    ('43.0618,141.3545', 'Kushiro, Japan'),
    ('43.0618,141.3545', 'Obihiro, Japan'),
    ('43.0618,141.3545', 'Muroran, Japan'),
    ('43.0618,141.3545', 'Otaru, Japan'),
    ('43.0618,141.3545', 'Tomakomai, Japan'),
    ('43.0618,141.3545', 'Iwamizawa, Japan'),
    ('43.0618,141.3545', 'Sapporo, Japan'),
    ('43.0618,141.3545', 'Hakodate, Japan'),
    ('43.0618,141.3545', 'Asahikawa, Japan'),
    
    # Additional major cities and prefectures
    ('35.8617,139.6455', 'Utsunomiya, Japan'),
    ('36.2048,137.2118', 'Matsumoto, Japan'),
    ('36.6485,137.1873', 'Kanazawa, Japan'),
    ('34.6937,135.5023', 'Sakai, Japan'),
    ('34.6901,135.1955', 'Himeji, Japan'),
    ('33.5902,130.4017', 'Kitakyushu, Japan'),
    ('32.7898,130.7417', 'Miyazaki, Japan'),
    ('31.5602,130.5581', 'Naha, Japan'),
    ('35.8617,139.6455', 'Tochigi, Japan'),
    ('36.2048,137.2118', 'Nagano, Japan'),
    ('36.6485,137.1873', 'Niigata, Japan'),
    ('36.6953,137.2117', 'Shizuoka, Japan'),
    ('34.6937,135.5023', 'Mie, Japan'),
    ('34.6901,135.1955', 'Hyogo, Japan'),
    ('33.5902,130.4017', 'Saga, Japan'),
    ('32.7898,130.7417', 'Miyazaki, Japan'),
    ('31.5602,130.5581', 'Okinawa, Japan'),
    
    # More regional centers and smaller cities
    ('35.8617,139.6455', 'Gunma, Japan'),
    ('36.2048,137.2118', 'Yamanashi, Japan'),
    ('36.6485,137.1873', 'Fukui, Japan'),
    ('36.6953,137.2117', 'Aichi, Japan'),
    ('34.6937,135.5023', 'Shiga, Japan'),
    ('34.6901,135.1955', 'Tottori, Japan'),
    ('33.5902,130.4017', 'Nagasaki, Japan'),
    ('32.7898,130.7417', 'Kumamoto, Japan'),
    ('31.5602,130.5581', 'Kagoshima, Japan'),
    ('39.7036,141.1527', 'Aomori, Japan'),
    ('38.2688,140.8721', 'Miyagi, Japan'),
    ('39.7036,141.1527', 'Iwate, Japan'),
    ('34.3853,132.4553', 'Ehime, Japan'),
    ('34.3853,132.4553', 'Kagawa, Japan'),
    ('34.3853,132.4553', 'Kochi, Japan'),
    ('43.0618,141.3545', 'Muroran, Japan'),
    ('43.0618,141.3545', 'Otaru, Japan'),
    ('43.0618,141.3545', 'Tomakomai, Japan'),
    ('43.0618,141.3545', 'Iwamizawa, Japan'),
    
    # Additional locations for comprehensive coverage
    ('35.6762,139.6503', 'Shinjuku, Tokyo, Japan'),
    ('35.6762,139.6503', 'Shibuya, Tokyo, Japan'),
    ('35.6762,139.6503', 'Ginza, Tokyo, Japan'),
    ('35.6762,139.6503', 'Akihabara, Tokyo, Japan'),
    ('35.6762,139.6503', 'Ikebukuro, Tokyo, Japan'),
    ('35.4437,139.6380', 'Yokohama Station, Japan'),
    ('35.4437,139.6380', 'Minato Mirai, Yokohama, Japan'),
    ('34.6937,135.5023', 'Umeda, Osaka, Japan'),
    ('34.6937,135.5023', 'Namba, Osaka, Japan'),
    ('34.6937,135.5023', 'Shinsaibashi, Osaka, Japan'),
    ('35.0116,135.7681', 'Gion, Kyoto, Japan'),
    ('35.0116,135.7681', 'Arashiyama, Kyoto, Japan'),
    ('35.1815,136.9066', 'Sakae, Nagoya, Japan'),
    ('35.1815,136.9066', 'Osu, Nagoya, Japan'),
    ('38.2688,140.8721', 'Sendai Station, Japan'),
    ('33.5902,130.4017', 'Tenjin, Fukuoka, Japan'),
    ('33.5902,130.4017', 'Hakata, Fukuoka, Japan'),
    ('43.0618,141.3545', 'Susukino, Sapporo, Japan'),
    ('43.0618,141.3545', 'Odori, Sapporo, Japan')
]

RADIUS = 25000  # 25 km radius

all_stores = []
seen_place_ids = set()

# Resume functionality
def load_progress():
    """Load progress from file if it exists"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress_data = json.load(f)
                print(f"📂 Found existing progress file: {PROGRESS_FILE}")
                print(f"📊 Resuming from location {progress_data.get('current_location_index', 0)} of {len(JAPAN_LOCATIONS)}")
                return progress_data
        except Exception as e:
            print(f"⚠️ Error loading progress file: {e}")
    return {'current_location_index': 0, 'completed_locations': [], 'all_stores': [], 'seen_place_ids': []}

def save_progress(current_index, completed_locations, stores, seen_ids):
    """Save current progress to file"""
    progress_data = {
        'timestamp': timestamp,
        'current_location_index': current_index,
        'completed_locations': completed_locations,
        'all_stores': stores,
        'seen_place_ids': list(seen_ids),
        'total_locations': len(JAPAN_LOCATIONS)
    }
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress_data, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving progress: {e}")

def save_store_to_csv(store):
    """Save a single store to CSV file with email information"""
    try:
        display_name = store.get('displayName', {})
        name = display_name.get('text', 'Unknown')
        address = store.get('formattedAddress', 'N/A')
        phone = store.get('nationalPhoneNumber', 'N/A')
        website = store.get('websiteUri', 'N/A')
        rating = store.get('rating', 'N/A')
        user_rating_count = store.get('userRatingCount', 'N/A')
        
        # Try to extract email
        email = 'N/A'
        if website and website != 'N/A':
            if '@' in str(store):
                store_str = json.dumps(store)
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', store_str)
                if email_match:
                    email = email_match.group(0)
        
        # Prepare CSV row
        row = [name, address, phone, email, website, rating, user_rating_count]
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(row)
    except Exception as e:
        print(f"⚠️ Error saving to CSV: {e}")

def initialize_csv():
    """Initialize CSV file with headers"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            headers = ['Name', 'Address', 'Phone', 'Email', 'Website', 'Rating', 'Review Count']
            csv_writer.writerow(headers)
        print(f"📄 Created CSV file: {CSV_FILE}")

print("Searching for hardware stores across Japan with pagination and email search...")
print("=" * 60)
print(f"🔄 Progress will be saved to: {PROGRESS_FILE}")
print(f"📄 CSV will be saved to: {CSV_FILE}")
print("=" * 60)

# Load existing progress
progress = load_progress()
current_location_index = progress['current_location_index']
completed_locations = progress['completed_locations']
all_stores = progress['all_stores']
seen_place_ids = set(progress['seen_place_ids'])

print(f"🔄 Starting from location {current_location_index + 1} of {len(JAPAN_LOCATIONS)}")
print(f"📈 Already completed: {len(completed_locations)} locations")
print(f"🏪 Already found: {len(all_stores)} stores")

# Initialize CSV file
initialize_csv()

def get_store_details(place_id):
    """Get detailed information for a store including potential email"""
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'id,displayName,formattedAddress,nationalPhoneNumber,websiteUri,rating,userRatingCount,types,editorialSummary,priceLevel,currentOpeningHours,delivery,servesDinner,servesLunch,servesBreakfast,servesBeer,servesWine,servesCocktails,servesDessert,servesCoffee,outdoorSeating,liveMusic,kidsMenu,menuForChildren,reservable,takeout,dineIn,deliveryOptions,subDeliveryOptions,accessibilityOptions,atmosphere,paymentOptions,services,highlights,popularity,priceLevel,rating,userRatingCount,photos,reviews,utcOffsetMinutes,viewport,location,iconMaskBaseUri,iconBackgroundColor,types,primaryType,primaryTypeDisplayName,shortFormattedAddress,id,internationalPhoneNumber,formattedAddress,addressComponents,plusCode,location,viewport,rating,googleMapsUri,regularOpeningHours,currentOpeningHours,secondaryOpeningHours,editorialSummary,priceLevel,attributions,userRatingCount,photos,reviews,types,primaryType,primaryTypeDisplayName,shortFormattedAddress,delivery,servesDinner,servesLunch,servesBreakfast,servesBeer,servesWine,servesCocktails,servesDessert,servesCoffee,outdoorSeating,liveMusic,kidsMenu,menuForChildren,reservable,takeout,dineIn,deliveryOptions,subDeliveryOptions,accessibilityOptions,atmosphere,paymentOptions,services,highlights,popularity,priceLevel,rating,userRatingCount,photos,reviews,utcOffsetMinutes,viewport,location,iconMaskBaseUri,iconBackgroundColor,types,primaryType,primaryTypeDisplayName,shortFormattedAddress,id,internationalPhoneNumber,formattedAddress,addressComponents,plusCode,location,viewport,rating,googleMapsUri,regularOpeningHours,currentOpeningHours,secondaryOpeningHours,editorialSummary,priceLevel,attributions,userRatingCount,photos,reviews,types,primaryType,primaryTypeDisplayName,shortFormattedAddress,delivery,servesDinner,servesLunch,servesBreakfast,servesBeer,servesWine,servesCocktails,servesDessert,servesCoffee,outdoorSeating,liveMusic,kidsMenu,menuForChildren,reservable,takeout,dineIn,deliveryOptions,subDeliveryOptions,accessibilityOptions,atmosphere,paymentOptions,services,highlights,popularity,priceLevel,rating,userRatingCount,photos,reviews,utcOffsetMinutes,viewport,location,iconMaskBaseUri,iconBackgroundColor,types,primaryType,primaryTypeDisplayName,shortFormattedAddress'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error getting details for {place_id}: {str(e)}")
        return None

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
                        
                        # Get detailed information including potential email
                        details = get_store_details(place_id)
                        if details:
                            place.update(details)
                        
                        location_stores.append(place)
                        all_stores.append(place)
                        
                        # Save to CSV immediately
                        save_store_to_csv(place)
                        
                        # Extract information
                        display_name = place.get('displayName', {})
                        name = display_name.get('text', 'Unknown')
                        
                        address = place.get('formattedAddress', 'N/A')
                        phone = place.get('nationalPhoneNumber', 'N/A')
                        website = place.get('websiteUri', 'N/A')
                        rating = place.get('rating', 'N/A')
                        user_rating_count = place.get('userRatingCount', 'N/A')
                        
                        # Try to extract email from various sources
                        email = 'N/A'
                        if website and website != 'N/A':
                            # Simple email extraction from website or other fields
                            if '@' in str(place):
                                # Look for email in the entire place data
                                place_str = json.dumps(place)
                                import re
                                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', place_str)
                                if email_match:
                                    email = email_match.group(0)
                        
                        # Print store info (only for first few stores to avoid spam)
                        if len(location_stores) <= 5:
                            print(f"    - {name}")
                            print(f"      Address: {address}")
                            print(f"      Phone: {phone}")
                            print(f"      Email: {email}")
                            print(f"      Website: {website}")
                            print(f"      Rating: {rating} ({user_rating_count} reviews)")
                            print()
                        
                        # No delay between stores for faster execution
                
                # Get next page token
                next_page_token = data.get('nextPageToken')
                
                # No delay between pages for faster execution
                    
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

try:
    for i in range(current_location_index, len(JAPAN_LOCATIONS)):
        coords, location_name = JAPAN_LOCATIONS[i]
        print(f"\nSearching in {location_name}... ({i+1}/{len(JAPAN_LOCATIONS)})")
        
        # Parse coordinates
        lat, lng = map(float, coords.split(','))
        
        # Search with pagination
        location_stores = search_location_with_pagination(lat, lng, location_name)
        total_found = len(location_stores)
        
        print(f"Total unique stores found in {location_name}: {total_found}")
        
        # Update progress
        completed_locations.append(location_name)
        save_progress(i + 1, completed_locations, all_stores, seen_place_ids)
        
        # No delay between locations for faster execution

except KeyboardInterrupt:
    print(f"\n⚠️ Search interrupted by user at location {i+1}/{len(JAPAN_LOCATIONS)}")
    print(f"💾 Progress saved. You can resume by running the script again.")
    print(f"📊 Found {len(all_stores)} stores so far")
    print(f"📄 CSV file saved to: {CSV_FILE}")
    exit(0)

print(f"\n" + "=" * 60)
print(f"TOTAL UNIQUE HARDWARE STORES FOUND: {len(all_stores)}")
print("=" * 60)

# Save all results to JSON file with timestamp in correct folder
json_filename = f'output/raw/japan_hardware_stores_{timestamp}.json'
with open(json_filename, 'w') as f:
    json.dump({
        'total_stores': len(all_stores),
        'search_locations': JAPAN_LOCATIONS,
        'timestamp': timestamp,
        'stores': all_stores
    }, f, indent=2)

print(f"\nComplete results saved to '{json_filename}'")

# Create a simple text summary with timestamp in correct folder
summary_filename = f'output/reports/japan_hardware_stores_summary_{timestamp}.txt'
with open(summary_filename, 'w') as f:
    f.write("JAPAN HARDWARE STORES - FINAL SUMMARY (WITH PAGINATION AND EMAIL SEARCH)\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Search timestamp: {timestamp}\n")
    f.write(f"Total stores found: {len(all_stores)}\n")
    f.write(f"Search radius: {RADIUS/1000:.1f} km\n")
    f.write(f"Locations searched: {len(JAPAN_LOCATIONS)}\n")
    f.write(f"Max results per location: 60 (3 pages × 20 results)\n\n")
    
    for i, store in enumerate(all_stores, 1):
        display_name = store.get('displayName', {})
        name = display_name.get('text', 'Unknown')
        address = store.get('formattedAddress', 'N/A')
        phone = store.get('nationalPhoneNumber', 'N/A')
        website = store.get('websiteUri', 'N/A')
        rating = store.get('rating', 'N/A')
        user_rating_count = store.get('userRatingCount', 'N/A')
        
        # Try to extract email
        email = 'N/A'
        if website and website != 'N/A':
            if '@' in str(store):
                import re
                store_str = json.dumps(store)
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', store_str)
                if email_match:
                    email = email_match.group(0)
        
        f.write(f"{i}. {name}\n")
        f.write(f"   Address: {address}\n")
        f.write(f"   Phone: {phone}\n")
        f.write(f"   Email: {email}\n")
        f.write(f"   Website: {website}\n")
        f.write(f"   Rating: {rating} ({user_rating_count} reviews)\n")
        f.write(f"   {'-' * 40}\n")

print(f"Text summary saved to '{summary_filename}'")

# Clean up progress file after successful completion
if os.path.exists(PROGRESS_FILE):
    os.remove(PROGRESS_FILE)
    print(f"🧹 Cleaned up progress file: {PROGRESS_FILE}")

# Print final summary to console
if all_stores:
    print(f"\n🎉 SUCCESS! Found {len(all_stores)} hardware stores across Japan!")
    print(f"📅 Search completed at: {timestamp}")
    print(f"🔍 Used pagination to get up to 60 results per location")
    print(f"📧 Included email search functionality")
    print(f"💾 Files saved to output/raw/ and output/reports/ folders")
    print(f"📄 CSV/Excel file: {CSV_FILE}")
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