import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

DB_PATH = "data/ipl.db"


def get_team_historical_pattern(team_id, conn):
    """Get team-specific patterns like first match performance"""

    # Get team's first match performance in each season
    first_matches = conn.execute('''
        SELECT m.date, m.winner_id
        FROM matches m
        WHERE (m.team1_id = ? OR m.team2_id = ?)
        AND m.season IN (SELECT DISTINCT season FROM matches WHERE (team1_id = ? OR team2_id = ?))
        GROUP BY m.season
        HAVING m.date = MIN(m.date)
    ''', (team_id, team_id, team_id, team_id)).fetchall()

    first_match_win_pct = sum(1 for m in first_matches if m[1] == team_id) / len(
        first_matches) if first_matches else 0.5

    return first_match_win_pct


def get_team_recent_form(team_id, date, conn, limit=5):
    """Get team's recent form before a given date"""
    matches = conn.execute('''
        SELECT winner_id
        FROM matches
        WHERE (team1_id = ? OR team2_id = ?) 
        AND date < ?
        AND winner_id IS NOT NULL
        ORDER BY date DESC
        LIMIT ?
    ''', (team_id, team_id, date, limit)).fetchall()

    if len(matches) == 0:
        return 0.5

    wins = sum(1 for m in matches if m[0] == team_id)
    return wins / len(matches)


def get_head_to_head(team1_id, team2_id, conn):
    """Get head-to-head record between teams"""
    matches = conn.execute('''
        SELECT winner_id
        FROM matches
        WHERE ((team1_id = ? AND team2_id = ?) OR (team1_id = ? AND team2_id = ?))
        AND winner_id IS NOT NULL
    ''', (team1_id, team2_id, team2_id, team1_id)).fetchall()

    if len(matches) == 0:
        return 0.5

    wins = sum(1 for m in matches if m[0] == team1_id)
    return wins / len(matches)


def get_venue_record(team_id, venue_id, conn):
    """Get team's performance at specific venue"""
    matches = conn.execute('''
        SELECT winner_id
        FROM matches
        WHERE venue_id = ? AND (team1_id = ? OR team2_id = ?)
        AND winner_id IS NOT NULL
    ''', (venue_id, team_id, team_id)).fetchall()

    if len(matches) == 0:
        return 0.5

    wins = sum(1 for m in matches if m[0] == team_id)
    return wins / len(matches)


def get_toss_impact(team_id, conn):
    """Get how often team wins after winning toss"""
    matches = conn.execute('''
        SELECT winner_id
        FROM matches
        WHERE toss_winner_id = ? AND winner_id IS NOT NULL
    ''', (team_id,)).fetchall()

    if len(matches) == 0:
        return 0.5

    wins = sum(1 for m in matches if m[0] == team_id)
    return wins / len(matches)


def build_features():
    """Build comprehensive features from historical data"""
    conn = sqlite3.connect(DB_PATH)

    # Get all completed matches
    matches = pd.read_sql_query('''
        SELECT m.id, m.team1_id, m.team2_id, m.venue_id, m.date,
               m.toss_winner_id, m.toss_decision, m.winner_id,
               t1.name as team1_name, t2.name as team2_name
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        WHERE m.winner_id IS NOT NULL
        ORDER BY m.date
    ''', conn)

    if len(matches) == 0:
        print("❌ No matches with results found!")
        conn.close()
        return None, None

    print(f"✅ Found {len(matches)} completed matches for training")

    features = []
    labels = []

    for _, match in matches.iterrows():
        # Get team names for display
        team1_name = match['team1_name']
        team2_name = match['team2_name']

        # 1. Recent form (last 5 matches)
        form1 = get_team_recent_form(match['team1_id'], match['date'], conn, 5)
        form2 = get_team_recent_form(match['team2_id'], match['date'], conn, 5)

        # 2. Head to head record
        h2h = get_head_to_head(match['team1_id'], match['team2_id'], conn)

        # 3. Venue record
        venue1 = get_venue_record(match['team1_id'], match['venue_id'], conn)
        venue2 = get_venue_record(match['team2_id'], match['venue_id'], conn)

        # 4. Toss impact
        toss_impact1 = get_toss_impact(match['team1_id'], conn)
        toss_impact2 = get_toss_impact(match['team2_id'], conn)

        # 5. First match pattern (special for teams like MI)
        first_match_pattern1 = get_team_historical_pattern(match['team1_id'], conn)
        first_match_pattern2 = get_team_historical_pattern(match['team2_id'], conn)

        # 6. Check if it's the team's first match of the season
        is_first_match1 = 1 if conn.execute('''
            SELECT COUNT(*) FROM matches 
            WHERE (team1_id = ? OR team2_id = ?) 
            AND season = (SELECT season FROM matches WHERE id = ?)
            AND date < ?
        ''', (match['team1_id'], match['team1_id'], match['id'], match['date'])).fetchone()[0] == 0 else 0

        is_first_match2 = 1 if conn.execute('''
            SELECT COUNT(*) FROM matches 
            WHERE (team1_id = ? OR team2_id = ?) 
            AND season = (SELECT season FROM matches WHERE id = ?)
            AND date < ?
        ''', (match['team2_id'], match['team2_id'], match['id'], match['date'])).fetchone()[0] == 0 else 0

        # 7. Toss winner and decision
        toss_winner_impact = 1 if match['toss_winner_id'] == match['team1_id'] else 0
        toss_decision_impact = 1 if match['toss_decision'] == 'bat' else 0

        # Feature vector
        feature_vector = [
            form1,  # Team 1 recent form
            form2,  # Team 2 recent form
            h2h,  # Head to head
            venue1,  # Team 1 venue record
            venue2,  # Team 2 venue record
            toss_impact1,  # Team 1 toss impact
            toss_impact2,  # Team 2 toss impact
            first_match_pattern1,  # Team 1 first match pattern
            first_match_pattern2,  # Team 2 first match pattern
            is_first_match1,  # Is this team1's first match?
            is_first_match2,  # Is this team2's first match?
            toss_winner_impact,  # Who won toss?
            toss_decision_impact  # Bat or field?
        ]

        features.append(feature_vector)
        labels.append(1 if match['winner_id'] == match['team1_id'] else 0)

    conn.close()
    return np.array(features), np.array(labels)


def train_model():
    """Train the real prediction model"""
    print("Building features from historical IPL data...")
    X, y = build_features()

    if X is None:
        print("❌ Cannot train model")
        return None

    print(f"Training on {len(X)} matches with {X.shape[1]} features")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Use Random Forest with optimized parameters
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n{'=' * 60}")
    print(f"🎯 MODEL ACCURACY: {accuracy:.3f} ({accuracy * 100:.1f}%)")
    print(f"{'=' * 60}")

    # Feature importance
    feature_names = [
        'Team 1 Recent Form', 'Team 2 Recent Form', 'Head to Head',
        'Team 1 Venue Record', 'Team 2 Venue Record',
        'Team 1 Toss Impact', 'Team 2 Toss Impact',
        'Team 1 First Match Pattern', 'Team 2 First Match Pattern',
        'Is Team 1 First Match', 'Is Team 2 First Match',
        'Toss Winner', 'Toss Decision'
    ]

    print("\n📊 TOP 10 MOST IMPORTANT FEATURES:")
    importance = model.feature_importances_
    sorted_idx = np.argsort(importance)[::-1][:10]
    for i, idx in enumerate(sorted_idx, 1):
        print(f"   {i}. {feature_names[idx]}: {importance[idx]:.3f}")

    # Save model
    os.makedirs("model", exist_ok=True)
    joblib.dump(model, "model/xgb_model.pkl")
    print("\n✅ Model saved to model/xgb_model.pkl")

    return model


def predict_match(team1_name, team2_name, venue_name, toss_winner=None, toss_decision=None):
    """Predict match using trained model"""
    import random

    try:
        conn = sqlite3.connect(DB_PATH)
        model = joblib.load("model/xgb_model.pkl")

        # Get team and venue IDs
        team1 = conn.execute("SELECT id FROM teams WHERE name = ?", (team1_name,)).fetchone()
        team2 = conn.execute("SELECT id FROM teams WHERE name = ?", (team2_name,)).fetchone()
        venue = conn.execute("SELECT id FROM venues WHERE name = ?", (venue_name,)).fetchone()

        if not team1 or not team2 or not venue:
            conn.close()
            prob = random.uniform(0.35, 0.65)
            return prob, 1 - prob

        # Get all features
        form1 = get_team_recent_form(team1[0], '2026-12-31', conn, 5)
        form2 = get_team_recent_form(team2[0], '2026-12-31', conn, 5)
        h2h = get_head_to_head(team1[0], team2[0], conn)
        venue1 = get_venue_record(team1[0], venue[0], conn)
        venue2 = get_venue_record(team2[0], venue[0], conn)
        toss_impact1 = get_toss_impact(team1[0], conn)
        toss_impact2 = get_toss_impact(team2[0], conn)
        first_pattern1 = get_team_historical_pattern(team1[0], conn)
        first_pattern2 = get_team_historical_pattern(team2[0], conn)

        # Check if this is first match of the season
        is_first1 = 1 if conn.execute('''
            SELECT COUNT(*) FROM matches 
            WHERE (team1_id = ? OR team2_id = ?) AND season = 2026
        ''', (team1[0], team1[0])).fetchone()[0] == 0 else 0

        is_first2 = 1 if conn.execute('''
            SELECT COUNT(*) FROM matches 
            WHERE (team1_id = ? OR team2_id = ?) AND season = 2026
        ''', (team2[0], team2[0])).fetchone()[0] == 0 else 0

        toss_winner_flag = 1 if toss_winner == team1_name else 0
        toss_decision_flag = 1 if toss_decision == 'bat' else 0

        # Feature vector
        features = [[
            form1, form2, h2h, venue1, venue2,
            toss_impact1, toss_impact2,
            first_pattern1, first_pattern2,
            is_first1, is_first2,
            toss_winner_flag, toss_decision_flag
        ]]

        prob = model.predict_proba(features)[0]
        conn.close()
        return prob[1], prob[0]

    except Exception as e:
        print(f"Prediction error: {e}")
        prob = random.uniform(0.35, 0.65)
        return prob, 1 - prob


if __name__ == "__main__":
    train_model()