#!/usr/bin/env python3
"""
Script to find hardware stores across the United States using Google Places API with pagination
Supports incremental saving and resume functionality
"""

import requests
import json
import time
import os
import csv
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Get current timestamp for file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Major US cities to search - Comprehensive coverage with ~10 cities per state
USA_CITIES = [
    # Alabama (10 cities)
    'Birmingham, AL', 'Montgomery, AL', 'Mobile, AL', 'Huntsville, AL', 'Tuscaloosa, AL',
    'Decatur, AL', 'Auburn, AL', 'Florence, AL', 'Dothan, AL', 'Gadsden, AL',
    
    # Alaska (10 cities)
    'Anchorage, AK', 'Fairbanks, AK', 'Juneau, AK', 'Kodiak, AK', 'Eagle River, AK',
    'North Pole, AK', 'Homer, AK', 'Kenai, AK', 'Palmer, AK', 'Bethel, AK',
    
    # Arizona (10 cities)
    'Phoenix, AZ', 'Tucson, AZ', 'Mesa, AZ', 'Chandler, AZ', 'Glendale, AZ',
    'Scottsdale, AZ', 'Peoria, AZ', 'Gilbert, AZ', 'Surprise, AZ', 'Fountain Hills, AZ',
    
    # Arkansas (10 cities)
    'Little Rock, AR', 'Fayetteville, AR', 'Springdale, AR', 'Fort Smith, AR', 'Jonesboro, AR',
    'Hot Springs, AR', 'West Memphis, AR', 'Searcy, AR', 'Russellville, AR', 'Rogers, AR',
    
    # California (10 cities)
    'Los Angeles, CA', 'San Francisco, CA', 'San Diego, CA', 'Sacramento, CA', 'San Jose, CA',
    'Long Beach, CA', 'Oakland, CA', 'Burbank, CA', 'Riverside, CA', 'Santa Barbara, CA',
    
    # Colorado (10 cities)
    'Denver, CO', 'Fort Collins, CO', 'Colorado Springs, CO', 'Boulder, CO', 'Lakewood, CO',
    'Loveland, CO', 'Aurora, CO', 'Longmont, CO', 'Pueblo, CO', 'Vail, CO',
    
    # Connecticut (10 cities)
    'New Haven, CT', 'Hartford, CT', 'Stamford, CT', 'Waterbury, CT', 'Norwalk, CT',
    'Danbury, CT', 'Bridgeport, CT', 'New Britain, CT', 'Bristol, CT', 'Meriden, CT',
    
    # Delaware (10 cities)
    'Wilmington, DE', 'Dover, DE', 'Milford, DE', 'Smyrna, DE', 'New Castle, DE',
    'Georgetown, DE', 'Middletown, DE', 'Newark, DE', 'Seaford, DE', 'Elsmere, DE',
    
    # Florida (10 cities)
    'Miami, FL', 'Orlando, FL', 'Tampa, FL', 'Jacksonville, FL', 'Fort Lauderdale, FL',
    'Kissimmee, FL', 'Sarasota, FL', 'West Palm Beach, FL', 'Winter Park, FL', 'Bradenton, FL',
    
    # Georgia (10 cities)
    'Atlanta, GA', 'Savannah, GA', 'Macon, GA', 'Athens, GA', 'Augusta, GA',
    'Columbus, GA', 'Brunswick, GA', 'Albany, GA', 'Valdosta, GA', 'Dalton, GA',
    
    # Hawaii (10 cities)
    'Honolulu, HI', 'Kailua, HI', 'Kaneohe, HI', 'Mililani, HI', 'Pearl City, HI',
    'Waipahu, HI', 'Ewa Beach, HI', 'Kapolei, HI', 'Aiea, HI', 'Hilo, HI',
    
    # Idaho (10 cities)
    'Boise, ID', 'Idaho Falls, ID', 'Pocatello, ID', 'Rexburg, ID', 'Twin Falls, ID',
    'Nampa, ID', 'Caldwell, ID', 'Meridian, ID', 'Coeur d\'Alene, ID', 'Lewiston, ID',
    
    # Illinois (10 cities)
    'Chicago, IL', 'Peoria, IL', 'Springfield, IL', 'Rockford, IL', 'Champaign, IL',
    'Bloomington, IL', 'Decatur, IL', 'Aurora, IL', 'Naperville, IL', 'Joliet, IL',
    
    # Indiana (10 cities)
    'Indianapolis, IN', 'Fort Wayne, IN', 'Evansville, IN', 'South Bend, IN', 'Carmel, IN',
    'Fishers, IN', 'Bloomington, IN', 'Hammond, IN', 'Gary, IN', 'Lafayette, IN',
    
    # Iowa (10 cities)
    'Des Moines, IA', 'Cedar Rapids, IA', 'Davenport, IA', 'Sioux City, IA', 'Iowa City, IA',
    'Waterloo, IA', 'Ames, IA', 'West Des Moines, IA', 'Council Bluffs, IA', 'Dubuque, IA',
    
    # Kansas (10 cities)
    'Wichita, KS', 'Kansas City, KS', 'Overland Park, KS', 'Olathe, KS', 'Topeka, KS',
    'Lawrence, KS', 'Shawnee, KS', 'Manhattan, KS', 'Lenexa, KS', 'Salina, KS',
    
    # Kentucky (10 cities)
    'Louisville, KY', 'Lexington, KY', 'Bowling Green, KY', 'Owensboro, KY', 'Covington, KY',
    'Richmond, KY', 'Georgetown, KY', 'Florence, KY', 'Elizabethtown, KY', 'Nicholasville, KY',
    
    # Louisiana (10 cities)
    'New Orleans, LA', 'Baton Rouge, LA', 'Shreveport, LA', 'Lafayette, LA', 'Lake Charles, LA',
    'Kenner, LA', 'Bossier City, LA', 'Monroe, LA', 'Alexandria, LA', 'Houma, LA',
    
    # Maine (10 cities)
    'Portland, ME', 'Lewiston, ME', 'Bangor, ME', 'Auburn, ME', 'Biddeford, ME',
    'Sanford, ME', 'Brunswick, ME', 'Augusta, ME', 'Scarborough, ME', 'Saco, ME',
    
    # Maryland (10 cities)
    'Baltimore, MD', 'Frederick, MD', 'Rockville, MD', 'Gaithersburg, MD', 'Bowie, MD',
    'Hagerstown, MD', 'Annapolis, MD', 'College Park, MD', 'Salisbury, MD', 'Laurel, MD',
    
    # Massachusetts (10 cities)
    'Boston, MA', 'Worcester, MA', 'Springfield, MA', 'Lowell, MA', 'Cambridge, MA',
    'New Bedford, MA', 'Brockton, MA', 'Quincy, MA', 'Lynn, MA', 'Fall River, MA',
    
    # Michigan (10 cities)
    'Detroit, MI', 'Grand Rapids, MI', 'Warren, MI', 'Sterling Heights, MI', 'Ann Arbor, MI',
    'Lansing, MI', 'Flint, MI', 'Dearborn, MI', 'Livonia, MI', 'Westland, MI',
    
    # Minnesota (10 cities)
    'Minneapolis, MN', 'Saint Paul, MN', 'Rochester, MN', 'Duluth, MN', 'Bloomington, MN',
    'Brooklyn Park, MN', 'Plymouth, MN', 'Saint Cloud, MN', 'Woodbury, MN', 'Eagan, MN',
    
    # Mississippi (10 cities)
    'Jackson, MS', 'Gulfport, MS', 'Southaven, MS', 'Hattiesburg, MS', 'Biloxi, MS',
    'Meridian, MS', 'Tupelo, MS', 'Greenville, MS', 'Olive Branch, MS', 'Horn Lake, MS',
    
    # Missouri (10 cities)
    'St. Louis, MO', 'Kansas City, MO', 'Springfield, MO', 'Columbia, MO', 'Independence, MO',
    'Lee\'s Summit, MO', 'O\'Fallon, MO', 'St. Joseph, MO', 'St. Charles, MO', 'St. Peters, MO',
    
    # Montana (10 cities)
    'Billings, MT', 'Missoula, MT', 'Great Falls, MT', 'Bozeman, MT', 'Butte, MT',
    'Helena, MT', 'Kalispell, MT', 'Havre, MT', 'Anaconda, MT', 'Miles City, MT',
    
    # Nebraska (10 cities)
    'Omaha, NE', 'Lincoln, NE', 'Bellevue, NE', 'Grand Island, NE', 'Kearney, NE',
    'Fremont, NE', 'Hastings, NE', 'Norfolk, NE', 'Columbus, NE', 'North Platte, NE',
    
    # Nevada (10 cities)
    'Las Vegas, NV', 'Reno, NV', 'Henderson, NV', 'Carson City, NV', 'Sparks, NV',
    'Elko, NV', 'Mesquite, NV', 'Boulder City, NV', 'Fernley, NV', 'Winnemucca, NV',
    
    # New Hampshire (10 cities)
    'Manchester, NH', 'Nashua, NH', 'Concord, NH', 'Dover, NH', 'Rochester, NH',
    'Keene, NH', 'Derry, NH', 'Portsmouth, NH', 'Laconia, NH', 'Lebanon, NH',
    
    # New Jersey (10 cities)
    'Newark, NJ', 'Jersey City, NJ', 'Paterson, NJ', 'Elizabeth, NJ', 'Edison, NJ',
    'Woodbridge, NJ', 'Lakewood, NJ', 'Toms River, NJ', 'Hamilton, NJ', 'Trenton, NJ',
    
    # New Mexico (10 cities)
    'Albuquerque, NM', 'Santa Fe, NM', 'Las Cruces, NM', 'Rio Rancho, NM', 'Roswell, NM',
    'Farmington, NM', 'Clovis, NM', 'Hobbs, NM', 'Alamogordo, NM', 'Carlsbad, NM',
    
    # New York (10 cities)
    'New York City, NY', 'Albany, NY', 'Buffalo, NY', 'Syracuse, NY', 'Rochester, NY',
    'Yonkers, NY', 'New Rochelle, NY', 'Mount Vernon, NY', 'Schenectady, NY', 'Utica, NY',
    
    # North Carolina (10 cities)
    'Charlotte, NC', 'Raleigh, NC', 'Greensboro, NC', 'Winston-Salem, NC', 'Durham, NC',
    'Fayetteville, NC', 'Cary, NC', 'Wilmington, NC', 'High Point, NC', 'Greenville, NC',
    
    # North Dakota (10 cities)
    'Fargo, ND', 'Bismarck, ND', 'Grand Forks, ND', 'Minot, ND', 'West Fargo, ND',
    'Williston, ND', 'Dickinson, ND', 'Mandan, ND', 'Jamestown, ND', 'Wahpeton, ND',
    
    # Ohio (10 cities)
    'Columbus, OH', 'Cincinnati, OH', 'Cleveland, OH', 'Toledo, OH', 'Akron, OH',
    'Dayton, OH', 'Parma, OH', 'Canton, OH', 'Lorain, OH', 'Hamilton, OH',
    
    # Oklahoma (10 cities)
    'Oklahoma City, OK', 'Tulsa, OK', 'Norman, OK', 'Broken Arrow, OK', 'Lawton, OK',
    'Edmond, OK', 'Moore, OK', 'Midwest City, OK', 'Enid, OK', 'Stillwater, OK',
    
    # Oregon (10 cities)
    'Portland, OR', 'Salem, OR', 'Eugene, OR', 'Gresham, OR', 'Hillsboro, OR',
    'Beaverton, OR', 'Bend, OR', 'Medford, OR', 'Springfield, OR', 'Corvallis, OR',
    
    # Pennsylvania (10 cities)
    'Philadelphia, PA', 'Pittsburgh, PA', 'Allentown, PA', 'Erie, PA', 'Reading, PA',
    'Scranton, PA', 'Bethlehem, PA', 'Lancaster, PA', 'Harrisburg, PA', 'Altoona, PA',
    
    # Rhode Island (10 cities)
    'Providence, RI', 'Warwick, RI', 'Cranston, RI', 'Pawtucket, RI', 'East Providence, RI',
    'Woonsocket, RI', 'Coventry, RI', 'Cumberland, RI', 'North Providence, RI', 'West Warwick, RI',
    
    # South Carolina (10 cities)
    'Charleston, SC', 'Columbia, SC', 'North Charleston, SC', 'Mount Pleasant, SC', 'Rock Hill, SC',
    'Greenville, SC', 'Summerville, SC', 'Sumter, SC', 'Hilton Head Island, SC', 'Florence, SC',
    
    # South Dakota (10 cities)
    'Sioux Falls, SD', 'Rapid City, SD', 'Aberdeen, SD', 'Brookings, SD', 'Watertown, SD',
    'Mitchell, SD', 'Yankton, SD', 'Pierre, SD', 'Huron, SD', 'Vermillion, SD',
    
    # Tennessee (10 cities)
    'Nashville, TN', 'Chattanooga, TN', 'Memphis, TN', 'Knoxville, TN', 'Clarksville, TN',
    'Murfreesboro, TN', 'Franklin, TN', 'Jackson, TN', 'Johnson City, TN', 'Kingsport, TN',
    
    # Texas (10 cities)
    'Houston, TX', 'Dallas, TX', 'San Antonio, TX', 'Austin, TX', 'El Paso, TX',
    'Fort Worth, TX', 'Arlington, TX', 'Corpus Christi, TX', 'Plano, TX', 'Lubbock, TX',
    
    # Utah (10 cities)
    'Salt Lake City, UT', 'West Valley City, UT', 'Provo, UT', 'West Jordan, UT', 'Orem, UT',
    'Sandy, UT', 'Ogden, UT', 'St. George, UT', 'Layton, UT', 'South Jordan, UT',
    
    # Vermont (10 cities)
    'Burlington, VT', 'South Burlington, VT', 'Rutland, VT', 'Barre, VT', 'Montpelier, VT',
    'Winooski, VT', 'St. Albans, VT', 'Newport, VT', 'Vergennes, VT', 'Middlebury, VT',
    
    # Virginia (10 cities)
    'Richmond, VA', 'Arlington, VA', 'Virginia Beach, VA', 'Roanoke, VA', 'Charlottesville, VA',
    'Blacksburg, VA', 'Harrisonburg, VA', 'Winchester, VA', 'Lynchburg, VA', 'Norfolk, VA',
    
    # Washington (10 cities)
    'Seattle, WA', 'Tacoma, WA', 'Bellevue, WA', 'Puyallup, WA', 'Federal Way, WA',
    'Kent, WA', 'Kirkland, WA', 'Everett, WA', 'Marysville, WA', 'Redmond, WA',
    
    # West Virginia (10 cities)
    'Charleston, WV', 'Huntington, WV', 'Parkersburg, WV', 'Morgantown, WV', 'Wheeling, WV',
    'Weirton, WV', 'Fairmont, WV', 'Martinsburg, WV', 'Beckley, WV', 'Clarksburg, WV',
    
    # Wisconsin (10 cities)
    'Milwaukee, WI', 'Madison, WI', 'Green Bay, WI', 'Kenosha, WI', 'Racine, WI',
    'Appleton, WI', 'Waukesha, WI', 'Oshkosh, WI', 'Eau Claire, WI', 'Janesville, WI',
    
    # Wyoming (10 cities)
    'Cheyenne, WY', 'Casper, WY', 'Laramie, WY', 'Gillette, WY', 'Rock Springs, WY',
    'Sheridan, WY', 'Green River, WY', 'Evanston, WY', 'Riverton, WY', 'Cody, WY'
]

# Major national chains to exclude
EXCLUDED_CHAINS = [
    'home depot', 'lowes', 'ace hardware', 'true value', 'menards',
    'harbor freight', 'northern tool', 'tractor supply', 'rural king',
    'atwoods', 'orchard supply', '84 lumber', 'carter lumber',
    'probuild', 'builders firstsource', 'beacon roofing supply',
    'fastenal', 'grainger', 'mcmaster-carr', 'w.w. grainger',
    'do it best', 'coast to coast', 'handy hardware', 'valley hardware',
    'central network retail group', 'orgill', 'do it centers',
    'hardware hank', 'hardware hank\'s', 'hardware hanks',
    'sutherland lumber', 'sutherland\'s lumber', 'sutherlands',
    'stock building supply', 'stock building', 'stock lumber',
    'blue linx', 'blue linx corporation', 'bluelinx',
    'abc supply', 'abc supply co', 'abc supply company',
    'sherwin williams', 'sherwin-williams', 'sherwinwilliams',
    'benjamin moore', 'benjamin moore & co', 'benjamin moore paint',
    'ppg paints', 'ppg architectural coatings', 'ppg',
    'valspar', 'valspar paint', 'valspar corporation',
    'behr', 'behr paint', 'behr process corporation',
    'glidden', 'glidden paint', 'glidden professional',
    'kelly-moore', 'kelly moore', 'kelly moore paint',
    'rodda paint', 'rodda paint company', 'rodda',
    'dunn-edwards', 'dunn edwards', 'dunn edwards paint',
    'cloverdale paint', 'cloverdale', 'cloverdale paint company'
]

# File names for saving progress
PROGRESS_FILE = f'../output/raw/usa_search_progress_{timestamp}.json'
CSV_FILE = f'../output/raw/usa_hardware_stores_{timestamp}.csv'
JSON_FILE = f'../output/raw/usa_hardware_stores_{timestamp}.json'

def load_progress():
    """Load existing progress from file"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
            print(f"📂 Loaded existing progress from {PROGRESS_FILE}")
            print(f"   Cities completed: {len(progress.get('completed_cities', []))}")
            print(f"   Stores found so far: {len(progress.get('all_stores', []))}")
            return progress
        except Exception as e:
            print(f"⚠️  Error loading progress: {e}")
    
    # Initialize new progress
    return {
        'all_stores': [],
        'seen_place_ids': set(),
        'completed_cities': [],
        'start_time': datetime.now().isoformat(),
        'timestamp': timestamp
    }

def save_progress(progress):
    """Save current progress to file"""
    try:
        # Convert set to list for JSON serialization
        progress_to_save = progress.copy()
        progress_to_save['seen_place_ids'] = list(progress['seen_place_ids'])
        
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress_to_save, f, indent=2)
    except Exception as e:
        print(f"⚠️  Error saving progress: {e}")

def save_store_to_csv(store):
    """Save a single store to CSV file"""
    try:
        display_name = store.get('displayName', {})
        name = display_name.get('text', 'Unknown')
        address = store.get('formattedAddress', 'N/A')
        phone = store.get('nationalPhoneNumber', 'N/A')
        website = store.get('websiteUri', 'N/A')
        rating = store.get('rating', 'N/A')
        user_rating_count = store.get('userRatingCount', 'N/A')
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([name, address, phone, website, rating, user_rating_count])
    except Exception as e:
        print(f"⚠️  Error saving to CSV: {e}")

def initialize_csv():
    """Initialize CSV file with headers"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Name', 'Address', 'Phone', 'Website', 'Rating', 'Review Count'])
        print(f"📄 Created CSV file: {CSV_FILE}")

def is_excluded_chain(store_name):
    """Check if store name contains excluded chain names"""
    store_name_lower = store_name.lower()
    for chain in EXCLUDED_CHAINS:
        if chain in store_name_lower:
            return True
    return False

def search_location_with_pagination(city_name, progress):
    """Search a location with pagination to get up to 60 results"""
    location_stores = []
    next_page_token = None
    page_count = 0
    
    while page_count < 3 and (next_page_token is not None or page_count == 0):
        # Use text search instead of nearby search
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': API_KEY,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.types'
        }
        
        payload = {
            "textQuery": f"hardware store in {city_name}",
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
                    if place_id not in progress['seen_place_ids']:
                        # Extract information
                        display_name = place.get('displayName', {})
                        name = display_name.get('text', 'Unknown')
                        
                        # Skip excluded chains
                        if is_excluded_chain(name):
                            continue
                        
                        progress['seen_place_ids'].add(place_id)
                        location_stores.append(place)
                        progress['all_stores'].append(place)
                        
                        # Save to CSV immediately
                        save_store_to_csv(place)
                        
                        address = place.get('formattedAddress', 'N/A')
                        phone = place.get('nationalPhoneNumber', 'N/A')
                        website = place.get('websiteUri', 'N/A')
                        rating = place.get('rating', 'N/A')
                        user_rating_count = place.get('userRatingCount', 'N/A')
                        
                        # Print store info (only for first few stores to avoid spam)
                        if len(location_stores) <= 3:
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
                print(f"Error in {city_name}: {response.status_code}")
                if 'error' in error_data:
                    print(f"  {error_data['error'].get('message', 'Unknown error')}")
                break
                
        except Exception as e:
            print(f"Error searching in {city_name}: {str(e)}")
            break
    
    return location_stores

def main():
    """Main function with resume capability"""
    print("Searching for hardware stores across the United States with pagination...")
    print("=" * 70)
    print(f"🔄 Progress will be saved to: {PROGRESS_FILE}")
    print(f"📄 CSV will be saved to: {CSV_FILE}")
    print(f"📊 JSON will be saved to: {JSON_FILE}")
    print("=" * 70)
    
    # Load existing progress or start new
    progress = load_progress()
    
    # Initialize CSV file
    initialize_csv()
    
    # Determine which cities to process
    completed_cities = set(progress.get('completed_cities', []))
    remaining_cities = [city for city in USA_CITIES if city not in completed_cities]
    
    print(f"\n📋 Progress Summary:")
    print(f"   Total cities: {len(USA_CITIES)}")
    print(f"   Completed: {len(completed_cities)}")
    print(f"   Remaining: {len(remaining_cities)}")
    print(f"   Stores found so far: {len(progress['all_stores'])}")
    
    if not remaining_cities:
        print("✅ All cities have been processed!")
        return
    
    print(f"\n🚀 Starting search for {len(remaining_cities)} remaining cities...")
    
    try:
        for i, city_name in enumerate(remaining_cities, 1):
            print(f"\n[{i}/{len(remaining_cities)}] Searching in {city_name}...")
            
            # Search with pagination
            location_stores = search_location_with_pagination(city_name, progress)
            total_found = len(location_stores)
            
            print(f"Total unique stores found in {city_name}: {total_found}")
            
            # Mark city as completed
            progress['completed_cities'].append(city_name)
            
            # Save progress after each city
            save_progress(progress)
            
            print(f"💾 Progress saved. Total stores: {len(progress['all_stores'])}")
            
            # Delay between locations
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n⏸️  Search interrupted by user.")
        print(f"💾 Saving current progress...")
        save_progress(progress)
        print(f"📊 Progress saved. You can resume later by running the script again.")
        return
    
    # Final save
    save_progress(progress)
    
    print(f"\n" + "=" * 70)
    print(f"TOTAL UNIQUE HARDWARE STORES FOUND: {len(progress['all_stores'])}")
    print("=" * 70)
    
    # Save final results to JSON file
    with open(JSON_FILE, 'w') as f:
        json.dump({
            'total_stores': len(progress['all_stores']),
            'search_cities': USA_CITIES,
            'excluded_chains': EXCLUDED_CHAINS,
            'timestamp': timestamp,
            'stores': progress['all_stores']
        }, f, indent=2)
    
    print(f"\nComplete results saved to '{JSON_FILE}'")
    print(f"CSV file saved to '{CSV_FILE}'")
    
    # Create a simple text summary with timestamp
    summary_filename = f'usa_hardware_stores_summary_{timestamp}.txt'
    with open(summary_filename, 'w') as f:
        f.write("UNITED STATES HARDWARE STORES - FINAL SUMMARY (EXCLUDING MAJOR CHAINS)\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Search timestamp: {timestamp}\n")
        f.write(f"Total stores found: {len(progress['all_stores'])}\n")
        f.write(f"Cities searched: {len(USA_CITIES)}\n")
        f.write(f"Max results per city: 60 (3 pages × 20 results)\n")
        f.write(f"Excluded chains: {', '.join(EXCLUDED_CHAINS)}\n\n")
        
        for i, store in enumerate(progress['all_stores'], 1):
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
            f.write(f"   {'-' * 50}\n")
    
    print(f"Text summary saved to '{summary_filename}'")
    
    # Print final summary to console
    if progress['all_stores']:
        print(f"\n🎉 SUCCESS! Found {len(progress['all_stores'])} hardware stores across the United States!")
        print(f"📅 Search completed at: {timestamp}")
        print(f"🔍 Used pagination to get up to 60 results per city")
        print(f"🗺️ Covered {len(USA_CITIES)} major US cities")
        print(f"🚫 Excluded major national chains")
        print("\nTop stores by rating:")
        
        # Sort by rating (if available)
        rated_stores = [s for s in progress['all_stores'] if s.get('rating') is not None]
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
        print("   3. Search terms and cities are appropriate")

if __name__ == "__main__":
    main() 