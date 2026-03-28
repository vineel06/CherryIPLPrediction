import sqlite3
import numpy as np
import joblib
import os
from datetime import datetime

DB_PATH = "data/ipl.db"
MODEL_PATH = "model/xgb_model.pkl"

model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)

def get_team_recent_form(team_id, date, conn):
    """Return win percentage in last 5 matches before date."""
    query = """
        SELECT winner_id
        FROM matches
        WHERE (team1_id = ? OR team2_id = ?) AND date < ?
        ORDER BY date DESC
        LIMIT 5
    """
    rows = conn.execute(query, (team_id, team_id, date)).fetchall()
    if not rows:
        return 0.5
    wins = sum(1 for r in rows if r[0] == team_id)
    return wins / len(rows)

def get_head_to_head(team1_id, team2_id, date, conn):
    """Head-to-head win ratio for team1 before date."""
    query = """
        SELECT winner_id
        FROM matches
        WHERE ((team1_id = ? AND team2_id = ?) OR (team1_id = ? AND team2_id = ?)) AND date < ?
    """
    rows = conn.execute(query, (team1_id, team2_id, team2_id, team1_id, date)).fetchall()
    if not rows:
        return 0.5
    wins = sum(1 for r in rows if r[0] == team1_id)
    return wins / len(rows)

def get_venue_avg_score(venue_id, date, conn):
    """Average first innings score at venue before date (simplified)."""
    # We don't have innings scores easily, use dummy for now
    return 165

def get_venue_bat_first_win_pct(venue_id, date, conn):
    """Percentage of matches won by team batting first at venue before date."""
    query = """
        SELECT toss_decision, winner_id, team1_id
        FROM matches
        WHERE venue_id = ? AND date < ? AND winner_id IS NOT NULL AND toss_decision IS NOT NULL
    """
    rows = conn.execute(query, (venue_id, date)).fetchall()
    if not rows:
        return 0.5
    bat_first_wins = 0
    total = 0
    for r in rows:
        if r[0] == 'bat':
            total += 1
            if r[1] == r[2]:  # team1 won (they batted first)
                bat_first_wins += 1
    return bat_first_wins / total if total > 0 else 0.5

def get_toss_impact(team_id, venue_id, date, conn):
    """How often team wins after winning toss at this venue before date."""
    query = """
        SELECT winner_id
        FROM matches
        WHERE toss_winner_id = ? AND venue_id = ? AND date < ?
    """
    rows = conn.execute(query, (team_id, venue_id, date)).fetchall()
    if not rows:
        return 0.5
    wins = sum(1 for r in rows if r[0] == team_id)
    return wins / len(rows)

def predict_match(match_id):
    if model is None:
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    match = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    if not match:
        conn.close()
        return None

    team1 = match['team1_id']
    team2 = match['team2_id']
    venue = match['venue_id']
    date = match['date']
    toss_winner = match['toss_winner_id']
    toss_decision = match['toss_decision']

    # Features (must match training)
    t1_form = get_team_recent_form(team1, date, conn)
    t2_form = get_team_recent_form(team2, date, conn)
    h2h = get_head_to_head(team1, team2, date, conn)
    venue_avg = get_venue_avg_score(venue, date, conn)
    venue_bat_first = get_venue_bat_first_win_pct(venue, date, conn)
    toss_impact1 = get_toss_impact(team1, venue, date, conn)
    toss_impact2 = get_toss_impact(team2, venue, date, conn)
    toss_bat_first = 1 if toss_decision == 'bat' else 0
    toss_team1 = 1 if toss_winner == team1 else 0

    # Dummy values for runs/wickets – we'll need to compute properly later
    t1_avg_runs = 160
    t2_avg_runs = 155
    t1_avg_wickets = 6
    t2_avg_wickets = 5.5

    features = np.array([[
        t1_form,
        t2_form,
        t1_avg_runs,
        t2_avg_runs,
        t1_avg_wickets,
        t2_avg_wickets,
        h2h,
        venue_avg,
        venue_bat_first,
        toss_impact1,
        toss_impact2,
        toss_bat_first,
        toss_team1
    ]])

    prob = model.predict_proba(features)[0]  # prob[0] for team1, prob[1] for team2
    winner = team1 if prob[0] > 0.5 else team2
    # Get team names
    team1_name = conn.execute("SELECT name FROM teams WHERE id = ?", (team1,)).fetchone()[0]
    team2_name = conn.execute("SELECT name FROM teams WHERE id = ?", (team2,)).fetchone()[0]
    winner_name = team1_name if winner == team1 else team2_name
    conn.close()

    return {
        'team1': team1_name,
        'team2': team2_name,
        'prob1': prob[0],
        'prob2': prob[1],
        'winner': winner_name,
        'confidence': max(prob)
    }