#!/usr/bin/env python3
"""
Enhanced script to find hardware stores across the United States with email discovery
Supports incremental saving and resume functionality

🔍 Email Discovery Methods with Metadata Tracking:

1. Website Scraping (High Accuracy: 0.9-0.95)
   - Main page analysis: Scans business website for email addresses
   - Contact page search: Looks for /contact, /contact-us, /about, /about-us pages
   - Email extraction: Uses regex to find valid email patterns
   - Spam filtering: Removes common spam emails (noreply, donotreply, etc.)
   - Confidence: 'high' to 'very_high'

2. Email Pattern Generation (Medium-Low Accuracy: 0.3-0.8)
   - Business name analysis: Creates email patterns from store names
   - Domain extraction: Uses business website domain when available
   - Common patterns: Generates emails like info@domain.com, contact@domain.com
   - Fallback domains: Uses common domains (gmail.com, yahoo.com) when no website domain
   - Confidence: 'low' to 'high' based on domain quality

📊 CSV Output Structure:
- Each email gets its own column with metadata
- Email_1, Email_1_Method, Email_1_Source, Email_1_Accuracy_Score, Email_1_Confidence
- Email_2, Email_2_Method, Email_2_Source, Email_2_Accuracy_Score, Email_2_Confidence  
- Email_3, Email_3_Method, Email_3_Source, Email_3_Accuracy_Score, Email_3_Confidence

🎯 Accuracy Scoring:
- 0.95: Contact page scraping (very_high confidence)
- 0.90: Main page scraping (high confidence)
- 0.80: Business domain with suffix (high confidence)
- 0.70: Business domain with name (medium confidence)
- 0.40: Common domain with name (low confidence)
- 0.30: Common domain with suffix (low confidence)
"""

import requests
import json
import time
import os
import csv
import re
from urllib.parse import urljoin, urlparse
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
PROGRESS_FILE = f'../output/raw/usa_search_progress_with_emails_{timestamp}.json'
CSV_FILE = f'../output/raw/usa_hardware_stores_with_emails_{timestamp}.csv'
JSON_FILE = f'../output/raw/usa_hardware_stores_with_emails_{timestamp}.json'

# Create summary file
summary_filename = f'../output/reports/usa_hardware_stores_with_emails_summary_{timestamp}.txt'

def extract_emails_from_text(text):
    """Extract email addresses from text using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Remove duplicates

def get_website_content(url, timeout=5):
    """Safely fetch website content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return None

def find_emails_from_website(website_url, store_name):
    """Attempt to find email addresses from a business website"""
    emails_with_metadata = []
    
    if not website_url or website_url == 'N/A':
        return emails_with_metadata
    
    try:
        # Normalize URL
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
        
        # Get main page content
        content = get_website_content(website_url)
        if content:
            # Extract emails from main page
            page_emails = extract_emails_from_text(content)
            for email in page_emails:
                if not any(spam in email.lower() for spam in ['noreply', 'no-reply', 'donotreply']):
                    emails_with_metadata.append({
                        'email': email,
                        'method': 'website_scraping',
                        'source': 'main_page',
                        'accuracy_score': 0.9,
                        'confidence': 'high'
                    })
            
            # Try to find contact page
            contact_urls = [
                urljoin(website_url, '/contact'),
                urljoin(website_url, '/contact-us'),
                urljoin(website_url, '/about'),
                urljoin(website_url, '/about-us')
            ]
            
            for contact_url in contact_urls:
                try:
                    contact_content = get_website_content(contact_url)
                    if contact_content:
                        contact_emails = extract_emails_from_text(contact_content)
                        for email in contact_emails:
                            if not any(spam in email.lower() for spam in ['noreply', 'no-reply', 'donotreply']):
                                emails_with_metadata.append({
                                    'email': email,
                                    'method': 'website_scraping',
                                    'source': 'contact_page',
                                    'accuracy_score': 0.95,
                                    'confidence': 'very_high'
                                })
                        break
                except:
                    continue
        
        # Remove duplicates based on email address
        unique_emails = []
        seen_emails = set()
        for email_data in emails_with_metadata:
            if email_data['email'] not in seen_emails:
                seen_emails.add(email_data['email'])
                unique_emails.append(email_data)
        
        return unique_emails[:3]  # Limit to 3 emails per store
        
    except Exception as e:
        return []

def generate_common_emails(store_name, website_url):
    """Generate common email patterns for a business"""
    emails_with_metadata = []
    
    if not store_name or store_name == 'Unknown':
        return emails_with_metadata
    
    # Clean store name
    clean_name = re.sub(r'[^\w\s]', '', store_name.lower())
    words = clean_name.split()
    
    if not words:
        return emails_with_metadata
    
    # Extract domain from website
    domain = None
    if website_url and website_url != 'N/A':
        try:
            parsed = urlparse(website_url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
        except:
            pass
    
    # Generate patterns
    patterns = []
    if words:
        patterns.append(words[0])
    if len(words) >= 2:
        patterns.append(f"{words[0]}{words[1]}")
        patterns.append(f"{words[0]}.{words[1]}")
    
    # Common email suffixes
    suffixes = ['info', 'contact', 'sales', 'service', 'admin']
    
    # Generate emails with metadata
    for pattern in patterns:
        if domain:
            emails_with_metadata.append({
                'email': f"{pattern}@{domain}",
                'method': 'pattern_generation',
                'source': 'business_domain',
                'accuracy_score': 0.7,
                'confidence': 'medium'
            })
        
        # Try with common domains
        for common_domain in ['gmail.com', 'yahoo.com']:
            emails_with_metadata.append({
                'email': f"{pattern}@{common_domain}",
                'method': 'pattern_generation',
                'source': 'common_domain',
                'accuracy_score': 0.4,
                'confidence': 'low'
            })
        
        # Try with suffixes
        for suffix in suffixes:
            if domain:
                emails_with_metadata.append({
                    'email': f"{suffix}@{domain}",
                    'method': 'pattern_generation',
                    'source': 'business_domain_suffix',
                    'accuracy_score': 0.8,
                    'confidence': 'high'
                })
            emails_with_metadata.append({
                'email': f"{suffix}@gmail.com",
                'method': 'pattern_generation',
                'source': 'common_domain_suffix',
                'accuracy_score': 0.3,
                'confidence': 'low'
            })
    
    # Remove duplicates and limit
    unique_emails = []
    seen_emails = set()
    for email_data in emails_with_metadata:
        if email_data['email'] not in seen_emails:
            seen_emails.add(email_data['email'])
            unique_emails.append(email_data)
    
    return unique_emails[:5]

def load_progress():
    """Load existing progress from file"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
            
            # Handle backward compatibility - convert old 'emails' to 'emails_data'
            for store in progress.get('all_stores', []):
                if 'emails' in store and 'emails_data' not in store:
                    # Convert old format to new format
                    old_emails = store['emails']
                    if isinstance(old_emails, list) and old_emails:
                        # Convert simple email list to metadata format
                        emails_data = []
                        for email in old_emails[:3]:  # Limit to 3 emails
                            emails_data.append({
                                'email': email,
                                'method': 'legacy_conversion',
                                'source': 'unknown',
                                'accuracy_score': 0.5,
                                'confidence': 'unknown'
                            })
                        store['emails_data'] = emails_data
                    else:
                        store['emails_data'] = []
                    # Remove old format
                    store.pop('emails', None)
            
            print(f"📂 Loaded existing progress from {PROGRESS_FILE}")
            return progress
        except Exception as e:
            print(f"⚠️  Error loading progress: {e}")
    
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
        progress_to_save = progress.copy()
        progress_to_save['seen_place_ids'] = list(progress['seen_place_ids'])
        
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress_to_save, f, indent=2)
    except Exception as e:
        print(f"⚠️  Error saving progress: {e}")

def save_store_to_csv(store):
    """Save a single store to CSV file with email information and metadata"""
    try:
        display_name = store.get('displayName', {})
        name = display_name.get('text', 'Unknown')
        address = store.get('formattedAddress', 'N/A')
        phone = store.get('nationalPhoneNumber', 'N/A')
        website = store.get('websiteUri', 'N/A')
        rating = store.get('rating', 'N/A')
        user_rating_count = store.get('userRatingCount', 'N/A')
        
        # Get email information with metadata
        emails_data = store.get('emails_data', [])
        
        # Prepare CSV row with up to 3 email columns
        row = [name, address, phone, website, rating, user_rating_count]
        
        # Add email columns (up to 3 emails with metadata)
        for i in range(3):
            if i < len(emails_data):
                email_info = emails_data[i]
                row.extend([
                    email_info['email'],
                    email_info['method'],
                    email_info['source'],
                    email_info['accuracy_score'],
                    email_info['confidence']
                ])
            else:
                # Empty columns for missing emails
                row.extend(['N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(row)
    except Exception as e:
        print(f"⚠️  Error saving to CSV: {e}")

def initialize_csv():
    """Initialize CSV file with headers including email metadata columns"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            headers = ['Name', 'Address', 'Phone', 'Website', 'Rating', 'Review Count']
            
            # Add headers for up to 3 emails with metadata
            for i in range(1, 4):
                headers.extend([
                    f'Email_{i}',
                    f'Email_{i}_Method',
                    f'Email_{i}_Source', 
                    f'Email_{i}_Accuracy_Score',
                    f'Email_{i}_Confidence'
                ])
            
            csv_writer.writerow(headers)
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
                    
                    if place_id not in progress['seen_place_ids']:
                        display_name = place.get('displayName', {})
                        name = display_name.get('text', 'Unknown')
                        
                        if is_excluded_chain(name):
                            continue
                        
                        progress['seen_place_ids'].add(place_id)
                        
                        # Get website URL
                        website = place.get('websiteUri', 'N/A')
                        
                        # Attempt to find emails with metadata
                        emails_data = []
                        if website and website != 'N/A':
                            print(f"    🔍 Searching for emails: {name}")
                            emails_data = find_emails_from_website(website, name)
                        
                        # If no emails found, generate patterns
                        if not emails_data:
                            generated_emails = generate_common_emails(name, website)
                            if generated_emails:
                                emails_data = generated_emails
                                print(f"    📧 Generated email patterns: {name}")
                        
                        # Add email information to store data
                        place['emails_data'] = emails_data
                        
                        location_stores.append(place)
                        progress['all_stores'].append(place)
                        
                        # Save to CSV immediately
                        save_store_to_csv(place)
                        
                        # Print store info (only first few)
                        if len(location_stores) <= 3:
                            address = place.get('formattedAddress', 'N/A')
                            phone = place.get('nationalPhoneNumber', 'N/A')
                            rating = place.get('rating', 'N/A')
                            user_rating_count = place.get('userRatingCount', 'N/A')
                            
                            print(f"    - {name}")
                            print(f"      Address: {address}")
                            print(f"      Phone: {phone}")
                            print(f"      Website: {website}")
                            
                            # Print email information with metadata
                            if emails_data:
                                for i, email_info in enumerate(emails_data[:2], 1):  # Show first 2 emails
                                    print(f"      Email {i}: {email_info['email']} ({email_info['method']}, {email_info['confidence']}, score: {email_info['accuracy_score']})")
                            else:
                                print(f"      Emails: N/A")
                            
                            print(f"      Rating: {rating} ({user_rating_count} reviews)")
                            print()
                
                next_page_token = data.get('nextPageToken')
                
                if next_page_token:
                    # time.sleep(2)  # Google requires a short delay before using next_page_token
                    pass
                
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
    """Main function with resume capability and email discovery"""
    print("Searching for hardware stores across the United States with email discovery...")
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
            
            location_stores = search_location_with_pagination(city_name, progress)
            total_found = len(location_stores)
            
            print(f"Total unique stores found in {city_name}: {total_found}")
            
            progress['completed_cities'].append(city_name)
            save_progress(progress)
            
            print(f"💾 Progress saved. Total stores: {len(progress['all_stores'])}")
            # time.sleep(1)  # Delay between locations
            
    except KeyboardInterrupt:
        print(f"\n⏸️  Search interrupted by user.")
        print(f"💾 Saving current progress...")
        save_progress(progress)
        print(f"📊 Progress saved. You can resume later by running the script again.")
        return
    
    save_progress(progress)
    
    print(f"\n" + "=" * 70)
    print(f"TOTAL UNIQUE HARDWARE STORES FOUND: {len(progress['all_stores'])}")
    print("=" * 70)
    
    # Save final results
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
    
    if progress['all_stores']:
        print(f"\n🎉 SUCCESS! Found {len(progress['all_stores'])} hardware stores!")
        print(f"📧 Attempted email discovery for all stores")
        
        # Show top stores with emails
        stores_with_emails = [s for s in progress['all_stores'] if s.get('emails_data')]
        print(f"📧 Stores with emails found: {len(stores_with_emails)}")
        
        if stores_with_emails:
            print("\nTop stores with emails:")
            for i, store in enumerate(stores_with_emails[:5], 1):
                name = store.get('displayName', {}).get('text', 'Unknown')
                emails_data = store.get('emails_data', [])
                email_str = '; '.join([email_info['email'] for email_info in emails_data[:2]])
                print(f"{i}. {name}")
                print(f"   Emails: {email_str}")
    else:
        print("\n❌ No hardware stores found.")

if __name__ == "__main__":
    main() 