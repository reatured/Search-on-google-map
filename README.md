# Virginia Hardware Store Finder

This project helps you find hardware stores across Virginia using the Google Places API.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```
2. **Set up your API key:**
   - Copy `.env.example` to `.env` and add your Google Maps API key.
3. **Run the main script:**
   ```bash
   python3 find_hardware_stores_final.py
   ```
4. **Check results:**
   - `virginia_hardware_stores_final.json` — Complete data
   - `virginia_hardware_stores_final_summary.txt` — Human-readable summary

## Files in this Project

- `find_hardware_stores_final.py` — Main script (multi-city, modern API)
- `test_api_key.py` — Test script to check API status
- `requirements.txt` — Python dependencies
- `.env.example` — Example environment file for your API key

## What the Script Does

- Searches 10 major Virginia cities for hardware stores
- Collects detailed information for each store:
  - Name and address
  - Phone number
  - Website
  - Rating and reviews
  - Opening hours
- Removes duplicates
- Saves results in multiple formats

## Virginia Cities Covered

- Richmond
- Arlington
- Washington DC area
- Norfolk
- Roanoke
- Charlottesville
- Blacksburg
- Harrisonburg
- Winchester
- Lynchburg

## Troubleshooting

- **"REQUEST_DENIED"**: Enable the Places API (New) in Google Cloud Console
- **"API key not valid"**: Check your API key and make sure it's correct
- **"Quota exceeded"**: You've hit the API usage limits for the day
- **No results**: Try increasing the search radius or adding more locations
