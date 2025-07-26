import os
import time
from typing import List, Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is required")

PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
if not PERPLEXITY_API_KEY:
    print("Warning: PERPLEXITY_API_KEY not set. AI features will be disabled.")

# Initialize Perplexity client (OpenAI-compatible)
perplexity_client = None
if PERPLEXITY_API_KEY and PERPLEXITY_API_KEY != 'your_perplexity_api_key_here':
    perplexity_client = OpenAI(
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai"
    )

GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
PLACES_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

class Store(BaseModel):
    name: str
    address: str
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    place_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SearchResponse(BaseModel):
    location: str
    stores: List[Store]

class CompanyAnalysisRequest(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    website: Optional[str] = None
    language: Optional[str] = "english"

class ProductCategory(BaseModel):
    name: str
    description: str
    potential_products: List[str]
    market_links: Optional[List[str]] = None

class CompanyAnalysisResponse(BaseModel):
    basicInfo: dict
    analysisPoints: List[str]
    nextSteps: List[str]
    productCategories: List[ProductCategory]
    perplexityAnalysis: str

class EmailGenerationRequest(BaseModel):
    store: dict
    analysis: Optional[dict] = None
    language: Optional[str] = "english"

class EmailGenerationResponse(BaseModel):
    subject: str
    body: str

app = FastAPI(
    title="Hardware Store Finder API",
    description="Search for hardware stores using Google Places API."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/search",
    response_model=SearchResponse,
    summary="Search hardware stores by location",
    tags=["Search"]
)
def search_hardware_stores(
    location: str = Query(
        ..., 
        description="Address, city, or place to search for hardware stores"
    )
):
    """
    Search for hardware stores near a given location using the Google Places API.
    Returns a list of stores with name, address, website, and phone number.
    """
    try:
        lat, lng = _geocode_location(location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Geocoding API request failed: {e}")

    try:
        all_results = _search_nearby_stores(lat, lng)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Places API request failed: {e}")
    
    if not all_results:
        return SearchResponse(location=location, stores=[])

    stores = _get_store_details(all_results)
    return SearchResponse(location=location, stores=stores)


@app.get(
    "/search/stream",
    summary="Stream hardware stores by location",
    tags=["Search"]
)
def stream_hardware_stores(
    location: str = Query(
        ..., 
        description="Address, city, or place to search for hardware stores"
    )
):
    """
    Stream hardware stores as they are found and processed.
    Returns stores one by one as JSON objects separated by newlines.
    """
    def generate():
        try:
            lat, lng = _geocode_location(location)
        except ValueError as e:
            yield f'data: {{"error": "Geocoding failed: {str(e)}"}}\n\n'
            return
        except requests.RequestException as e:
            yield f'data: {{"error": "Geocoding API request failed: {str(e)}"}}\n\n'
            return

        try:
            all_results = _search_nearby_stores(lat, lng)
        except requests.RequestException as e:
            yield f'data: {{"error": "Places API request failed: {str(e)}"}}\n\n'
            return
        
        if not all_results:
            yield f'data: {{"location": "{location}", "stores": [], "completed": true}}\n\n'
            return

        # Send initial response with location
        yield f'data: {{"location": "{location}", "total_found": {len(all_results)}}}\n\n'
        
        # Stream stores as they're processed
        for i, store in enumerate(all_results):
            store_data = _get_single_store_details(store)
            if store_data:
                result = {
                    "store": store_data.dict(),
                    "index": i + 1,
                    "total": len(all_results)
                }
                yield f'data: {json.dumps(result)}\n\n'
        
        # Send completion signal
        yield f'data: {{"completed": true}}\n\n'

    return StreamingResponse(generate(), media_type="text/plain")


@app.post(
    "/api/analyze-company",
    response_model=CompanyAnalysisResponse,
    summary="Analyze hardware store company information",
    tags=["AI Analysis"]
)
async def analyze_company(request: CompanyAnalysisRequest):
    """
    Analyze a hardware store company using Perplexity AI to get:
    - Product categories and potential products
    - Market analysis and insights
    - Business recommendations
    """
    if not perplexity_client:
        raise HTTPException(
            status_code=503, 
            detail="AI analysis service is not available. Please check PERPLEXITY_API_KEY configuration."
        )
    
    try:
        # Create comprehensive prompt for Perplexity
        if request.language == "chinese":
            prompt = f"""
            请分析位于 {request.address} 的五金店 "{request.name}"。
            {f"电话: {request.phone}" if request.phone else ""}
            {f"网站: {request.website}" if request.website else ""}
            
            请提供以下信息：
            1. 公司概况和市场地位
            2. 他们可能经营的主要产品类别
            3. 具体的潜在产品，如果可能的话提供市场链接
            4. 商业见解和合作机会
            5. 当地市场竞争分析
            
            重点关注对寻求与他们合作的五金供应商的可行见解。
            包括具体的产品类别，如工具、紧固件、建材等。
            如果有的话，请提供市场研究链接。
            
            请用中文回答。
            """
        else:
            prompt = f"""
            Analyze the hardware store "{request.name}" located at {request.address}.
            {f"Phone: {request.phone}" if request.phone else ""}
            {f"Website: {request.website}" if request.website else ""}
            
            Please provide:
            1. Company overview and market position
            2. Main product categories they likely carry
            3. Specific potential products with market links where possible
            4. Business insights and partnership opportunities
            5. Competitive analysis in their local market
            
            Focus on actionable insights for a hardware supplier looking to partner with them.
            Include specific product categories like tools, fasteners, building materials, etc.
            Provide market research links where available.
            """
        
        # Call Perplexity API
        response = perplexity_client.chat.completions.create(
            model="sonar",
            messages=[
                {
                    "role": "system",
                    "content": "You are a business analyst specializing in hardware retail market analysis. Provide detailed, actionable insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.2
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse and structure the response
        analysis_response = CompanyAnalysisResponse(
            basicInfo={
                "name": request.name,
                "address": request.address,
                "phone": request.phone,
                "website": request.website
            },
            analysisPoints=[],
            nextSteps=[],
            productCategories=[],
            perplexityAnalysis=analysis_text or "AI analysis completed successfully."
        )
        
        return analysis_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing company: {str(e)}"
        )


@app.post(
    "/api/generate-email",
    response_model=EmailGenerationResponse,
    summary="Generate cold email for hardware store outreach",
    tags=["AI Analysis"]
)
async def generate_email(request: EmailGenerationRequest):
    """
    Generate a personalized cold email for reaching out to a hardware store.
    Uses AI to create contextual, professional outreach emails.
    """
    if not perplexity_client:
        raise HTTPException(
            status_code=503,
            detail="AI email generation service is not available. Please check PERPLEXITY_API_KEY configuration."
        )
    
    try:
        store_info = request.store
        analysis_info = request.analysis.get('perplexityAnalysis', '') if request.analysis else ''
        
        # Create prompt for email generation
        if request.language == "chinese":
            prompt = f"""
            为以下五金店生成一封专业的商务合作邮件：
            
            店铺信息：
            - 名称: {store_info.get('name', 'N/A')}
            - 地址: {store_info.get('address', 'N/A')}
            - 电话: {store_info.get('phone', 'N/A')}
            - 网站: {store_info.get('website', 'N/A')}
            
            {"市场分析信息：" + analysis_info if analysis_info else ""}
            
            请生成：
            1. 邮件主题（简洁且吸引人）
            2. 邮件正文（专业、个性化、突出合作价值）
            
            发件人背景：James Hardware是一家成立于1995年的家族五金制造出口公司，专业生产家居装饰五金产品。
            
            请用中文回复，格式如下：
            主题：[邮件主题]
            
            正文：
            [邮件正文内容]
            """
        else:
            prompt = f"""
            Generate a professional cold email for reaching out to the following hardware store:
            
            Store Information:
            - Name: {store_info.get('name', 'N/A')}
            - Address: {store_info.get('address', 'N/A')}
            - Phone: {store_info.get('phone', 'N/A')}
            - Website: {store_info.get('website', 'N/A')}
            
            {"Market Analysis: " + analysis_info if analysis_info else ""}
            
            Generate:
            1. Email subject line (concise and compelling)
            2. Email body (professional, personalized, value-focused)
            
            Sender Background: James Hardware is a family-owned hardware manufacturing and export company established in 1995, specializing in high-quality home decoration hardware products.
            
            Format your response as:
            Subject: [email subject]
            
            Body:
            [email body content]
            """
        
        # Call Perplexity API for email generation
        response = perplexity_client.chat.completions.create(
            model="sonar",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional business communication specialist. Generate personalized, compelling cold emails for B2B hardware partnerships."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        email_content = response.choices[0].message.content
        
        # Parse subject and body from AI response
        try:
            if "Subject:" in email_content and "Body:" in email_content:
                parts = email_content.split("Body:", 1)
                subject = parts[0].replace("Subject:", "").strip()
                body = parts[1].strip()
            elif "主题：" in email_content and "正文：" in email_content:
                parts = email_content.split("正文：", 1)
                subject = parts[0].replace("主题：", "").strip()
                body = parts[1].strip()
            else:
                # Fallback: use first line as subject, rest as body
                lines = email_content.strip().split('\n', 1)
                subject = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else email_content
        except:
            # Ultimate fallback
            subject = f"Partnership Opportunity with {store_info.get('name', 'Your Hardware Store')}"
            body = email_content
        
        return EmailGenerationResponse(
            subject=subject,
            body=body
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating email: {str(e)}"
        )


def _geocode_location(location: str) -> tuple[float, float]:
    """Geocode a location string to lat/lng coordinates."""
    geo_params = {'address': location, 'key': API_KEY}
    geo_resp = requests.get(GEOCODE_URL, params=geo_params, timeout=10)
    geo_resp.raise_for_status()
    
    geo_data = geo_resp.json()
    if geo_data.get('status') != 'OK' or not geo_data.get('results'):
        raise ValueError(f"Geocoding failed: {geo_data.get('status')}")
    
    loc = geo_data['results'][0]['geometry']['location']
    return loc['lat'], loc['lng']


def _search_nearby_stores(lat: float, lng: float) -> List[dict]:
    """Search for nearby hardware stores using Google Places API."""
    params = {
        'location': f'{lat},{lng}',
        'radius': 10000,
        'type': 'hardware_store',
        'key': API_KEY
    }
    
    all_results = []
    next_page_token = None
    
    while True:
        if next_page_token:
            params['pagetoken'] = next_page_token
            time.sleep(2)  # Required delay for pagination
        
        resp = requests.get(PLACES_URL, params=params, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        if data.get('status') not in ['OK', 'ZERO_RESULTS']:
            raise requests.RequestException(f"Places API error: {data.get('status')}")
        
        results = data.get('results', [])
        all_results.extend(results)
        
        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break
    
    return all_results


def _get_store_details(stores_data: List[dict]) -> List[Store]:
    """Get detailed information for each store."""
    stores = []
    
    for store in stores_data:
        store_data = _get_single_store_details(store)
        if store_data:
            stores.append(store_data)
    
    return stores


def _get_single_store_details(store: dict) -> Optional[Store]:
    """Get detailed information for a single store."""
    name = store.get('name', 'N/A')
    place_id = store.get('place_id')
    
    if not place_id:
        return None
    
    details_params = {
        'place_id': place_id,
        'fields': 'name,formatted_phone_number,website,formatted_address,international_phone_number',
        'key': API_KEY
    }
    
    try:
        details_resp = requests.get(DETAILS_URL, params=details_params, timeout=10)
        details_resp.raise_for_status()
        details = details_resp.json().get('result', {})
    except requests.RequestException:
        details = {}
    
    return Store(
        name=name,
        address=details.get('formatted_address', store.get('vicinity', 'N/A')),
        website=details.get('website'),
        phone=(
            details.get('formatted_phone_number') or 
            details.get('international_phone_number')
        ),
        email=None,
        place_id=place_id,
        latitude=store.get('geometry', {}).get('location', {}).get('lat'),
        longitude=store.get('geometry', {}).get('location', {}).get('lng')
    )