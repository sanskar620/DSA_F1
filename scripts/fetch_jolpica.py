import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("JOLPICA_BASE_URL", "https://api.jolpi.ca/ergast/f1")
HEADERS = {"User-Agent": "F1-StrategyIQ/1.0"}
OUTPUT_DIR = os.path.join("data", "raw", "jolpica")

ENDPOINTS = [
    "seasons",
    "races",
    "drivers",
    "constructors",
    # Note: results, pitstops, laps, standings are typically nested under specific races in Ergast/Jolpica
    # We will fetch a subset to avoid massive downloads for now, targeting recent years if possible,
    # or just the top level metadata.
]

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def fetch_with_retry(url, max_retries=3, delay=1.0):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429: # Rate limited
                print(f"Rate limited. Waiting {delay * 5}s...")
                time.sleep(delay * 5)
            else:
                print(f"Error {response.status_code} fetching {url}")
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            time.sleep(delay)
    return None

def fetch_paginated(endpoint, limit=100):
    """Fetches all pages for a given endpoint"""
    offset = 0
    all_data = []
    
    while True:
        url = f"{BASE_URL}/{endpoint}.json?limit={limit}&offset={offset}"
        print(f"Fetching {url}")
        
        data = fetch_with_retry(url)
        if not data:
            break
            
        try:
            # Ergast API structure
            mrdata = data.get("MRData", {})
            total = int(mrdata.get("total", 0))
            
            # The actual table name depends on the endpoint (e.g. SeasonTable, RaceTable)
            # We'll just store the raw MRData
            all_data.append(data)
            
            offset += limit
            if offset >= total:
                break
                
            time.sleep(0.5) # Rate limiting
        except Exception as e:
            print(f"Failed to parse pagination for {endpoint}: {e}")
            break
            
    return all_data

def main():
    ensure_dir(OUTPUT_DIR)
    
    for endpoint in ENDPOINTS:
        endpoint_dir = os.path.join(OUTPUT_DIR, endpoint)
        ensure_dir(endpoint_dir)
        
        cache_file = os.path.join(endpoint_dir, f"{endpoint}_all.json")
        if os.path.exists(cache_file):
            print(f"Skipping {endpoint}, cache already exists.")
            continue
            
        data = fetch_paginated(endpoint)
        if data:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Saved {endpoint} data to {cache_file}")

if __name__ == "__main__":
    main()
