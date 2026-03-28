import sqlite3
import datetime

DB_PATH = "data/ipl.db"

# Map of team names to their IDs (we need to look them up)
TEAMS = {
    "Mumbai Indians": "Mumbai Indians",
    "Chennai Super Kings": "Chennai Super Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bangalore",
    "Kolkata Knight Riders": "Kolkata Knight Riders",
    "Delhi Capitals": "Delhi Capitals",
    "Punjab Kings": "Punjab Kings",
    "Rajasthan Royals": "Rajasthan Royals",
    "Sunrisers Hyderabad": "Sunrisers Hyderabad",
    "Lucknow Super Giants": "Lucknow Super Giants",
    "Gujarat Titans": "Gujarat Titans"
}

# Sample 2026 schedule (first few matches)
SCHEDULE_2026 = [
    {"match_number": 1, "date": "2026-03-28", "team1": "Mumbai Indians", "team2": "Chennai Super Kings", "venue": "Wankhede Stadium, Mumbai", "city": "Mumbai"},
    {"match_number": 2, "date": "2026-03-29", "team1": "Royal Challengers Bangalore", "team2": "Kolkata Knight Riders", "venue": "M. Chinnaswamy Stadium, Bengaluru", "city": "Bengaluru"},
    {"match_number": 3, "date": "2026-03-30", "team1": "Delhi Capitals", "team2": "Punjab Kings", "venue": "Arun Jaitley Stadium, Delhi", "city": "Delhi"},
    {"match_number": 4, "date": "2026-03-31", "team1": "Rajasthan Royals", "team2": "Sunrisers Hyderabad", "venue": "Sawai Mansingh Stadium, Jaipur", "city": "Jaipur"},
    {"match_number": 5, "date": "2026-04-01", "team1": "Lucknow Super Giants", "team2": "Gujarat Titans", "venue": "BRSABV Ekana Cricket Stadium, Lucknow", "city": "Lucknow"},
]

def insert_2026_matches():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get team IDs
    team_ids = {}
    for team_name in TEAMS:
        c.execute("SELECT id FROM teams WHERE name = ?", (team_name,))
        row = c.fetchone()
        if row:
            team_ids[team_name] = row[0]
        else:
            print(f"Team '{team_name}' not found in database. Inserting...")
            c.execute("INSERT INTO teams (name) VALUES (?)", (team_name,))
            team_ids[team_name] = c.lastrowid

    # Get or create venue IDs
    for match in SCHEDULE_2026:
        venue = match['venue']
        city = match['city']
        c.execute("SELECT id FROM venues WHERE name = ?", (venue,))
        row = c.fetchone()
        if row:
            venue_id = row[0]
        else:
            c.execute("INSERT INTO venues (name, city) VALUES (?, ?)", (venue, city))
            venue_id = c.lastrowid

        team1_id = team_ids[match['team1']]
        team2_id = team_ids[match['team2']]

        # Insert match (winner_id NULL because not played yet)
        c.execute('''INSERT INTO matches 
            (season, match_number, date, team1_id, team2_id, venue_id)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (2026, match['match_number'], match['date'], team1_id, team2_id, venue_id))

    conn.commit()
    conn.close()
    print("2026 matches inserted.")

if __name__ == "__main__":
    insert_2026_matches()