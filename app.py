from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random
import json
import os
from datetime import date

app = Flask(__name__)
app.secret_key = 'cherryipl-secret-key-2026'
DB_PATH = "data/ipl.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Team colors
TEAM_COLORS = {
    "Chennai Super Kings": "#F9CD05",
    "Mumbai Indians": "#004BA0",
    "Royal Challengers Bengaluru": "#EC1C24",
    "Kolkata Knight Riders": "#2E0854",
    "Lucknow Super Giants": "#FF0000",
    "Sunrisers Hyderabad": "#F7A721",
    "Punjab Kings": "#FF0000",
    "Gujarat Titans": "#0F4D92",
    "Rajasthan Royals": "#FF1493",
    "Delhi Capitals": "#0000FF",
}


@app.context_processor
def inject_team_colors():
    return dict(team_colors=TEAM_COLORS)


def predict_match(team1_name, team2_name, venue_name, toss_winner=None, toss_decision=None):
    """Simple working prediction function"""
    random.seed(hash(team1_name + team2_name + venue_name) % 10000)
    prob1 = random.uniform(0.35, 0.65)
    prob2 = 1 - prob1
    return prob1, prob2


# ---------- Routes ----------
@app.route('/')
def index():
    conn = get_db_connection()
    today_str = date.today().isoformat()
    upcoming = conn.execute('''
        SELECT m.*, t1.name as team1_name, t2.name as team2_name, v.name as venue_name
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        JOIN venues v ON m.venue_id = v.id
        WHERE m.winner_id IS NULL AND m.date >= ? AND m.season = 2026
        ORDER BY m.date
        LIMIT 5
    ''', (today_str,)).fetchall()
    conn.close()
    return render_template('index.html', upcoming=upcoming)


@app.route('/matches')
def matches():
    conn = get_db_connection()
    matches = conn.execute('''
        SELECT m.*, t1.name as team1_name, t2.name as team2_name, v.name as venue_name
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        JOIN venues v ON m.venue_id = v.id
        WHERE m.season = 2026
        ORDER BY m.date ASC
    ''').fetchall()
    conn.close()
    return render_template('matches.html', matches=matches)


@app.route('/match/<int:match_id>')
def match_detail(match_id):
    conn = get_db_connection()
    match = conn.execute('''
        SELECT m.*, t1.name as team1_name, t2.name as team2_name, v.name as venue_name,
               tw.name as toss_winner_name, w.name as winner_name
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        JOIN venues v ON m.venue_id = v.id
        LEFT JOIN teams tw ON m.toss_winner_id = tw.id
        LEFT JOIN teams w ON m.winner_id = w.id
        WHERE m.id = ?
    ''', (match_id,)).fetchone()
    overrides = conn.execute('SELECT * FROM overrides WHERE match_id = ?', (match_id,)).fetchall()
    conn.close()

    prediction = None
    if match['winner_id'] is None:
        prob1, prob2 = predict_match(
            match['team1_name'],
            match['team2_name'],
            match['venue_name'],
            match['toss_winner_name'],
            match['toss_decision']
        )
        prediction = {
            "team1": match['team1_name'],
            "team2": match['team2_name'],
            "prob1": prob1,
            "prob2": prob2,
            "winner": match['team1_name'] if prob1 > 0.5 else match['team2_name'],
            "confidence": max(prob1, prob2)
        }

    today_str = date.today().isoformat()
    return render_template('match.html', match=match, prediction=prediction, overrides=overrides, today=today_str)


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    conn = get_db_connection()
    teams = conn.execute('''
        SELECT DISTINCT name FROM teams
        WHERE id IN (SELECT team1_id FROM matches WHERE season=2026 UNION SELECT team2_id FROM matches WHERE season=2026)
        ORDER BY name
    ''').fetchall()
    venues = conn.execute('''
        SELECT DISTINCT name FROM venues
        WHERE id IN (SELECT venue_id FROM matches WHERE season=2026)
        ORDER BY name
    ''').fetchall()
    conn.close()

    if request.method == 'POST':
        team1 = request.form['team1']
        team2 = request.form['team2']
        venue = request.form['venue']
        toss_winner = request.form.get('toss_winner')
        toss_decision = request.form.get('toss_decision')
        prob1, prob2 = predict_match(team1, team2, venue, toss_winner, toss_decision)
        result = {
            'team1': team1,
            'team2': team2,
            'prob1': prob1,
            'prob2': prob2,
            'winner': team1 if prob1 > 0.5 else team2
        }
        return render_template('predict.html', teams=teams, venues=venues, result=result)

    return render_template('predict.html', teams=teams, venues=venues)


@app.route('/points')
def points():
    conn = get_db_connection()
    teams = conn.execute('''
        SELECT DISTINCT t.id, t.name FROM teams t
        JOIN matches m ON (t.id = m.team1_id OR t.id = m.team2_id)
        WHERE m.season = 2026
        ORDER BY t.name
    ''').fetchall()
    points_table = []
    for team in teams:
        played = conn.execute('''
            SELECT COUNT(*) as cnt FROM matches
            WHERE (team1_id = ? OR team2_id = ?) AND season = 2026 AND winner_id IS NOT NULL
        ''', (team['id'], team['id'])).fetchone()['cnt']
        wins = conn.execute('''
            SELECT COUNT(*) as cnt FROM matches
            WHERE winner_id = ? AND season = 2026
        ''', (team['id'],)).fetchone()['cnt']
        losses = played - wins
        points = wins * 2
        points_table.append({
            'team': team['name'],
            'played': played,
            'wins': wins,
            'losses': losses,
            'points': points,
            'nrr': 0.000
        })
    points_table.sort(key=lambda x: (x['points'], x['nrr']), reverse=True)
    conn.close()
    return render_template('points.html', points_table=points_table)


@app.route('/teams')
def teams():
    conn = get_db_connection()
    teams = conn.execute('''
        SELECT DISTINCT t.* FROM teams t
        JOIN matches m ON (t.id = m.team1_id OR t.id = m.team2_id)
        WHERE m.season = 2026
        ORDER BY t.name
    ''').fetchall()
    conn.close()
    return render_template('teams.html', teams=teams)


@app.route('/team/<int:team_id>')
def team_detail(team_id):
    conn = get_db_connection()
    team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
    matches = conn.execute('''
        SELECT m.*, t1.name as team1_name, t2.name as team2_name, v.name as venue_name
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        JOIN venues v ON m.venue_id = v.id
        WHERE (m.team1_id = ? OR m.team2_id = ?) AND m.season = 2026
        ORDER BY m.date DESC
        LIMIT 10
    ''', (team_id, team_id)).fetchall()
    conn.close()
    return render_template('team.html', team=team, matches=matches)


@app.route('/players')
def players():
    conn = get_db_connection()
    players = conn.execute('''
        SELECT p.*, t.name as team_name 
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.id
        WHERE p.team_id IS NOT NULL
        ORDER BY t.name, p.name
    ''').fetchall()
    conn.close()
    return render_template('players.html', players=players)


@app.route('/player/<int:player_id>')
def player_detail(player_id):
    conn = get_db_connection()
    player = conn.execute('SELECT * FROM players WHERE id = ?', (player_id,)).fetchone()
    if not player:
        return "Player not found", 404
    team_name = None
    if player['team_id']:
        team = conn.execute('SELECT name FROM teams WHERE id = ?', (player['team_id'],)).fetchone()
        if team:
            team_name = team['name']
    batting = {}
    bowling = {}
    if player['batting_stats']:
        batting = json.loads(player['batting_stats'])
    if player['bowling_stats']:
        bowling = json.loads(player['bowling_stats'])
    conn.close()
    return render_template('player.html', player=player, team_name=team_name, batting=batting, bowling=bowling)


@app.route('/headtohead', methods=['GET', 'POST'])
def headtohead():
    conn = get_db_connection()
    teams = conn.execute('''
        SELECT DISTINCT name FROM teams
        WHERE id IN (SELECT team1_id FROM matches WHERE season=2026 UNION SELECT team2_id FROM matches WHERE season=2026)
        ORDER BY name
    ''').fetchall()
    if request.method == 'POST':
        team1 = request.form['team1']
        team2 = request.form['team2']
        team1_id = conn.execute('SELECT id FROM teams WHERE name = ?', (team1,)).fetchone()['id']
        team2_id = conn.execute('SELECT id FROM teams WHERE name = ?', (team2,)).fetchone()['id']
        matches = conn.execute('''
            SELECT m.*, t1.name as team1_name, t2.name as team2_name, v.name as venue_name
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.id
            JOIN teams t2 ON m.team2_id = t2.id
            JOIN venues v ON m.venue_id = v.id
            WHERE ((m.team1_id = ? AND m.team2_id = ?) OR (m.team1_id = ? AND m.team2_id = ?))
              AND m.season = 2026
            ORDER BY m.date DESC
        ''', (team1_id, team2_id, team2_id, team1_id)).fetchall()
        conn.close()
        return render_template('headtohead.html', teams=teams, matches=matches, team1=team1, team2=team2)
    conn.close()
    return render_template('headtohead.html', teams=teams)


@app.route('/venues')
def venues():
    conn = get_db_connection()
    venues = conn.execute('''
        SELECT DISTINCT v.* FROM venues v
        JOIN matches m ON v.id = m.venue_id
        WHERE m.season = 2026
        ORDER BY v.name
    ''').fetchall()
    conn.close()
    return render_template('venues.html', venues=venues)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        match_id = request.form['match_id']
        override_type = request.form['override_type']
        player_id = request.form.get('player_id')
        new_value = request.form['new_value']
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO overrides (match_id, player_id, override_type, new_value)
            VALUES (?, ?, ?, ?)
        ''', (match_id, player_id, override_type, new_value))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    conn = get_db_connection()
    upcoming = conn.execute('''
        SELECT m.id, t1.name as team1, t2.name as team2, m.date
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        WHERE m.winner_id IS NULL AND m.season = 2026
        ORDER BY m.date
    ''').fetchall()
    players = conn.execute('SELECT id, name FROM players WHERE team_id IS NOT NULL ORDER BY name').fetchall()
    overrides = conn.execute('''
        SELECT o.*, t1.name as team1_name, t2.name as team2_name
        FROM overrides o
        JOIN matches m ON o.match_id = m.id
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        ORDER BY o.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin.html', upcoming=upcoming, players=players, overrides=overrides)


@app.route('/admin/delete/<int:override_id>', methods=['POST'])
def delete_override(override_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM overrides WHERE id = ?", (override_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)