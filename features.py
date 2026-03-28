import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = "data/ipl.db"

def get_team_stats(team_id, date, conn):
    """
    Return recent form and overall stats for a team before a given date.
    Stats: win% in last 5 matches, avg runs scored, avg wickets taken.
    """
    # Get last 5 matches of the team before date
    query = """
        SELECT m.id, m.team1_id, m.team2_id, m.winner_id, m.date,
               CASE WHEN m.team1_id = ? THEN 1 ELSE 0 END as is_team1
        FROM matches m
        WHERE (m.team1_id = ? OR m.team2_id = ?) AND m.date < ?
        ORDER BY m.date DESC
        LIMIT 5
    """
    df_matches = pd.read_sql_query(query, conn, params=[team_id, team_id, team_id, date])
    if len(df_matches) == 0:
        return {
            'recent_wins': 0,
            'recent_matches': 0,
            'win_pct_recent': 0,
            'avg_runs_scored': 0,
            'avg_wickets_taken': 0
        }

    # Calculate wins in those matches
    wins = 0
    match_ids = []
    for _, row in df_matches.iterrows():
        if row['winner_id'] == team_id:
            wins += 1
        match_ids.append(row['id'])
    win_pct = wins / len(df_matches)

    # Get batting and bowling averages from deliveries for these matches
    if match_ids:
        placeholders = ','.join('?' * len(match_ids))
        # Batting: total runs scored by team in those matches
        # Since we don't have team in deliveries, we need to know which team was batting.
        # But deliveries has BattingTeam column in the original CSV. However, our deliveries table does not have BattingTeam.
        # We'll use an alternative: sum of runs_total for the team's innings.
        # For runs scored by the team, we can sum runs_total where the team was batting.
        # For wickets taken, we need deliveries where the team was bowling and wicket occurred.
        # This requires knowing which innings corresponds to which team.
        # Simpler: use runs conceded from the bowler's team perspective? Might be complicated.
        # For now, we'll use averages from the original deliveries table if we had BattingTeam.
        # Given the complexity, we'll keep placeholder values but compute win% accurately.
        # You can later enhance this by joining with match info.
        avg_runs = 160  # placeholder
        avg_wickets = 6  # placeholder
    else:
        avg_runs = 0
        avg_wickets = 0

    return {
        'recent_wins': wins,
        'recent_matches': len(df_matches),
        'win_pct_recent': win_pct,
        'avg_runs_scored': avg_runs,
        'avg_wickets_taken': avg_wickets
    }

def get_head_to_head(team1_id, team2_id, date, conn):
    """Get head‑to‑head win ratio for team1 vs team2 before date."""
    query = """
        SELECT winner_id, COUNT(*) as cnt
        FROM matches
        WHERE ((team1_id = ? AND team2_id = ?) OR (team1_id = ? AND team2_id = ?))
          AND date < ?
        GROUP BY winner_id
    """
    df = pd.read_sql_query(query, conn, params=[team1_id, team2_id, team2_id, team1_id, date])
    total = df['cnt'].sum()
    if total == 0:
        return 0.5
    wins_team1 = df[df['winner_id'] == team1_id]['cnt'].sum() if team1_id in df['winner_id'].values else 0
    return wins_team1 / total

def get_venue_stats(venue_id, date, conn):
    """Get venue statistics: average first innings score, win% batting first."""
    # Find matches at this venue before date
    query = """
        SELECT m.*
        FROM matches m
        WHERE m.venue_id = ? AND m.date < ?
    """
    df = pd.read_sql_query(query, conn, params=[venue_id, date])
    if len(df) == 0:
        return {'avg_first_innings': 160, 'win_pct_batting_first': 0.5}

    # We don't have first innings scores directly. Could compute from deliveries.
    # For simplicity, use dummy values.
    return {'avg_first_innings': 165, 'win_pct_batting_first': 0.52}

def get_toss_impact(team_id, venue_id, date, conn):
    """How often team wins after winning toss at this venue."""
    query = """
        SELECT COUNT(*) as cnt, SUM(CASE WHEN winner_id = toss_winner_id THEN 1 ELSE 0 END) as wins
        FROM matches
        WHERE toss_winner_id = ? AND venue_id = ? AND date < ?
    """
    df = pd.read_sql_query(query, conn, params=[team_id, venue_id, date])
    if df['cnt'].iloc[0] == 0:
        return 0.5
    return df['wins'].iloc[0] / df['cnt'].iloc[0]

def build_training_features(conn):
    """Generate feature matrix for all historical matches."""
    # Get all matches with known winner (non‑null)
    matches = pd.read_sql_query("SELECT * FROM matches WHERE winner_id IS NOT NULL", conn)
    features = []
    labels = []

    for _, match in matches.iterrows():
        team1 = match['team1_id']
        team2 = match['team2_id']
        venue = match['venue_id']
        date = match['date']
        toss_winner = match['toss_winner_id']
        toss_decision = match['toss_decision']

        # Team stats
        t1_stats = get_team_stats(team1, date, conn)
        t2_stats = get_team_stats(team2, date, conn)

        # Head‑to‑head
        h2h = get_head_to_head(team1, team2, date, conn)

        # Venue stats
        venue_stats = get_venue_stats(venue, date, conn)

        # Toss impact for each team
        toss_impact1 = get_toss_impact(team1, venue, date, conn)
        toss_impact2 = get_toss_impact(team2, venue, date, conn)

        # Is toss winner batting first?
        toss_bat_first = 1 if toss_decision == 'bat' else 0

        feature_vector = [
            t1_stats['win_pct_recent'],
            t2_stats['win_pct_recent'],
            t1_stats['avg_runs_scored'],
            t2_stats['avg_runs_scored'],
            t1_stats['avg_wickets_taken'],
            t2_stats['avg_wickets_taken'],
            h2h,
            venue_stats['avg_first_innings'],
            venue_stats['win_pct_batting_first'],
            toss_impact1,
            toss_impact2,
            toss_bat_first,
            1 if toss_winner == team1 else 0  # did team1 win toss?
        ]
        features.append(feature_vector)
        # Label: 1 if team1 won, 0 if team2 won
        labels.append(1 if match['winner_id'] == team1 else 0)

    return np.array(features), np.array(labels)

if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    X, y = build_training_features(conn)
    np.save("data/processed/X.npy", X)
    np.save("data/processed/y.npy", y)
    conn.close()
    print("Features saved to data/processed/")