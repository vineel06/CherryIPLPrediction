import sqlite3
import json

DB_PATH = "data/ipl.db"


def update_player_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Add stats columns if they don't exist
    try:
        c.execute("ALTER TABLE players ADD COLUMN batting_stats TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE players ADD COLUMN bowling_stats TEXT")
    except:
        pass

    # Get all players
    players = c.execute("SELECT id, name FROM players WHERE team_id IS NOT NULL").fetchall()

    for player_id, player_name in players:
        # Batting stats
        batting = c.execute('''
            SELECT 
                COUNT(DISTINCT match_id) as matches,
                COALESCE(SUM(runs_batsman), 0) as runs,
                COALESCE(COUNT(CASE WHEN runs_batsman >= 50 AND runs_batsman < 100 THEN 1 END), 0) as fifties,
                COALESCE(COUNT(CASE WHEN runs_batsman >= 100 THEN 1 END), 0) as hundreds,
                COALESCE(MAX(runs_batsman), 0) as highest_score,
                COALESCE(ROUND(AVG(runs_batsman), 2), 0) as average,
                COALESCE(COUNT(CASE WHEN player_dismissed_id = ? THEN 1 END), 0) as dismissals
            FROM deliveries
            WHERE batsman_id = ?
        ''', (player_id, player_id)).fetchone()

        # Bowling stats
        bowling = c.execute('''
            SELECT 
                COUNT(DISTINCT match_id) as matches,
                COALESCE(COUNT(CASE WHEN wicket_type IS NOT NULL THEN 1 END), 0) as wickets,
                COALESCE(SUM(runs_total), 0) as runs_conceded,
                COALESCE(ROUND(SUM(runs_total) * 1.0 / NULLIF(COUNT(CASE WHEN wicket_type IS NOT NULL THEN 1 END), 0), 2), 0) as average
            FROM deliveries
            WHERE bowler_id = ?
        ''', (player_id,)).fetchone()

        # Convert to dict
        batting_dict = {
            'matches': batting[0] or 0,
            'runs': batting[1] or 0,
            'fifties': batting[2] or 0,
            'hundreds': batting[3] or 0,
            'highest_score': batting[4] or 0,
            'average': batting[5] or 0,
            'dismissals': batting[6] or 0
        }

        bowling_dict = {
            'matches': bowling[0] or 0,
            'wickets': bowling[1] or 0,
            'runs_conceded': bowling[2] or 0,
            'average': bowling[3] or 0
        }

        # Update player
        c.execute("UPDATE players SET batting_stats = ?, bowling_stats = ? WHERE id = ?",
                  (json.dumps(batting_dict), json.dumps(bowling_dict), player_id))

    conn.commit()
    conn.close()
    print(f"✅ Updated stats for {len(players)} players")


if __name__ == "__main__":
    update_player_stats()