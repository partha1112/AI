from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

NWS_API_URL = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_requiremts(url: str)-> dict[str, Any] | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }

    async with httpx.AsyncClient() as client :
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()

            return response.json()
        except Exception:
            return None
        
def format_alerts(data):
    alerts = []

    for feature in data.get("features", []):
        p = feature["properties"]

        # Get only the first meaningful line from the description
        summary = ""
        if p.get("description"):
            summary = p["description"].split("\n\n")[0].replace("* WHAT...", "")

        alerts.append({
            "event": p.get("event"),
            "severity": p.get("severity"),
            "area": p.get("areaDesc"),
            "ends": p.get("ends"),
            "summary": summary.strip()
        })

    return alerts
        
@mcp.tool()
async def get_weather_resort(area: str) -> str:
    """Get the weather alert report for a US state code like NY or TX."""

    area = area.strip().upper()
    url = f"{NWS_API_URL}/alerts/active?area={area}"
    response = await make_nws_requiremts(url=url)
    if response is None:
        return "Unable to fetch weather data."
    return str(format_alerts(response))


