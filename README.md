# Virginia Hardware Store Finder

This project helps you find hardware stores across Virginia using the Google Places API.

## Current Issue

The API key in the script is valid, but the **Places API (New)** is not enabled for the project. You need to enable it to use the script.

## Quick Fix

1. **Enable the Places API (New):**
   - Go to: https://console.developers.google.com/apis/api/places.googleapis.com/overview?project=1065797904404
   - Click "Enable" to activate the Places API (New)

2. **Wait a few minutes** for the changes to propagate

3. **Run the script again:**
   ```bash
   python3 find_hardware_stores_v2.py
   ```

## Alternative: Get Your Own API Key

If you prefer to use your own API key:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable these APIs:
   - **Places API (New)** - Required for finding places
   - **Maps JavaScript API** - Optional, for additional features
   - **Geocoding API** - Optional, for address conversion
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Replace the `API_KEY` variable in the script with your new key

## Files in this Project

- `find_hardware_stores.py` - Original script (single location)
- `find_hardware_stores_v2.py` - Enhanced script (multiple Virginia locations)
- `test_api_key.py` - Test script to check API status
- `requirements.txt` - Python dependencies

## How to Run

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Run the main script:
   ```bash
   python3 find_hardware_stores_v2.py
   ```

3. Check results:
   - `virginia_hardware_stores_complete.json` - Complete data
   - `virginia_hardware_stores_summary.txt` - Human-readable summary

## What the Script Does

1. Searches 10 major Virginia cities for hardware stores
2. Collects detailed information for each store:
   - Name and address
   - Phone number
   - Website
   - Rating and reviews
   - Opening hours
3. Removes duplicates
4. Saves results in multiple formats

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

## Expected Output

Once the API is enabled, you should see output like:
```
Searching for hardware stores across Virginia...
============================================================

Searching in Richmond, VA...
Found 15 hardware stores in Richmond, VA
  - Home Depot
    Address: 123 Main St, Richmond, VA
    Phone: (804) 555-0123
    Website: https://www.homedepot.com
    Rating: 4.2

  - Lowe's
    Address: 456 Oak Ave, Richmond, VA
    Phone: (804) 555-0456
    Website: https://www.lowes.com
    Rating: 4.1
...
```

## Troubleshooting

- **"REQUEST_DENIED"**: Enable the Places API (New) in Google Cloud Console
- **"API key not valid"**: Check your API key and make sure it's correct
- **"Quota exceeded"**: You've hit the API usage limits for the day
- **No results**: Try increasing the search radius or adding more locations
