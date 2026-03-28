import sqlite3
import pandas as pd
import os
import glob
import requests
import zipfile
from io import BytesIO

DB_PATH = "data/ipl.db"


def download_dataset():
    """Download IPL dataset from GitHub"""
    url = "https://github.com/ritesh-ojha/IPL-DATASET/archive/refs/heads/main.zip"
    print("📥 Downloading IPL dataset...")

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with zipfile.ZipFile(BytesIO(response.content)) as z:
                z.extractall("data/raw/")
            print("✅ Dataset downloaded and extracted")
            return True
    except Exception as e:
        print(f"❌ Download failed: {e}")

    return False


def find_csv_files():
    """Find the correct CSV files"""
    base = "data/raw"

    # Look for Match_Info.csv (the file we have)
    match_files = glob.glob(os.path.join(base, "**", "Match_Info.csv"), recursive=True)
    if match_files:
        return match_files[0], None

    # Look for matches.csv as fallback
    match_files = glob.glob(os.path.join(base, "**", "matches.csv"), recursive=True)
    if match_files:
        return match_files[0], None

    return None, None


def load_historical_data():
    """Load historical IPL data into database"""
    conn = sqlite3.connect(DB_PATH)

    # Create tables if they don't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS venues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            city TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season INTEGER,
            match_number INTEGER,
            date TEXT,
            team1_id INTEGER,
            team2_id INTEGER,
            venue_id INTEGER,
            toss_winner_id INTEGER,
            toss_decision TEXT,
            winner_id INTEGER,
            win_type TEXT,
            win_margin INTEGER
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            team_id INTEGER,
            role TEXT,
            price INTEGER
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            player_id INTEGER,
            override_type TEXT,
            new_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Find CSV file
    match_csv, _ = find_csv_files()

    if not match_csv:
        print("📥 No CSV found, downloading...")
        if not download_dataset():
            print("❌ Cannot proceed without data")
            conn.close()
            return

        match_csv, _ = find_csv_files()

    print(f"📄 Loading from: {match_csv}")
    df = pd.read_csv(match_csv)
    print(f"📊 Loaded {len(df)} matches")

    # Insert teams
    print("🏏 Adding teams...")
    all_teams = set()
    for col in ['team1', 'team2', 'toss_winner', 'winner']:
        if col in df.columns:
            all_teams.update(df[col].dropna().unique())

    team_map = {}
    for team in all_teams:
        conn.execute("INSERT OR IGNORE INTO teams (name) VALUES (?)", (team,))
        team_map[team] = conn.execute("SELECT id FROM teams WHERE name = ?", (team,)).fetchone()[0]

    # Insert venues
    print("🏟️ Adding venues...")
    venue_map = {}
    if 'venue' in df.columns:
        for venue in df['venue'].unique():
            city = df[df['venue'] == venue]['city'].iloc[0] if 'city' in df.columns else "India"
            conn.execute("INSERT OR IGNORE INTO venues (name, city) VALUES (?, ?)", (venue, city))
            venue_map[venue] = conn.execute("SELECT id FROM venues WHERE name = ?", (venue,)).fetchone()[0]

    # Insert matches
    print("🏏 Adding matches...")
    count = 0
    winner_count = 0

    for _, row in df.iterrows():
        try:
            team1 = row.get('team1')
            team2 = row.get('team2')
            venue = row.get('venue')

            if not team1 or not team2 or not venue:
                continue

            team1_id = team_map.get(team1)
            team2_id = team_map.get(team2)
            venue_id = venue_map.get(venue)

            if not team1_id or not team2_id or not venue_id:
                continue

            toss_winner = row.get('toss_winner')
            toss_winner_id = team_map.get(toss_winner) if pd.notna(toss_winner) else None

            winner = row.get('winner')
            winner_id = team_map.get(winner) if pd.notna(winner) else None

            if winner_id:
                winner_count += 1

            conn.execute('''
                INSERT OR IGNORE INTO matches 
                (season, match_number, date, team1_id, team2_id, venue_id, 
                 toss_winner_id, toss_decision, winner_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row.get('season'), row.get('match_number', row.get('id')), row.get('date'),
                team1_id, team2_id, venue_id,
                toss_winner_id,
                row.get('toss_decision') if pd.notna(row.get('toss_decision')) else None,
                winner_id
            ))
            count += 1
        except Exception as e:
            continue

    conn.commit()

    # Final check
    total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    total_winners = conn.execute("SELECT COUNT(*) FROM matches WHERE winner_id IS NOT NULL").fetchone()[0]

    print(f"\n{'=' * 50}")
    print(f"✅ Loaded {count} matches")
    print(f"📊 Total matches in DB: {total_matches}")
    print(f"🏆 Matches with winners: {total_winners}")
    print(f"{'=' * 50}")

    conn.close()

    return total_winners > 0


if __name__ == "__main__":
    success = load_historical_data()
    if success:
        print("\n✅ Historical data loaded successfully!")
        print("Now run: python train_real_model.py")
    else:
        print("\n❌ Failed to load historical data")