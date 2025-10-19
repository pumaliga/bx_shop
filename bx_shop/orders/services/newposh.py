import requests
from django.core.cache import cache


API_KEY = "06603b5df7cd68b4b180b003c08ce901"
BASE_URL = "https://api.novaposhta.ua/v2.0/json/"


def get_warehouses_by_city(city_name):
    """
    Get list of warehouses (branches) by city name with caching.
    """
    # Create cache key from city name
    cache_key = f"nova_poshta_warehouses_{city_name.lower().strip()}"

    # Try to get from cache first
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    # If not in cache, make API call
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {
            "CityName": city_name,
            "Language": "UA"
        }
    }

    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                warehouses = data["data"]
                # Check if any warehouses were found
                if not warehouses:
                    return {"error": f"No warehouses found for city '{city_name}'. Please check the city name."}

                # Cache successful response for 24 hours
                cache.set(cache_key, warehouses, 60 * 60 * 24)
                return warehouses
            else:
                return {"error": data.get("errors")}
        else:
            return {"error": "Failed to connect to Nova Poshta API"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


def get_city_ref_by_name(city_name):
    """
    Get city reference by city name with caching.
    """
    # Create cache key from city name
    cache_key = f"nova_poshta_city_ref_{city_name.lower().strip()}"
    print(city_name)
    # Try to get from cache first
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        print(f"Cache for {city_name.lower().strip()}")
        return cached_data

    # If not in cache, make API call
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address", 
        "calledMethod": "getCities",
        "methodProperties": {
            "FindByString": city_name,
            "Limit": 1
        }
    }

    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(data)
            if data.get("success") and data["data"]:
                city_ref = data["data"][0]["Ref"]
                # Cache successful response for 24 hours
                cache.set(cache_key, city_ref, 60 * 60 * 24)
                return city_ref
            else:
                return {"error": f"City '{city_name}' not found"}
        else:
            return {"error": "Failed to connect to Nova Poshta API"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


def get_streets_by_city_ref(city_ref, query):
    """
    Get a list of streets by CityRef and search query with caching.
    """
    # Create cache key from city_ref and query
    cache_key = f"nova_poshta_streets_{city_ref}_{query.lower().strip()}"
    
    # Try to get from cache first
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    # If not in cache, make API call
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getStreet",
        "methodProperties": {
            "CityRef": city_ref,
            "FindByString": query,
            "Limit": 20
        }
    }

    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                streets = data["data"]
                # Check if any streets were found
                if not streets:
                    return {"error": f"No streets found matching '{query}'. Please check the spelling."}
                
                # Cache successful response for 1 hour (streets change less frequently)
                cache.set(cache_key, streets, 60 * 60)
                return streets
            else:
                # Don't cache errors - return immediately
                return {"error": data.get("errors")}
        else:
            return {"error": "Failed to connect to Nova Poshta API"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
