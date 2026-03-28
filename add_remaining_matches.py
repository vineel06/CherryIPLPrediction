import sqlite3
import csv
import os
from datetime import datetime

DB_PATH = "data/ipl.db"

# Mapping of full venue names from your schedule to your database format
VENUE_MAPPING = {
    "M Chinnaswamy Stadium, Bengaluru": ("M.Chinnaswamy Stadium, Bengaluru", "Bengaluru"),
    "Wankhede Stadium, Mumbai": ("Wankhede Stadium, Mumbai", "Mumbai"),
    "ACA Stadium, Guwahati": ("Barsapara Stadium, Guwahati", "Guwahati"),
    "New International Cricket Stadium, New Chandigarh": (
        "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh", "New Chandigarh"),
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow": ("BRSABV Ekana Cricket Stadium, Lucknow",
                                                                              "Lucknow"),
    "Eden Gardens, Kolkata": ("Eden Gardens, Kolkata", "Kolkata"),
    "MA Chidambaram Stadium, Chennai": ("MA Chidambaram Stadium, Chennai", "Chennai"),
    "Arun Jaitley Stadium, Delhi": ("Arun Jaitley Stadium, Delhi", "Delhi"),
    "Narendra Modi Stadium, Ahmedabad": ("Narendra Modi Stadium, Ahmedabad", "Ahmedabad"),
    "Rajiv Gandhi International Stadium, Hyderabad": ("Rajiv Gandhi International Stadium, Hyderabad", "Hyderabad"),
    "Sawai Mansingh Stadium, Jaipur": ("Sawai Mansingh Stadium, Jaipur", "Jaipur"),
    "Shaheed Veer Narayan Singh International Cricket Stadium, Raipur": (
        "Shaheed Veer Narayan Singh International Stadium, Raipur", "Raipur"),
    "Himachal Pradesh Cricket Association Stadium, Dharamshala": (
        "Himachal Pradesh Cricket Association Stadium, Dharamsala", "Dharamsala"),
}

# All remaining league matches (21-70) - NO PLAYOFFS
REMAINING_MATCHES = [
    # Match 21
    {"match_number": 21, "date": "2026-04-13", "team1": "Sunrisers Hyderabad", "team2": "Rajasthan Royals",
     "venue": "Rajiv Gandhi International Stadium, Hyderabad"},
    # Match 22
    {"match_number": 22, "date": "2026-04-14", "team1": "Chennai Super Kings", "team2": "Kolkata Knight Riders",
     "venue": "MA Chidambaram Stadium, Chennai"},
    # Match 23
    {"match_number": 23, "date": "2026-04-15", "team1": "Royal Challengers Bengaluru", "team2": "Lucknow Super Giants",
     "venue": "M Chinnaswamy Stadium, Bengaluru"},
    # Match 24
    {"match_number": 24, "date": "2026-04-16", "team1": "Mumbai Indians", "team2": "Punjab Kings",
     "venue": "Wankhede Stadium, Mumbai"},
    # Match 25
    {"match_number": 25, "date": "2026-04-17", "team1": "Gujarat Titans", "team2": "Kolkata Knight Riders",
     "venue": "Narendra Modi Stadium, Ahmedabad"},
    # Match 26
    {"match_number": 26, "date": "2026-04-18", "team1": "Royal Challengers Bengaluru", "team2": "Delhi Capitals",
     "venue": "M Chinnaswamy Stadium, Bengaluru"},
    # Match 27
    {"match_number": 27, "date": "2026-04-18", "team1": "Sunrisers Hyderabad", "team2": "Chennai Super Kings",
     "venue": "Rajiv Gandhi International Stadium, Hyderabad"},
    # Match 28
    {"match_number": 28, "date": "2026-04-19", "team1": "Kolkata Knight Riders", "team2": "Rajasthan Royals",
     "venue": "Eden Gardens, Kolkata"},
    # Match 29
    {"match_number": 29, "date": "2026-04-19", "team1": "Punjab Kings", "team2": "Lucknow Super Giants",
     "venue": "New International Cricket Stadium, New Chandigarh"},
    # Match 30
    {"match_number": 30, "date": "2026-04-20", "team1": "Gujarat Titans", "team2": "Mumbai Indians",
     "venue": "Narendra Modi Stadium, Ahmedabad"},
    # Match 31
    {"match_number": 31, "date": "2026-04-21", "team1": "Sunrisers Hyderabad", "team2": "Delhi Capitals",
     "venue": "Rajiv Gandhi International Stadium, Hyderabad"},
    # Match 32
    {"match_number": 32, "date": "2026-04-22", "team1": "Lucknow Super Giants", "team2": "Rajasthan Royals",
     "venue": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow"},
    # Match 33
    {"match_number": 33, "date": "2026-04-23", "team1": "Mumbai Indians", "team2": "Chennai Super Kings",
     "venue": "Wankhede Stadium, Mumbai"},
    # Match 34
    {"match_number": 34, "date": "2026-04-24", "team1": "Royal Challengers Bengaluru", "team2": "Gujarat Titans",
     "venue": "M Chinnaswamy Stadium, Bengaluru"},
    # Match 35
    {"match_number": 35, "date": "2026-04-25", "team1": "Delhi Capitals", "team2": "Punjab Kings",
     "venue": "Arun Jaitley Stadium, Delhi"},
    # Match 36
    {"match_number": 36, "date": "2026-04-25", "team1": "Rajasthan Royals", "team2": "Sunrisers Hyderabad",
     "venue": "Sawai Mansingh Stadium, Jaipur"},
    # Match 37
    {"match_number": 37, "date": "2026-04-26", "team1": "Gujarat Titans", "team2": "Chennai Super Kings",
     "venue": "Narendra Modi Stadium, Ahmedabad"},
    # Match 38
    {"match_number": 38, "date": "2026-04-26", "team1": "Lucknow Super Giants", "team2": "Kolkata Knight Riders",
     "venue": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow"},
    # Match 39
    {"match_number": 39, "date": "2026-04-27", "team1": "Delhi Capitals", "team2": "Royal Challengers Bengaluru",
     "venue": "Arun Jaitley Stadium, Delhi"},
    # Match 40
    {"match_number": 40, "date": "2026-04-28", "team1": "Punjab Kings", "team2": "Rajasthan Royals",
     "venue": "New International Cricket Stadium, New Chandigarh"},
    # Match 41
    {"match_number": 41, "date": "2026-04-29", "team1": "Mumbai Indians", "team2": "Sunrisers Hyderabad",
     "venue": "Wankhede Stadium, Mumbai"},
    # Match 42
    {"match_number": 42, "date": "2026-04-30", "team1": "Gujarat Titans", "team2": "Royal Challengers Bengaluru",
     "venue": "Narendra Modi Stadium, Ahmedabad"},
    # Match 43
    {"match_number": 43, "date": "2026-05-01", "team1": "Rajasthan Royals", "team2": "Delhi Capitals",
     "venue": "Sawai Mansingh Stadium, Jaipur"},
    # Match 44
    {"match_number": 44, "date": "2026-05-02", "team1": "Chennai Super Kings", "team2": "Mumbai Indians",
     "venue": "MA Chidambaram Stadium, Chennai"},
    # Match 45
    {"match_number": 45, "date": "2026-05-03", "team1": "Sunrisers Hyderabad", "team2": "Kolkata Knight Riders",
     "venue": "Rajiv Gandhi International Stadium, Hyderabad"},
    # Match 46
    {"match_number": 46, "date": "2026-05-03", "team1": "Gujarat Titans", "team2": "Punjab Kings",
     "venue": "Narendra Modi Stadium, Ahmedabad"},
    # Match 47
    {"match_number": 47, "date": "2026-05-04", "team1": "Mumbai Indians", "team2": "Lucknow Super Giants",
     "venue": "Wankhede Stadium, Mumbai"},
    # Match 48
    {"match_number": 48, "date": "2026-05-05", "team1": "Delhi Capitals", "team2": "Chennai Super Kings",
     "venue": "Arun Jaitley Stadium, Delhi"},
    # Match 49
    {"match_number": 49, "date": "2026-05-06", "team1": "Sunrisers Hyderabad", "team2": "Punjab Kings",
     "venue": "Rajiv Gandhi International Stadium, Hyderabad"},
    # Match 50
    {"match_number": 50, "date": "2026-05-07", "team1": "Lucknow Super Giants", "team2": "Royal Challengers Bengaluru",
     "venue": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow"},
    # Match 51
    {"match_number": 51, "date": "2026-05-08", "team1": "Delhi Capitals", "team2": "Kolkata Knight Riders",
     "venue": "Arun Jaitley Stadium, Delhi"},
    # Match 52
    {"match_number": 52, "date": "2026-05-09", "team1": "Rajasthan Royals", "team2": "Gujarat Titans",
     "venue": "Sawai Mansingh Stadium, Jaipur"},
    # Match 53
    {"match_number": 53, "date": "2026-05-10", "team1": "Chennai Super Kings", "team2": "Lucknow Super Giants",
     "venue": "MA Chidambaram Stadium, Chennai"},
    # Match 54
    {"match_number": 54, "date": "2026-05-10", "team1": "Royal Challengers Bengaluru", "team2": "Mumbai Indians",
     "venue": "Shaheed Veer Narayan Singh International Cricket Stadium, Raipur"},
    # Match 55
    {"match_number": 55, "date": "2026-05-11", "team1": "Punjab Kings", "team2": "Delhi Capitals",
     "venue": "Himachal Pradesh Cricket Association Stadium, Dharamshala"},
    # Match 56
    {"match_number": 56, "date": "2026-05-12", "team1": "Gujarat Titans", "team2": "Sunrisers Hyderabad",
     "venue": "Narendra Modi Stadium, Ahmedabad"},
    # Match 57
    {"match_number": 57, "date": "2026-05-13", "team1": "Royal Challengers Bengaluru", "team2": "Kolkata Knight Riders",
     "venue": "Shaheed Veer Narayan Singh International Cricket Stadium, Raipur"},
    # Match 58
    {"match_number": 58, "date": "2026-05-14", "team1": "Punjab Kings", "team2": "Mumbai Indians",
     "venue": "Himachal Pradesh Cricket Association Stadium, Dharamshala"},
    # Match 59
    {"match_number": 59, "date": "2026-05-15", "team1": "Lucknow Super Giants", "team2": "Chennai Super Kings",
     "venue": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow"},
    # Match 60
    {"match_number": 60, "date": "2026-05-16", "team1": "Kolkata Knight Riders", "team2": "Gujarat Titans",
     "venue": "Eden Gardens, Kolkata"},
    # Match 61
    {"match_number": 61, "date": "2026-05-17", "team1": "Punjab Kings", "team2": "Royal Challengers Bengaluru",
     "venue": "Himachal Pradesh Cricket Association Stadium, Dharamshala"},
    # Match 62
    {"match_number": 62, "date": "2026-05-17", "team1": "Delhi Capitals", "team2": "Rajasthan Royals",
     "venue": "Arun Jaitley Stadium, Delhi"},
    # Match 63
    {"match_number": 63, "date": "2026-05-18", "team1": "Chennai Super Kings", "team2": "Sunrisers Hyderabad",
     "venue": "MA Chidambaram Stadium, Chennai"},
    # Match 64
    {"match_number": 64, "date": "2026-05-19", "team1": "Rajasthan Royals", "team2": "Lucknow Super Giants",
     "venue": "Sawai Mansingh Stadium, Jaipur"},
    # Match 65
    {"match_number": 65, "date": "2026-05-20", "team1": "Kolkata Knight Riders", "team2": "Mumbai Indians",
     "venue": "Eden Gardens, Kolkata"},
    # Match 66
    {"match_number": 66, "date": "2026-05-21", "team1": "Chennai Super Kings", "team2": "Gujarat Titans",
     "venue": "MA Chidambaram Stadium, Chennai"},
    # Match 67
    {"match_number": 67, "date": "2026-05-22", "team1": "Sunrisers Hyderabad", "team2": "Royal Challengers Bengaluru",
     "venue": "Rajiv Gandhi International Stadium, Hyderabad"},
    # Match 68
    {"match_number": 68, "date": "2026-05-23", "team1": "Lucknow Super Giants", "team2": "Punjab Kings",
     "venue": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow"},
    # Match 69
    {"match_number": 69, "date": "2026-05-24", "team1": "Mumbai Indians", "team2": "Rajasthan Royals",
     "venue": "Wankhede Stadium, Mumbai"},
    # Match 70
    {"match_number": 70, "date": "2026-05-24", "team1": "Kolkata Knight Riders", "team2": "Delhi Capitals",
     "venue": "Eden Gardens, Kolkata"},
]


def get_or_create_team(c, team_name):
    """Get team ID, create if doesn't exist"""
    c.execute("SELECT id FROM teams WHERE name = ?", (team_name,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO teams (name) VALUES (?)", (team_name,))
        return c.lastrowid


def get_or_create_venue(c, venue_name_input):
    """Get venue ID from mapped name, create if doesn't exist"""
    if venue_name_input in VENUE_MAPPING:
        venue_name, city = VENUE_MAPPING[venue_name_input]
    else:
        venue_name = venue_name_input
        city = "India"

    c.execute("SELECT id FROM venues WHERE name = ?", (venue_name,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO venues (name, city) VALUES (?, ?)", (venue_name, city))
        return c.lastrowid


def add_matches():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Add remaining league matches (21-70)
    for match in REMAINING_MATCHES:
        team1_id = get_or_create_team(c, match['team1'])
        team2_id = get_or_create_team(c, match['team2'])
        venue_id = get_or_create_venue(c, match['venue'])

        c.execute('''
            INSERT OR IGNORE INTO matches 
            (season, match_number, date, team1_id, team2_id, venue_id)
            VALUES (2026, ?, ?, ?, ?, ?)
        ''', (match['match_number'], match['date'], team1_id, team2_id, venue_id))

    conn.commit()
    conn.close()
    print(f"✅ Added {len(REMAINING_MATCHES)} league matches successfully!")
    print(
        f"Total matches in database: {len(REMAINING_MATCHES) + 20} (20 original + {len(REMAINING_MATCHES)} new league matches)")


if __name__ == "__main__":
    add_matches()