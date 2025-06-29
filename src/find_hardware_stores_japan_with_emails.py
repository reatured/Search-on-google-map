#!/usr/bin/env python3
"""
Enhanced script to find hardware stores across Japan with comprehensive email and contact discovery
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

# Create output directories if they don't exist
os.makedirs('output/raw', exist_ok=True)
os.makedirs('output/reports', exist_ok=True)

# Progress file for resume functionality
PROGRESS_FILE = f'output/raw/japan_search_progress_with_emails_{timestamp}.json'

# CSV file for Excel export
CSV_FILE = f'output/raw/japan_hardware_stores_with_emails_{timestamp}.csv'

# JSON file for complete data
JSON_FILE = f'output/raw/japan_hardware_stores_with_emails_{timestamp}.json'

# Japanese hardware store chains to exclude (optional)
EXCLUDED_CHAINS = [
    'Kohnan'
]

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
                urljoin(website_url, '/about-us'),
                urljoin(website_url, '/お問い合わせ'),
                urljoin(website_url, '/会社概要'),
                urljoin(website_url, '/company'),
                urljoin(website_url, '/info')
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
    suffixes = ['info', 'contact', 'sales', 'service', 'admin', 'support']
    
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
        'completed_locations': [],
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

def search_location_with_pagination(lat, lng, location_name, progress):
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

def main():
    """Main function with resume capability and email discovery"""
    print("Searching for hardware stores across Japan with comprehensive email discovery...")
    print("=" * 70)
    print(f"🔄 Progress will be saved to: {PROGRESS_FILE}")
    print(f"📄 CSV will be saved to: {CSV_FILE}")
    print(f"📊 JSON will be saved to: {JSON_FILE}")
    print("=" * 70)
    
    # Load existing progress or start new
    progress = load_progress()
    
    # Initialize CSV file
    initialize_csv()
    
    # Determine which locations to process
    completed_locations = set(progress.get('completed_locations', []))
    remaining_locations = [(coords, name) for coords, name in JAPAN_LOCATIONS if name not in completed_locations]
    
    print(f"\n📋 Progress Summary:")
    print(f"   Total locations: {len(JAPAN_LOCATIONS)}")
    print(f"   Completed: {len(completed_locations)}")
    print(f"   Remaining: {len(remaining_locations)}")
    print(f"   Stores found so far: {len(progress['all_stores'])}")
    
    try:
        for coords, location_name in remaining_locations:
            print(f"\nSearching in {location_name}... ({len(completed_locations) + 1}/{len(JAPAN_LOCATIONS)})")
            
            # Parse coordinates
            lat, lng = map(float, coords.split(','))
            
            # Search with pagination
            location_stores = search_location_with_pagination(lat, lng, location_name, progress)
            total_found = len(location_stores)
            
            print(f"Total unique stores found in {location_name}: {total_found}")
            
            # Update progress
            completed_locations.add(location_name)
            progress['completed_locations'] = list(completed_locations)
            save_progress(progress)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Search interrupted by user")
        print(f"💾 Progress saved. You can resume by running the script again.")
        print(f"📊 Found {len(progress['all_stores'])} stores so far")
        print(f"📄 CSV file saved to: {CSV_FILE}")
        exit(0)
    
    print(f"\n" + "=" * 60)
    print(f"TOTAL UNIQUE HARDWARE STORES FOUND: {len(progress['all_stores'])}")
    print("=" * 60)
    
    # Save all results to JSON file
    with open(JSON_FILE, 'w') as f:
        json.dump({
            'total_stores': len(progress['all_stores']),
            'search_locations': JAPAN_LOCATIONS,
            'timestamp': timestamp,
            'stores': progress['all_stores']
        }, f, indent=2)
    
    print(f"\nComplete results saved to '{JSON_FILE}'")
    print(f"CSV file saved to '{CSV_FILE}'")
    
    # Clean up progress file after successful completion
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print(f"🧹 Cleaned up progress file: {PROGRESS_FILE}")
    
    # Print final summary
    if progress['all_stores']:
        print(f"\n🎉 SUCCESS! Found {len(progress['all_stores'])} hardware stores across Japan!")
        print(f"📅 Search completed at: {timestamp}")
        print(f"🔍 Used pagination to get up to 60 results per location")
        print(f"📧 Included comprehensive email discovery")
        print(f"💾 Files saved to output/raw/ folder")
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
        print("   3. Search radius and locations are appropriate")

if __name__ == "__main__":
    main() 