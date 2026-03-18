# 🍒 CherryIPL – IPL 2026 Match Predictor

A free, open‑source web app that predicts IPL 2026 match outcomes using machine learning.  
Built with Python (Flask, XGBoost) and a dark cricket‑themed UI.

## ✨ Features
- 🤖 **ML‑Powered Predictions** – trained on historical IPL data (76.9% accuracy)
- 🎨 **Team‑Colored Progress Bars** – each team's jersey colour in prediction bars
- 🏏 **Live Match Simulation** – placeholder scores for today's matches
- 📊 **Player Stats** – batting & bowling stats from ball‑by‑ball data
- 🔄 **Head‑to‑Head Records** – compare any two teams
- 🛠️ **Admin Overrides** – manually update toss, injuries, or predictions
- 🌙 **Dark Cricket Theme** – with subtle bat/ball background pattern
- 💯 **100% Free** – no hidden costs, no API keys required

## 🛠️ Tech Stack
- Backend: Flask (Python)
- Database: SQLite
- ML: XGBoost, scikit‑learn, pandas
- Frontend: Bootstrap 5, custom CSS

## 🚀 Run Locally
1. Clone the repo  
   `git clone https://github.com/vineel06/CherryIPLPrediction.git`
2. Install dependencies  
   `pip install -r requirements.txt`
3. Initialize the database  
   `python init_db.py`
4. Load historical data  
   `python scripts/fetch_historical.py`
5. Populate the database  
   `python populate_db.py`
6. Generate features and train the model  
   `python model/features.py`  
   `python model/train.py`
7. Insert 2026 schedule & players  
   `python scripts/insert_2026_schedule.py`  
   `python load_2026_data.py` (if you have the auction data)
8. Run the app  
   `python app.py`

## ⚠️ Disclaimer
This project is for educational and entertainment purposes only. It does not encourage betting or gambling. Match predictions are probabilistic and may not be accurate.

## 📄 License
MIT
