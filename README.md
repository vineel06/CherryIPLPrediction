🍒 CherryIPL – IPL 2026 Match Predictor
A free, open-source web application that predicts IPL 2026 match outcomes using machine learning. Built with Python (Flask, Random Forest) and a dark cricket-themed UI.

✨ Features
🤖 ML-Powered Predictions – Trained on 1,146 historical IPL matches (70.9% accuracy)
🎨 Team-Colored UI – Each team displayed in official IPL 2026 jersey colours
📊 Player Statistics – Batting & bowling stats for 250+ players
🔄 Head-to-Head Records – Compare any two teams
📈 Points Table – Real-time standings
🛠️ Admin Overrides – Update toss, injuries, or predictions manually
🌙 Dark Cricket Theme – Immersive cricket-style UI
💯 100% Free – No API keys or hidden costs

🛠️ Tech Stack
Category	    Technology
Backend	Python  3.11+, Flask
Database	    SQLite
ML Model	    Random Forest Classifier
Frontend	    Bootstrap 5, Jinja2, CSS3
Data Processing	Pandas, NumPy
Data Sources	Cricsheet, IPL Official Data

🎯 Model Features
The model uses 13 features trained on 1,146 IPL matches (2008–2025):
Feature	Description
Team Recent Form	Win % in last 5 matches
Head-to-Head	Historical win ratio
Venue Record	Performance at venue
Toss Impact	Win % after toss
First Match Pattern	Season opener performance
Toss Winner & Decision	Impact of toss

📌 Model Accuracy: 70.9% (test data)

📁 Project Structure
CherryIPLPrediction/
├── app.py
├── model/
│   ├── train_real_model.py
│   └── features.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── matches.html
│   ├── match.html
│   ├── predict.html
│   ├── points.html
│   ├── teams.html
│   ├── team.html
│   ├── players.html
│   ├── player.html
│   ├── headtohead.html
│   ├── venues.html
│   └── admin.html
├── scripts/
│   ├── fetch_historical.py
│   └── update_data.py
├── static/
│   └── style.css
├── requirements.txt
└── README.md

🚀 Quick Start
🔧 Prerequisites
Python 3.11+
Git
Virtual environment (recommended)

⚙️ Installation
1. Clone the repository
git clone https://github.com/vineel06/CherryIPLPrediction.git
cd CherryIPLPrediction

2. Create & activate virtual environment
Windows
python -m venv .venv
.venv\Scripts\activate

Mac/Linux
python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Initialize database & load data
python complete_setup.py
python load_2026_data.py
python add_remaining_matches.py
python update_2026_players.py
python update_player_stats.py
python train_real_model.py

5. Run the app
python app.py

6. Open in browser
http://127.0.0.1:5000

🎨 Team Colours (IPL 2026)
Team	                    Colour	Hex Code
Chennai Super Kings	        Yellow	#F9CD05
Mumbai Indians	            Blue	#004BA0
Royal Challengers Bengaluru	Red	    #EC1C24
Kolkata Knight Riders	    Purple	#2E0854
Lucknow Super Giants	    Red	    #FF0000
Sunrisers Hyderabad	        Orange	#F7A721
Punjab Kings	            Red	    #FF0000
Gujarat Titans	         Navy Blue	#0F4D92
Rajasthan Royals	        Pink	#FF1493
Delhi Capitals	            Blue	#0000FF

📊 Usage Guide
🔍 Viewing Predictions
Homepage → Upcoming matches with predictions
Matches Page → Full schedule
Match Details → Prediction + confidence score
🎯 Custom Predictions
Use the Predict page
Select teams, venue, and toss outcome
👥 Player Stats
Explore 250+ players
View runs, averages, wickets, etc.

🛠️ Admin Features
Visit /admin
Update toss, injuries, or override predictions

⚠️ Disclaimer
This project is for educational and entertainment purposes only.
It does not support betting or gambling.
Predictions are probabilistic and may not always be accurate.
The developers are not responsible for misuse.

📄 License
Licensed under the MIT License.

🙏 Acknowledgments
Cricsheet (ball-by-ball data)
IPL Official Website (player data)
Random Forest (ML model)
Bootstrap (UI framework)
Open-source contributors ❤️

📧 Contact
Developer: Vineel
GitHub: https://github.com/vineel06
Project: https://github.com/vineel06/CherryIPLPrediction

🌟 Show Your Support
If you found this project helpful:
⭐ Star the repository
📢 Share with cricket fans
