import os
import sqlite3
from .fetch_historical import download_historical
from .fetch_schedule import fetch_schedule
from ..model.features import build_training_features
from ..model.train import train
import subprocess

def update_all():
    print("Starting data update...")
    download_historical()
    fetch_schedule()

    # Repopulate database from CSVs? That would be heavy. Instead, we'll just update new matches.
    # For simplicity, we'll just rebuild the entire DB once a week.
    # But we'll skip for now.

    # Rebuild features and retrain (optional, maybe run weekly)
    # We can check if it's Sunday, etc.
    print("Rebuilding features...")
    conn = sqlite3.connect("data/ipl.db")
    X, y = build_training_features(conn)
    np.save("data/processed/X.npy", X)
    np.save("data/processed/y.npy", y)
    conn.close()
    print("Retraining model...")
    train()
    print("Update complete.")