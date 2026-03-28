import requests
import json
import os

def fetch_schedule():
    """Fetch upcoming match schedule from free API."""
    # Try the public IPL 2025 API first
    url = "https://ipl-okn0.onrender.com/ipl-2025-schedule"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Save to data/raw/schedule.json
            with open("data/raw/schedule.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Schedule fetched from IPL API.")
            return data
    except Exception as e:
        print(f"IPL API failed: {e}")

    # Fallback: official IPL stats API (example for 2024)
    fallback_url = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/136-matchschedule.js"
    try:
        r = requests.get(fallback_url)
        if r.status_code == 200:
            # The response is JSONP; we need to strip the callback
            text = r.text
            # Remove the callback wrapper: callbackFunc({...})
            json_str = text[text.find('(')+1:text.rfind(')')]
            data = json.loads(json_str)
            with open("data/raw/schedule.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Schedule fetched from official IPL API.")
            return data
    except Exception as e:
        print(f"Official IPL API failed: {e}")

    print("No schedule data could be fetched.")
    return None

if __name__ == "__main__":
    fetch_schedule()