# Find Hardware Store Web App

A full-stack web application to search for hardware stores by location using Google Places API. The backend is built with FastAPI (Python), and the frontend is a React app.

---

## 🌐 Web App Quick Start

### 1. Backend Setup (FastAPI)

```bash
cd backend
# (Recommended) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn python-dotenv requests

# Add your Google Maps API key to .env
# Example:
echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env

# Start the backend server
uvicorn main:app --reload
# The API will be available at http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

### 2. Frontend Setup (React)

```bash
cd frontend
npm install  # Only needed the first time
npm start
# The app will open at http://localhost:3000
```

### 3. Usage
- Enter a location (city, address, etc.) in the search box.
- Click "Search" to find hardware stores near that location.
- Results will show name, address, phone, and website (if available).

---

## Project Structure (Full Stack)

```
Find Hardware Store/
├── backend/         # FastAPI backend (API server)
│   ├── main.py      # FastAPI app entry point
│   └── ...
├── frontend/        # React frontend (web UI)
│   ├── src/App.js   # Main React app logic
│   └── ...
├── src/             # Python scripts for batch data collection
├── output/          # Data output from scripts
└── README.md        # (This file)
```

---

# Find Hardware Store

A comprehensive Python project to find hardware stores across different locations using Google Places API. This project includes scripts for searching hardware stores in Virginia, the United States, France, Germany, Washington, and any custom location.

## 📁 Project Structure

```
Find Hardware Store/
├── src/                       # Python source code
│   ├── find_hardware_stores_final.py          # Virginia hardware stores search
│   ├── find_hardware_stores_usa.py            # USA hardware stores search (resume capable)
│   ├── find_hardware_stores_usa_with_emails.py # USA search with email discovery
│   ├── find_hardware_store_by_location.py     # Search any location
│   ├── find_hardware_stores_france.py         # France hardware stores search
│   ├── find_hardware_stores_germany.py        # Germany hardware stores search
│   ├── find_hardware_stores_washington.py     # Washington hardware stores search
│   ├── check_api_usage.py                     # Check API limits and usage
│   └── test_api_key.py                        # Test API key functionality
├── output/                    # Generated output files
│   ├── raw/                   # Machine-readable data
│   │   ├── *.json            # JSON data files
│   │   ├── *.csv             # CSV data files
│   │   └── *_progress_*.json # Progress tracking files
│   └── reports/              # Human-readable reports
│       └── *_summary_*.txt   # Text summary files
├── .env                       # Environment variables (API key)
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd "Find Hardware Store"

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env
```

### 2. Enable Google APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - **Places API (New)** - Required for searching places
   - **Geocoding API** - Required for location search
4. Create API credentials and add to `.env` file

### 3. Run Scripts

#### Search Virginia Hardware Stores
```bash
cd src
python3 find_hardware_stores_final.py
```
**Features:**
- Searches 10 major Virginia cities
- Finds 177+ hardware stores
- Saves incremental CSV data
- Includes all major chains

#### Search Any Location
```bash
cd src
python3 find_hardware_store_by_location.py
```
**Features:**
- Interactive location input
- Geocodes any address/city
- Finds hardware stores within 10km radius
- Includes known chain contact info

#### Search USA with Resume Capability
```bash
cd src
python3 find_hardware_stores_usa.py
```
**Features:**
- Searches 500 US cities (10 per state)
- Excludes major national chains
- Resume capability (stop/continue)
- Up to 60 results per city
- ~1,500 API requests total

#### Search USA with Email Discovery
```bash
cd src
python3 find_hardware_stores_usa_with_emails.py
```
**Features:**
- All features from USA search
- Website scraping for email addresses
- Email pattern generation
- Contact page analysis
- Enhanced CSV with email column

#### Search France Hardware Stores
```bash
cd src
python3 find_hardware_stores_france.py
```
**Features:**
- Searches major French cities
- Focuses on French hardware chains
- Includes Leroy Merlin, Castorama data

#### Search Germany Hardware Stores
```bash
cd src
python3 find_hardware_stores_germany.py
```
**Features:**
- Searches major German cities
- Focuses on German hardware chains
- Comprehensive German market coverage

#### Search Washington Hardware Stores
```bash
cd src
python3 find_hardware_stores_washington.py
```
**Features:**
- Searches Washington state cities
- Regional hardware store focus
- Pacific Northwest coverage

#### Check API Usage
```bash
cd src
python3 check_api_usage.py
```
**Features:**
- Tests API connectivity
- Shows rate limiting info
- Estimates usage for large searches
- Provides Google Cloud Console guidance

#### Test API Key
```bash
cd src
python3 test_api_key.py
```
**Features:**
- Validates API key
- Tests basic functionality
- Troubleshooting tool

## 📊 Output Files

All output files are organized in the `output/` folder:

- **`output/raw/`**: Machine-readable data (JSON, CSV, progress files)
- **`output/reports/`**: Human-readable summaries and reports

### File Types
- **JSON files**: Complete structured data with all store information
- **CSV files**: Spreadsheet-friendly format for analysis
- **Text summaries**: Human-readable summaries with store details
- **Progress files**: Resume capability for long searches

### File Naming Convention
- `{location}_hardware_stores_{timestamp}.json` - Complete data
- `{location}_hardware_stores_{timestamp}.csv` - CSV format
- `{location}_hardware_stores_summary_{timestamp}.txt` - Text summary
- `{location}_search_progress_{timestamp}.json` - Progress tracking

## 🔄 Resume Capability

The USA search scripts support stopping and resuming:
- Press `Ctrl+C` to safely stop
- Run the same command again to resume from where you left off
- Progress is automatically saved after each city
- No data loss during interruption

## 📧 Email Discovery

The enhanced USA script attempts to find email addresses by:
1. **Website scraping**: Extracts emails from business websites
2. **Pattern generation**: Creates likely email addresses based on business names
3. **Contact page analysis**: Searches for contact information pages
4. **Spam filtering**: Removes noreply and automated emails

## 🎯 Features

- **Comprehensive coverage**: Search across multiple cities and states
- **Incremental saving**: Data saved as it's processed
- **Resume capability**: Stop and continue long searches
- **Email discovery**: Find contact emails for businesses
- **Duplicate prevention**: Avoid duplicate stores across searches
- **Major chain filtering**: Focus on independent hardware stores
- **Progress tracking**: Real-time progress updates
- **Multi-country support**: USA, France, Germany, Washington
- **Flexible search**: Any location worldwide

## 📋 Requirements

- Python 3.7+
- Google Places API key
- Internet connection
- Required packages: `requests`, `python-dotenv`

## ⚠️ API Limits

- **Free tier**: ~1,000 requests per day
- **Paid tier**: Higher limits available
- **Rate limiting**: 100 requests per 100 seconds
- **USA search**: Requires ~1,500 API requests
- **Virginia search**: Requires ~100 API requests
- **Location search**: Requires ~50 API requests

## 📝 Usage Examples

### Quick Virginia Search
```bash
cd src
python3 find_hardware_stores_final.py
# Results: 177+ hardware stores across Virginia
```

### Custom Location Search
```bash
cd src
python3 find_hardware_store_by_location.py
# Enter: "San Francisco, CA"
# Results: Hardware stores in San Francisco area
```

### Large USA Search (with resume)
```bash
cd src
python3 find_hardware_stores_usa.py
# Can be stopped with Ctrl+C and resumed later
# Results: Thousands of independent hardware stores
```

### USA Search with Emails
```bash
cd src
python3 find_hardware_stores_usa_with_emails.py
# Includes email discovery for each store
# Results: Hardware stores with contact emails
```

## 🔧 Troubleshooting

### Common Issues
- **"REQUEST_DENIED"**: Enable Places API (New) in Google Cloud Console
- **"API key not valid"**: Check your API key in .env file
- **"Quota exceeded"**: You've hit daily API limits
- **No results**: Try increasing search radius or different location

### API Setup Help
```bash
cd src
python3 test_api_key.py
python3 check_api_usage.py
```

## 🎯 Notes

- All scripts run from the `src/` directory
- Output files are automatically saved to `output/` directory
- API key must be enabled for Places API (New)
- Long searches can be safely interrupted and resumed
- Email discovery may take longer but provides valuable contact data
- Each script is optimized for its specific use case

## 🎯 Data Analysis

The generated CSV files can be used for:
- **Market research**: Analyze hardware store distribution
- **Competitive analysis**: Find local competitors
- **Business development**: Identify underserved areas
- **Contact database**: Email marketing campaigns
- **Geographic analysis**: Store location patterns
