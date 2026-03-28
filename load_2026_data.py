import sqlite3
import re

DB_PATH = "data/ipl.db"

# --- Schedule data (manually extracted from your message) ---
SCHEDULE_2026 = [
    {"match_number": 1, "date": "2026-03-28", "team1": "Royal Challengers Bengaluru", "team2": "Sunrisers Hyderabad", "venue": "M.Chinnaswamy Stadium, Bengaluru", "city": "Bengaluru"},
    {"match_number": 2, "date": "2026-03-29", "team1": "Mumbai Indians", "team2": "Kolkata Knight Riders", "venue": "Wankhede Stadium, Mumbai", "city": "Mumbai"},
    {"match_number": 3, "date": "2026-03-30", "team1": "Rajasthan Royals", "team2": "Chennai Super Kings", "venue": "Barsapara Stadium, Guwahati", "city": "Guwahati"},
    {"match_number": 4, "date": "2026-03-31", "team1": "Punjab Kings", "team2": "Gujarat Titans", "venue": "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh", "city": "New Chandigarh"},
    {"match_number": 5, "date": "2026-04-01", "team1": "Lucknow Super Giants", "team2": "Delhi Capitals", "venue": "BRSABV Ekana Cricket Stadium, Lucknow", "city": "Lucknow"},
    {"match_number": 6, "date": "2026-04-02", "team1": "Kolkata Knight Riders", "team2": "Sunrisers Hyderabad", "venue": "Eden Gardens, Kolkata", "city": "Kolkata"},
    {"match_number": 7, "date": "2026-04-03", "team1": "Chennai Super Kings", "team2": "Punjab Kings", "venue": "MA Chidambaram Stadium, Chennai", "city": "Chennai"},
    {"match_number": 8, "date": "2026-04-04", "team1": "Delhi Capitals", "team2": "Mumbai Indians", "venue": "Arun Jaitley Stadium, Delhi", "city": "Delhi"},
    {"match_number": 9, "date": "2026-04-04", "team1": "Gujarat Titans", "team2": "Rajasthan Royals", "venue": "Narendra Modi Stadium, Ahmedabad", "city": "Ahmedabad"},
    {"match_number": 10, "date": "2026-04-05", "team1": "Sunrisers Hyderabad", "team2": "Lucknow Super Giants", "venue": "Rajiv Gandhi International Stadium, Hyderabad", "city": "Hyderabad"},
    {"match_number": 11, "date": "2026-04-05", "team1": "Royal Challengers Bengaluru", "team2": "Chennai Super Kings", "venue": "M.Chinnaswamy Stadium, Bengaluru", "city": "Bengaluru"},
    {"match_number": 12, "date": "2026-04-06", "team1": "Kolkata Knight Riders", "team2": "Punjab Kings", "venue": "Eden Gardens, Kolkata", "city": "Kolkata"},
    {"match_number": 13, "date": "2026-04-07", "team1": "Rajasthan Royals", "team2": "Mumbai Indians", "venue": "Barsapara Stadium, Guwahati", "city": "Guwahati"},
    {"match_number": 14, "date": "2026-04-08", "team1": "Delhi Capitals", "team2": "Gujarat Titans", "venue": "Arun Jaitley Stadium, Delhi", "city": "Delhi"},
    {"match_number": 15, "date": "2026-04-09", "team1": "Kolkata Knight Riders", "team2": "Lucknow Super Giants", "venue": "Eden Gardens, Kolkata", "city": "Kolkata"},
    {"match_number": 16, "date": "2026-04-10", "team1": "Rajasthan Royals", "team2": "Royal Challengers Bengaluru", "venue": "Barsapara Stadium, Guwahati", "city": "Guwahati"},
    {"match_number": 17, "date": "2026-04-11", "team1": "Punjab Kings", "team2": "Sunrisers Hyderabad", "venue": "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh", "city": "New Chandigarh"},
    {"match_number": 18, "date": "2026-04-11", "team1": "Chennai Super Kings", "team2": "Delhi Capitals", "venue": "MA Chidambaram Stadium, Chennai", "city": "Chennai"},
    {"match_number": 19, "date": "2026-04-12", "team1": "Lucknow Super Giants", "team2": "Gujarat Titans", "venue": "BRSABV Ekana Cricket Stadium, Lucknow", "city": "Lucknow"},
    {"match_number": 20, "date": "2026-04-12", "team1": "Mumbai Indians", "team2": "Royal Challengers Bengaluru", "venue": "Wankhede Stadium, Mumbai", "city": "Mumbai"},
    # Playoffs – we'll add them separately
]

PLAYOFFS = [
    {"match_number": 21, "date": "2026-05-26", "team1": "1st placed", "team2": "2nd placed", "venue": "TBD", "city": "TBD", "stage": "Qualifier 1"},
    {"match_number": 22, "date": "2026-05-27", "team1": "3rd placed", "team2": "4th placed", "venue": "TBD", "city": "TBD", "stage": "Eliminator"},
    {"match_number": 23, "date": "2026-05-29", "team1": "Loser of Qualifier 1", "team2": "Winner of Eliminator", "venue": "TBD", "city": "TBD", "stage": "Qualifier 2"},
    {"match_number": 24, "date": "2026-05-31", "team1": "Winner of Qualifier 1", "team2": "Winner of Qualifier 2", "venue": "M. Chinnaswamy Stadium, Bengaluru", "city": "Bengaluru", "stage": "Final"},
]

# --- Auction data (simplified; you may need to expand) ---
# This is a partial list; you should add all sold players from your message.
# Format: (player_name, team, role, price_in_crores)
AUCTION_SOLD = [
    # RCB
    ("Virat Kohli", "Royal Challengers Bengaluru", "BAT", 21.00),
    ("Josh Hazlewood", "Royal Challengers Bengaluru", "BOWL", 12.50),
    ("Phil Salt", "Royal Challengers Bengaluru", "BAT", 11.50),
    ("Rajat Patidar", "Royal Challengers Bengaluru", "BAT", 11.00),
    ("Jitesh Sharma", "Royal Challengers Bengaluru", "BAT", 11.00),
    ("Bhuvneshwar Kumar", "Royal Challengers Bengaluru", "BOWL", 10.75),
    ("Rasikh Salam", "Royal Challengers Bengaluru", "BOWL", 6.00),
    ("Krunal Pandya", "Royal Challengers Bengaluru", "AR", 5.75),
    ("Yash Dayal", "Royal Challengers Bengaluru", "BOWL", 5.00),
    ("Tim David", "Royal Challengers Bengaluru", "AR", 3.00),
    ("Suyash Sharma", "Royal Challengers Bengaluru", "BOWL", 2.60),
    ("Jacob Bethell", "Royal Challengers Bengaluru", "AR", 2.60),
    ("Devdutt Padikkal", "Royal Challengers Bengaluru", "BAT", 2.00),
    ("Nuwan Thushara", "Royal Challengers Bengaluru", "BOWL", 1.60),
    ("Romario Shepherd", "Royal Challengers Bengaluru", "AR", 1.50),
    ("Swapnil Singh", "Royal Challengers Bengaluru", "AR", 0.50),
    ("Abhinandan Singh", "Royal Challengers Bengaluru", "BOWL", 0.30),
    ("Jordan Cox", "Royal Challengers Bengaluru", "BAT", 0.75),  # from auction sold list
    ("Jacob Duffy", "Royal Challengers Bengaluru", "BOWL", 2.00),
    ("Venkatesh Iyer", "Royal Challengers Bengaluru", "AR", 7.00),
    ("Kanishk Chouhan", "Royal Challengers Bengaluru", "AR", 0.30),
    ("Vihaan Malhotra", "Royal Challengers Bengaluru", "AR", 0.30),
    ("Vicky Ostwal", "Royal Challengers Bengaluru", "AR", 0.30),
    ("Satvik Deswal", "Royal Challengers Bengaluru", "AR", 0.30),
    ("Mangesh Yadav", "Royal Challengers Bengaluru", "AR", 5.20),
    # MI
    ("Jasprit Bumrah", "Mumbai Indians", "BOWL", 18.00),
    ("Suryakumar Yadav", "Mumbai Indians", "BAT", 16.35),
    ("Hardik Pandya", "Mumbai Indians", "AR", 16.35),
    ("Rohit Sharma", "Mumbai Indians", "BAT", 16.30),
    ("Trent Boult", "Mumbai Indians", "BOWL", 12.50),
    ("Deepak Chahar", "Mumbai Indians", "BOWL", 9.25),
    ("Tilak Varma", "Mumbai Indians", "AR", 8.00),
    ("Naman Dhir", "Mumbai Indians", "AR", 5.25),
    ("Will Jacks", "Mumbai Indians", "AR", 5.25),
    ("AM Ghazanfar", "Mumbai Indians", "BOWL", 4.80),
    ("Sherfane Rutherford", "Mumbai Indians", "BAT", 2.60),
    ("Shardul Thakur", "Mumbai Indians", "AR", 2.00),
    ("Mitchell Santner", "Mumbai Indians", "AR", 2.00),
    ("Ryan Rickelton", "Mumbai Indians", "BAT", 1.00),
    ("Corbin Bosch", "Mumbai Indians", "AR", 0.75),
    ("Robin Minz", "Mumbai Indians", "BAT", 0.65),
    ("Mayank Markande", "Mumbai Indians", "BOWL", 0.30),
    ("Ashwani Kumar", "Mumbai Indians", "BOWL", 0.30),
    ("Raj Bawa", "Mumbai Indians", "AR", 0.30),
    ("Raghu Sharma", "Mumbai Indians", "BOWL", 0.30),
    ("Quinton de Kock", "Mumbai Indians", "BAT", 1.00),
    ("Danish Malewar", "Mumbai Indians", "BAT", 0.30),
    ("Atharva Ankolekar", "Mumbai Indians", "AR", 0.30),
    ("Mohd Izhar", "Mumbai Indians", "BOWL", 0.30),
    ("Mayank Rawat", "Mumbai Indians", "AR", 0.30),
    # SRH
    ("Heinrich Klaasen", "Sunrisers Hyderabad", "BAT", 23.00),
    ("Pat Cummins", "Sunrisers Hyderabad", "AR", 18.00),
    ("Abhishek Sharma", "Sunrisers Hyderabad", "AR", 14.00),
    ("Travis Head", "Sunrisers Hyderabad", "BAT", 14.00),
    ("Ishan Kishan", "Sunrisers Hyderabad", "BAT", 11.25),
    ("Harshal Patel", "Sunrisers Hyderabad", "AR", 8.00),
    ("Nitish Kumar Reddy", "Sunrisers Hyderabad", "AR", 6.00),
    ("Eshan Malinga", "Sunrisers Hyderabad", "BOWL", 1.20),
    ("Jaydev Unadkat", "Sunrisers Hyderabad", "BOWL", 1.00),
    ("Brydon Carse", "Sunrisers Hyderabad", "AR", 1.00),
    ("Kamindu Mendis", "Sunrisers Hyderabad", "AR", 0.75),
    ("Zeeshan Ansari", "Sunrisers Hyderabad", "BOWL", 0.40),
    ("Aniket Verma", "Sunrisers Hyderabad", "BAT", 0.30),
    ("Harsh Dubey", "Sunrisers Hyderabad", "AR", 0.30),
    ("Ravichandran Smaran", "Sunrisers Hyderabad", "BAT", 0.30),
    ("Liam Livingstone", "Sunrisers Hyderabad", "AR", 13.00),
    ("Shivam Mavi", "Sunrisers Hyderabad", "BOWL", 0.75),
    ("Jack Edwards", "Sunrisers Hyderabad", "AR", 3.00),
    ("Krains Fuletra", "Sunrisers Hyderabad", "AR", 0.30),
    ("Praful Hinge", "Sunrisers Hyderabad", "BOWL", 0.30),
    ("Shivang Kumar", "Sunrisers Hyderabad", "AR", 0.30),
    ("Sakib Hussain", "Sunrisers Hyderabad", "BOWL", 0.30),
    ("Salil Arora", "Sunrisers Hyderabad", "BAT", 1.50),
    ("Onkar Tarmale", "Sunrisers Hyderabad", "BOWL", 0.30),
    ("Amit Kumar", "Sunrisers Hyderabad", "BOWL", 0.30),
    # CSK
    ("Sanju Samson", "Chennai Super Kings", "BAT", 18.00),
    ("Ruturaj Gaikwad", "Chennai Super Kings", "BAT", 18.00),
    ("Shivam Dube", "Chennai Super Kings", "AR", 12.00),
    ("Noor Ahmad", "Chennai Super Kings", "BOWL", 10.00),
    ("Khaleel Ahmed", "Chennai Super Kings", "BOWL", 4.80),
    ("MS Dhoni", "Chennai Super Kings", "BAT", 4.00),
    ("Anshul Kamboj", "Chennai Super Kings", "AR", 3.40),
    ("Dewald Brevis", "Chennai Super Kings", "BAT", 2.20),
    ("Gurjapneet Singh", "Chennai Super Kings", "BOWL", 2.20),
    ("Nathan Ellis", "Chennai Super Kings", "BOWL", 2.00),
    ("Jamie Overton", "Chennai Super Kings", "AR", 1.50),
    ("Urvil Patel", "Chennai Super Kings", "BAT", 0.30),
    ("Ayush Mhatre", "Chennai Super Kings", "BAT", 0.30),
    ("Mukesh Choudhary", "Chennai Super Kings", "BOWL", 0.30),
    ("Shreyas Gopal", "Chennai Super Kings", "BOWL", 0.30),
    ("Ramakrishna Ghosh", "Chennai Super Kings", "AR", 0.30),
    ("Rahul Chahar", "Chennai Super Kings", "BOWL", 5.20),
    ("Matt Henry", "Chennai Super Kings", "BOWL", 2.00),
    ("Akeal Hosein", "Chennai Super Kings", "BOWL", 2.00),
    ("Sarfaraz Khan", "Chennai Super Kings", "BAT", 0.75),
    ("Zak Foulkes", "Chennai Super Kings", "AR", 0.75),
    ("Matthew Short", "Chennai Super Kings", "AR", 1.50),
    ("Aman Khan", "Chennai Super Kings", "AR", 0.40),
    ("Kartik Sharma", "Chennai Super Kings", "BAT", 14.20),
    ("Prashant Veer", "Chennai Super Kings", "AR", 14.20),
    # DC
    ("Axar Patel", "Delhi Capitals", "AR", 16.50),
    ("KL Rahul", "Delhi Capitals", "BAT", 14.00),
    ("Kuldeep Yadav", "Delhi Capitals", "BOWL", 13.25),
    ("Mitchell Starc", "Delhi Capitals", "BOWL", 11.75),
    ("T Natarajan", "Delhi Capitals", "BOWL", 10.75),
    ("Tristan Stubbs", "Delhi Capitals", "BAT", 10.00),
    ("Mukesh Kumar", "Delhi Capitals", "BOWL", 8.00),
    ("Nitish Rana", "Delhi Capitals", "AR", 4.20),
    ("Abishek Porel", "Delhi Capitals", "BAT", 4.00),
    ("Ashutosh Sharma", "Delhi Capitals", "AR", 3.80),
    ("Sameer Rizvi", "Delhi Capitals", "AR", 0.95),
    ("Dushmantha Chameera", "Delhi Capitals", "BOWL", 0.75),
    ("Vipraj Nigam", "Delhi Capitals", "AR", 0.50),
    ("Karun Nair", "Delhi Capitals", "BAT", 0.50),
    ("Madhav Tiwari", "Delhi Capitals", "AR", 0.40),
    ("Tripurana Vijay", "Delhi Capitals", "AR", 0.30),
    ("Ajay Mandal", "Delhi Capitals", "AR", 0.30),
    ("David Miller", "Delhi Capitals", "BAT", 2.00),
    ("Ben Duckett", "Delhi Capitals", "BAT", 2.00),
    ("Lungi Ngidi", "Delhi Capitals", "BOWL", 2.00),
    ("Kyle Jamieson", "Delhi Capitals", "BOWL", 2.00),
    ("Pathum Nissanka", "Delhi Capitals", "BAT", 4.00),
    ("Prithvi Shaw", "Delhi Capitals", "BAT", 0.75),
    ("Auqib Nabi", "Delhi Capitals", "AR", 8.40),
    ("Sahil Parakh", "Delhi Capitals", "BAT", 0.30),
    # KKR
    ("Rinku Singh", "Kolkata Knight Riders", "BAT", 13.00),
    ("Sunil Narine", "Kolkata Knight Riders", "BOWL", 12.00),
    ("Varun Chakravarthy", "Kolkata Knight Riders", "BOWL", 12.00),
    ("Harshit Rana", "Kolkata Knight Riders", "BOWL", 4.00),
    ("Ramandeep Singh", "Kolkata Knight Riders", "AR", 4.00),
    ("Angkrish Raghuvanshi", "Kolkata Knight Riders", "BAT", 3.00),
    ("Vaibhav Arora", "Kolkata Knight Riders", "BOWL", 1.80),
    ("Ajinkya Rahane", "Kolkata Knight Riders", "BAT", 1.50),
    ("Rovman Powell", "Kolkata Knight Riders", "BAT", 1.50),
    ("Manish Pandey", "Kolkata Knight Riders", "BAT", 0.75),
    ("Umran Malik", "Kolkata Knight Riders", "BOWL", 0.75),
    ("Anukul Roy", "Kolkata Knight Riders", "AR", 0.40),
    ("Cameron Green", "Kolkata Knight Riders", "BAT", 25.20),
    ("Finn Allen", "Kolkata Knight Riders", "BAT", 2.00),
    ("Matheesha Pathirana", "Kolkata Knight Riders", "BOWL", 18.00),
    ("Rachin Ravindra", "Kolkata Knight Riders", "AR", 2.00),
    ("Mustafizur Rahman", "Kolkata Knight Riders", "BOWL", 9.20),
    ("Tim Seifert", "Kolkata Knight Riders", "BAT", 1.50),
    ("Rahul Tripathi", "Kolkata Knight Riders", "BAT", 0.75),
    ("Akash Deep", "Kolkata Knight Riders", "BOWL", 1.00),
    ("Kartik Tyagi", "Kolkata Knight Riders", "BOWL", 0.30),
    ("Prashant Solanki", "Kolkata Knight Riders", "BOWL", 0.30),
    ("Tejasvi Dahiya", "Kolkata Knight Riders", "BAT", 3.00),
    ("Sarthak Ranjan", "Kolkata Knight Riders", "AR", 0.30),
    ("Daksh Kamra", "Kolkata Knight Riders", "AR", 0.30),
    # RR
    ("Yashasvi Jaiswal", "Rajasthan Royals", "AR", 18.00),
    ("Ravindra Jadeja", "Rajasthan Royals", "AR", 14.00),
    ("Riyan Parag", "Rajasthan Royals", "AR", 14.00),
    ("Dhruv Jurel", "Rajasthan Royals", "BAT", 14.00),
    ("Jofra Archer", "Rajasthan Royals", "BOWL", 12.50),
    ("Shimron Hetmyer", "Rajasthan Royals", "BAT", 11.00),
    ("Tushar Deshpande", "Rajasthan Royals", "BOWL", 6.50),
    ("Sandeep Sharma", "Rajasthan Royals", "BOWL", 4.00),
    ("Nandre Burger", "Rajasthan Royals", "BOWL", 3.50),
    ("Sam Curran", "Rajasthan Royals", "AR", 2.40),
    ("Kwena Maphaka", "Rajasthan Royals", "BOWL", 1.50),
    ("Vaibhav Sooryavanshi", "Rajasthan Royals", "BAT", 1.10),
    ("Donovan Ferreira", "Rajasthan Royals", "BAT", 1.00),
    ("Shubham Dubey", "Rajasthan Royals", "BAT", 0.80),
    ("Yudhvir Singh", "Rajasthan Royals", "AR", 0.35),
    ("Lhuan-dre Pretorius", "Rajasthan Royals", "BAT", 0.30),
    ("Ravi Bishnoi", "Rajasthan Royals", "BOWL", 7.20),
    ("Adam Milne", "Rajasthan Royals", "BOWL", 2.40),
    ("Kuldeep Sen", "Rajasthan Royals", "BOWL", 0.75),
    ("Aman Rao", "Rajasthan Royals", "BAT", 0.30),
    ("Ravi Singh", "Rajasthan Royals", "BAT", 0.95),
    ("Brijesh Sharma", "Rajasthan Royals", "BOWL", 0.30),
    ("Vignesh Puthur", "Rajasthan Royals", "BOWL", 0.30),
    ("Yash Raj Punja", "Rajasthan Royals", "BOWL", 0.30),
    ("Sushant Mishra", "Rajasthan Royals", "BOWL", 0.90),
    # GT
    ("Rashid Khan", "Gujarat Titans", "BOWL", 18.00),
    ("Shubman Gill", "Gujarat Titans", "BAT", 16.50),
    ("Mohammed Siraj", "Gujarat Titans", "BOWL", 12.25),
    ("Jos Buttler", "Gujarat Titans", "BAT", 15.75),
    ("Kagiso Rabada", "Gujarat Titans", "BOWL", 10.75),
    ("Prasidh Krishna", "Gujarat Titans", "BOWL", 9.50),
    ("Sai Sudharsan", "Gujarat Titans", "BAT", 8.50),
    ("Rahul Tewatia", "Gujarat Titans", "AR", 4.00),
    ("M Shahrukh Khan", "Gujarat Titans", "AR", 4.00),
    ("Washington Sundar", "Gujarat Titans", "AR", 3.20),
    ("Glenn Phillips", "Gujarat Titans", "BAT", 2.00),
    ("Sai Kishore", "Gujarat Titans", "AR", 2.00),
    ("Arshad Khan", "Gujarat Titans", "AR", 1.30),
    ("Gurnoor Brar", "Gujarat Titans", "BOWL", 1.30),
    ("Ishant Sharma", "Gujarat Titans", "BOWL", 0.75),
    ("Jayant Yadav", "Gujarat Titans", "AR", 0.75),
    ("Kumar Kushagra", "Gujarat Titans", "BAT", 0.65),
    ("Anuj Rawat", "Gujarat Titans", "BAT", 0.30),
    ("Nishant Sindhu", "Gujarat Titans", "AR", 0.30),
    ("Manav Suthar", "Gujarat Titans", "BOWL", 0.30),
    ("Jason Holder", "Gujarat Titans", "AR", 7.00),
    ("Tom Banton", "Gujarat Titans", "BAT", 2.00),
    ("Luke Wood", "Gujarat Titans", "BOWL", 0.75),
    ("Prithvi Raj", "Gujarat Titans", "BOWL", 0.30),
    ("Ashok Sharma", "Gujarat Titans", "BOWL", 0.90),
    # LSG
    ("Rishabh Pant", "Lucknow Super Giants", "BAT", 27.00),
    ("Nicholas Pooran", "Lucknow Super Giants", "BAT", 21.00),
    ("Mayank Yadav", "Lucknow Super Giants", "BOWL", 11.00),
    ("Mohammed Shami", "Lucknow Super Giants", "BOWL", 10.00),
    ("Avesh Khan", "Lucknow Super Giants", "BOWL", 9.75),
    ("Abdul Samad", "Lucknow Super Giants", "AR", 4.20),
    ("Ayush Badoni", "Lucknow Super Giants", "AR", 4.00),
    ("Mohsin Khan", "Lucknow Super Giants", "BOWL", 4.00),
    ("Mitchell Marsh", "Lucknow Super Giants", "AR", 3.40),
    ("Shahbaz Ahmed", "Lucknow Super Giants", "AR", 2.40),
    ("Aiden Markram", "Lucknow Super Giants", "BAT", 2.00),
    ("Matthew Breetzke", "Lucknow Super Giants", "BAT", 0.75),
    ("Manimaran Siddharth", "Lucknow Super Giants", "BOWL", 0.75),
    ("Akash Singh", "Lucknow Super Giants", "BOWL", 0.30),
    ("Arjun Tendulkar", "Lucknow Super Giants", "BOWL", 0.30),
    ("Arshin Kulkarni", "Lucknow Super Giants", "AR", 0.30),
    ("Prince Yadav", "Lucknow Super Giants", "BOWL", 0.30),
    ("Digvesh Rathi", "Lucknow Super Giants", "BOWL", 0.30),
    ("Himmat Singh", "Lucknow Super Giants", "BAT", 0.30),
    ("Wanindu Hasaranga", "Lucknow Super Giants", "AR", 2.00),
    ("Anrich Nortje", "Lucknow Super Giants", "BOWL", 2.00),
    ("Josh Inglis", "Lucknow Super Giants", "BAT", 8.60),
    ("Naman Tiwari", "Lucknow Super Giants", "BOWL", 1.00),
    ("Mukul Choudhary", "Lucknow Super Giants", "BAT", 2.60),
    ("Akshat Raghuwanshi", "Lucknow Super Giants", "BAT", 2.20),
    # PBKS
    ("Shreyas Iyer", "Punjab Kings", "BAT", 26.75),
    ("Arshdeep Singh", "Punjab Kings", "BOWL", 18.00),
    ("Yuzvendra Chahal", "Punjab Kings", "BOWL", 18.00),
    ("Marcus Stoinis", "Punjab Kings", "AR", 11.00),
    ("Marco Jansen", "Punjab Kings", "AR", 7.00),
    ("Shashank Singh", "Punjab Kings", "AR", 5.50),
    ("Nehal Wadhera", "Punjab Kings", "BAT", 4.20),
    ("Prabhsimran Singh", "Punjab Kings", "BAT", 4.00),
    ("Priyansh Arya", "Punjab Kings", "BAT", 3.80),
    ("Mitchell Owen", "Punjab Kings", "AR", 3.00),
    ("Azmatullah Omarzai", "Punjab Kings", "AR", 2.40),
    ("Lockie Ferguson", "Punjab Kings", "BOWL", 2.00),
    ("Vijaykumar Vyshak", "Punjab Kings", "BOWL", 1.80),
    ("Yash Thakur", "Punjab Kings", "BOWL", 1.60),
    ("Harpreet Brar", "Punjab Kings", "AR", 1.50),
    ("Vishnu Vinod", "Punjab Kings", "BAT", 0.95),
    ("Xavier Bartlett", "Punjab Kings", "BOWL", 0.80),
    ("Pyla Avinash", "Punjab Kings", "BAT", 0.30),
    ("Harnoor Singh", "Punjab Kings", "BAT", 0.30),
    ("Suryansh Shedge", "Punjab Kings", "AR", 0.30),
    ("Musheer Khan", "Punjab Kings", "AR", 0.30),
    ("Cooper Connolly", "Punjab Kings", "AR", 3.00),
    ("Ben Dwarshuis", "Punjab Kings", "AR", 4.40),
    ("Praveen Dubey", "Punjab Kings", "BOWL", 0.30),
    ("Vishal Nishad", "Punjab Kings", "BOWL", 0.30),
]

def get_or_create_team(c, team_name):
    c.execute("SELECT id FROM teams WHERE name = ?", (team_name,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO teams (name) VALUES (?)", (team_name,))
        return c.lastrowid

def get_or_create_venue(c, venue_name, city):
    c.execute("SELECT id FROM venues WHERE name = ?", (venue_name,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO venues (name, city) VALUES (?, ?)", (venue_name, city))
        return c.lastrowid

def insert_matches(conn):
    c = conn.cursor()
    for match in SCHEDULE_2026 + PLAYOFFS:
        team1 = match['team1']
        team2 = match['team2']
        venue = match['venue']
        city = match.get('city', 'TBD')
        date = match['date']
        match_num = match['match_number']

        # Skip if team names are placeholders (like "1st placed")
        if team1 in ["1st placed", "2nd placed", "3rd placed", "4th placed", "Loser of Qualifier 1", "Winner of Eliminator", "Winner of Qualifier 1", "Winner of Qualifier 2"]:
            # For playoffs, we might want to insert later when teams are known.
            # For now, skip or insert with NULL team ids.
            continue

        team1_id = get_or_create_team(c, team1)
        team2_id = get_or_create_team(c, team2)
        venue_id = get_or_create_venue(c, venue, city)

        c.execute('''INSERT OR IGNORE INTO matches 
            (season, match_number, date, team1_id, team2_id, venue_id)
            VALUES (2026, ?, ?, ?, ?, ?)''',
            (match_num, date, team1_id, team2_id, venue_id))
    conn.commit()
    print("Matches inserted.")

def insert_players(conn):
    c = conn.cursor()
    for player_name, team_name, role, price in AUCTION_SOLD:
        team_id = get_or_create_team(c, team_name)
        # Check if player already exists; if yes, update team and price
        c.execute("SELECT id FROM players WHERE name = ?", (player_name,))
        row = c.fetchone()
        if row:
            player_id = row[0]
            c.execute("UPDATE players SET team_id = ?, role = ?, price = ? WHERE id = ?",
                      (team_id, role, price, player_id))
        else:
            c.execute('''INSERT INTO players (name, team_id, role, price) VALUES (?, ?, ?, ?)''',
                      (player_name, team_id, role, price))
    conn.commit()
    print("Players inserted.")

def main():
    conn = sqlite3.connect(DB_PATH)
    insert_matches(conn)
    insert_players(conn)
    conn.close()

if __name__ == "__main__":
    main()