import os
import requests
import zipfile
from io import BytesIO

def download_historical():
    """Download IPL matches and deliveries CSV from GitHub."""
    url = "https://github.com/ritesh-ojha/IPL-DATASET/archive/refs/heads/main.zip"
    print("Downloading historical data...")
    r = requests.get(url)
    if r.status_code == 200:
        z = zipfile.ZipFile(BytesIO(r.content))
        z.extractall("data/raw/")
        print("Historical data downloaded and extracted.")
    else:
        print("Failed to download historical data.")

if __name__ == "__main__":
    download_historical()