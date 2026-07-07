import os, airportsdata, requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
BASE_URL = "http://api.aviationstack.com/v1/flights"

AIRPORTS = airportsdata.load("IATA")

COUNRTY_ALiAS = {
    "usa" : "US",
    "UAE" : "UAE",
    "uk" : "UK",
    "england" : "UK",
    "scotland" : "UK",
    "wales" : "UK",
    "northern ireland" : "UK",
    "ireland" : "IRL",
    "france" : "FR",
    "germany" : "DE",
    "spain" : "ES",
    "italy" : "IT",
    "portugal" : "PT",
    "india" : "IN",
    "china" : "CN",
    "japan" : "JP",
    "korea" : "KR",
    "russia" : "RU",
    "brazil" : "BR",
    "canada" : "CA",
    "australia" : "AU",
    "new zealand" : "NZ",
    "south africa" : "ZA",
    "south korea" : "KR",
    "south sudan" : "SS",
    "sudan" : "SD"
}

MAIN_AIRPORTS = {
    "US" : "JFK",
    "IN" : "DEL",
    "AE" : "DXB",
    "UK" : "LHR",
    "IRL" : "DUB",
    "FR" : "PAR",
    "DE" : "BER",
    "ES" : "MAD",
    "IT" : "ROM",
    "PT" : "LIS",
    "CN" : "PEK",
    "JP" : "NRT",
    "KR" : "ICN",
    "RU" : "MOW",
    "BR" : "SAO",
    "CA" : "YYZ",
    "AU" : "SYD",
    "NZ" : "AKL",
    "ZA" : "JNB",
    "SS" : "JUBA",
    "SD" : "KRT"
}

def search_flights(origin:str, destination:str):
    try:
        country_origin = COUNRTY_ALiAS.get(origin.lower(), origin)
        country_destination = COUNRTY_ALiAS.get(destination.lower(), destination)
        if country_origin not in MAIN_AIRPORTS or country_destination not in MAIN_AIRPORTS:
            return "Invalid origin or destination"
        origin_airport = MAIN_AIRPORTS[country_origin]
        destination_airport = MAIN_AIRPORTS[country_destination]
        params = {
            "access_key" : API_KEY,
            "flight_status" : "active",
            "limit" : 100,
            "offset" : 0,
            "origin" : origin_airport,
            "destination" : destination_airport
        }
        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return str(e)