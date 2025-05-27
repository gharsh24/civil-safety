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

@router.get("/emergency-contacts")
async def get_emergency_contacts_by_location(lat: float, lon: float) -> Dict:
    headers = {"User-Agent": "YourApp/1.0"}

    # Step 1: Get country code using reverse geocoding from Nominatim
    async with httpx.AsyncClient() as client:
        geo_response = await client.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "json",
                "zoom": 3,
                "addressdetails": 1
            },
            headers=headers
        )

        if geo_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to reverse geocode location.")

        country_code = geo_response.json().get("address", {}).get("country_code", "").upper()
        if not country_code:
            raise HTTPException(status_code=404, detail="Could not determine country from coordinates.")

        # Step 2: Use EmergencyNumberAPI to get emergency numbers
        emer_response = await client.get(f"https://emergencynumberapi.com/api/country/{country_code}")
        if emer_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch emergency contacts.")

        emer_data = emer_response.json().get("data", {})

    return {
        "country": emer_data.get("country", {}).get("name", "Unknown"),
        "ISOCode": country_code,
        "emergency_contacts": {
            "ambulance": emer_data.get("ambulance", {}).get("all", []),
            "fire": emer_data.get("fire", {}).get("all", []),
            "police": emer_data.get("police", {}).get("all", []),
            "dispatch": emer_data.get("dispatch", {}).get("all", []),
            "member_112": emer_data.get("member_112", False),
            "localOnly": emer_data.get("localOnly", False),
        }
    }