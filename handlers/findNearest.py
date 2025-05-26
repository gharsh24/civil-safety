from fastapi import APIRouter, HTTPException
from typing import List, Dict
import httpx
from models import HelpRequest

router = APIRouter()

@router.post("/find-help")
async def find_help(request: HelpRequest):
    # Parse latitude and longitude from the location string
    try:
        lat_str, lon_str = request.location.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        print("coordinates are ", lat, lon)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid location format. Use 'lat,lon'.")

    # Construct the Nominatim search query
    query = f"{request.help_type} near {lat},{lon}"
    params = {
        "q": query,
        "format": "json",
        "limit": 10,
        "addressdetails": 1
    }
    headers = {"User-Agent": "YourApp/1.0"}

    # Send the request to Nominatim
    async with httpx.AsyncClient() as client:
        response = await client.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
        response.raise_for_status()
        results= response.json()
    
    extracted_results = []
    for item in results:
        extracted_results.append({
            "name": item.get("display_name", "N/A"),
            "latitude": float(item["lat"]),  # Nominatim returns lat/lon as strings
            "longitude": float(item["lon"])
        })
    
    print("response sent ", extracted_results)
    return extracted_results
