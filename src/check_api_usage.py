#!/usr/bin/env python3
"""
Script to check Google Places API usage and limits
"""

import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

def check_api_usage():
    """Check current API usage by making a test request and checking headers"""
    
    print("Checking Google Places API usage...")
    print("=" * 50)
    
    # Test the new Places API
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'places.id,places.displayName'
    }
    
    payload = {
        "textQuery": "hardware store in New York",
        "maxResultCount": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Response Status: {response.status_code}")
        
        # Check for rate limiting headers
        headers_to_check = [
            'X-RateLimit-Limit',
            'X-RateLimit-Remaining', 
            'X-RateLimit-Reset',
            'Quota-User',
            'X-Goog-QuotaUser'
        ]
        
        print("\nRate Limiting Headers:")
        for header in headers_to_check:
            value = response.headers.get(header)
            if value:
                print(f"  {header}: {value}")
            else:
                print(f"  {header}: Not present")
        
        # Check response content
        if response.status_code == 200:
            data = response.json()
            places = data.get('places', [])
            print(f"\n✅ API is working! Found {len(places)} places in test query")
            
            # Check for quota information in response
            if 'error' in data:
                print(f"⚠️  API Error: {data['error']}")
                
        elif response.status_code == 429:
            print("❌ Rate limit exceeded!")
            print("Response headers:", dict(response.headers))
            
        elif response.status_code == 403:
            print("❌ Quota exceeded or API not enabled!")
            print("Response:", response.text)
            
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")

def check_google_cloud_console_info():
    """Provide information about checking usage in Google Cloud Console"""
    
    print("\n" + "=" * 50)
    print("HOW TO CHECK YOUR API USAGE:")
    print("=" * 50)
    
    print("1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print("\n2. Select your project")
    
    print("\n3. Go to APIs & Services > Dashboard")
    print("   https://console.cloud.google.com/apis/dashboard")
    
    print("\n4. Click on 'Places API (New)' or 'Places API'")
    
    print("\n5. Check the 'Quotas' tab for:")
    print("   - Requests per day")
    print("   - Requests per 100 seconds")
    print("   - Current usage")
    
    print("\n6. Go to 'Credentials' to see:")
    print("   - API key restrictions")
    print("   - Quota limits")
    
    print("\n7. Check 'Reports' for detailed usage analytics")

def estimate_usage_for_usa_script():
    """Estimate API usage for the USA script"""
    
    print("\n" + "=" * 50)
    print("ESTIMATED API USAGE FOR USA SCRIPT:")
    print("=" * 50)
    
    cities = 500
    pages_per_city = 3
    requests_per_page = 1
    
    total_requests = cities * pages_per_city * requests_per_page
    
    print(f"Cities to search: {cities}")
    print(f"Pages per city: {pages_per_city}")
    print(f"Total API requests needed: {total_requests:,}")
    
    print(f"\nTime estimate (with 2-second delays between pages):")
    print(f"  - API calls: {total_requests:,}")
    print(f"  - Delays: ~{total_requests * 2 / 60:.1f} minutes")
    print(f"  - Total runtime: ~{total_requests * 2 / 3600:.1f} hours")
    
    print(f"\n⚠️  WARNING: This will use {total_requests:,} API requests!")
    print("   Make sure you have sufficient quota available.")

if __name__ == "__main__":
    check_api_usage()
    check_google_cloud_console_info()
    estimate_usage_for_usa_script() 