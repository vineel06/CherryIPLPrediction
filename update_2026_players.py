import sqlite3
import os

DB_PATH = "data/ipl.db"

# 2026 Official Squads
PLAYERS_2026 = [
    # Chennai Super Kings (CSK)
    ("Ruturaj Gaikwad", "CSK", "BAT"),
    ("MS Dhoni", "CSK", "WK-BAT"),
    ("Sanju Samson", "CSK", "WK-BAT"),
    ("Dewald Brevis", "CSK", "BAT"),
    ("Ayush Mhatre", "CSK", "BAT"),
    ("Kartik Sharma", "CSK", "WK-BAT"),
    ("Sarfaraz Khan", "CSK", "BAT"),
    ("Urvil Patel", "CSK", "WK-BAT"),
    ("Jamie Overton", "CSK", "AR"),
    ("Ramakrishna Ghosh", "CSK", "AR"),
    ("Prashant Veer", "CSK", "AR"),
    ("Matthew William Short", "CSK", "AR"),
    ("Aman Khan", "CSK", "AR"),
    ("Zak Foulkes", "CSK", "AR"),
    ("Shivam Dube", "CSK", "AR"),
    ("Khaleel Ahmed", "CSK", "BOWL"),
    ("Noor Ahmad", "CSK", "BOWL"),
    ("Anshul Kamboj", "CSK", "BOWL"),
    ("Mukesh Choudhary", "CSK", "BOWL"),
    ("Shreyas Gopal", "CSK", "BOWL"),
    ("Gurjapneet Singh", "CSK", "BOWL"),
    ("Akeal Hosein", "CSK", "BOWL"),
    ("Matt Henry", "CSK", "BOWL"),
    ("Rahul Chahar", "CSK", "BOWL"),
    ("Spencer Johnson", "CSK", "BOWL"),

    # Delhi Capitals (DC)
    ("KL Rahul", "DC", "WK-BAT"),
    ("Karun Nair", "DC", "BAT"),
    ("David Miller", "DC", "BAT"),
    ("Ben Duckett", "DC", "WK-BAT"),
    ("Pathum Nissanka", "DC", "BAT"),
    ("Sahil Parakh", "DC", "BAT"),
    ("Prithvi Shaw", "DC", "BAT"),
    ("Abishek Porel", "DC", "WK-BAT"),
    ("Tristan Stubbs", "DC", "WK-BAT"),
    ("Axar Patel", "DC", "AR"),
    ("Sameer Rizvi", "DC", "AR"),
    ("Ashutosh Sharma", "DC", "AR"),
    ("Vipraj Nigam", "DC", "AR"),
    ("Ajay Mandal", "DC", "AR"),
    ("Tripurana Vijay", "DC", "AR"),
    ("Madhav Tiwari", "DC", "AR"),
    ("Nitish Rana", "DC", "AR"),
    ("Mitchell Starc", "DC", "BOWL"),
    ("T. Natarajan", "DC", "BOWL"),
    ("Mukesh Kumar", "DC", "BOWL"),
    ("Dushmantha Chameera", "DC", "BOWL"),
    ("Auqib Nabi", "DC", "BOWL"),
    ("Lungisani Ngidi", "DC", "BOWL"),
    ("Kyle Jamieson", "DC", "BOWL"),
    ("Kuldeep Yadav", "DC", "BOWL"),

    # Gujarat Titans (GT)
    ("Shubman Gill", "GT", "BAT"),
    ("Jos Buttler", "GT", "WK-BAT"),
    ("Kumar Kushagra", "GT", "WK-BAT"),
    ("Anuj Rawat", "GT", "WK-BAT"),
    ("Tom Banton", "GT", "WK-BAT"),
    ("Glenn Phillips", "GT", "BAT"),
    ("Sai Sudharsan", "GT", "BAT"),
    ("Nishant Sindhu", "GT", "AR"),
    ("Washington Sundar", "GT", "AR"),
    ("Mohd. Arshad Khan", "GT", "AR"),
    ("Sai Kishore", "GT", "AR"),
    ("Jayant Yadav", "GT", "AR"),
    ("Jason Holder", "GT", "AR"),
    ("Rahul Tewatia", "GT", "AR"),
    ("Shahrukh Khan", "GT", "AR"),
    ("Kagiso Rabada", "GT", "BOWL"),
    ("Mohammed Siraj", "GT", "BOWL"),
    ("Prasidh Krishna", "GT", "BOWL"),
    ("Manav Suthar", "GT", "BOWL"),
    ("Gurnoor Singh Brar", "GT", "BOWL"),
    ("Ishant Sharma", "GT", "BOWL"),
    ("Ashok Sharma", "GT", "BOWL"),
    ("Luke Wood", "GT", "BOWL"),
    ("Kulwant Khejroliya", "GT", "BOWL"),
    ("Rashid Khan", "GT", "BOWL"),

    # Kolkata Knight Riders (KKR)
    ("Ajinkya Rahane", "KKR", "BAT"),
    ("Rinku Singh", "KKR", "BAT"),
    ("Angkrish Raghuvanshi", "KKR", "BAT"),
    ("Manish Pandey", "KKR", "BAT"),
    ("Finn Allen", "KKR", "WK-BAT"),
    ("Tejasvi Singh", "KKR", "WK-BAT"),
    ("Rahul Tripathi", "KKR", "BAT"),
    ("Tim Seifert", "KKR", "WK-BAT"),
    ("Rovman Powell", "KKR", "BAT"),
    ("Anukul Roy", "KKR", "AR"),
    ("Cameron Green", "KKR", "AR"),
    ("Sarthak Ranjan", "KKR", "AR"),
    ("Daksh Kamra", "KKR", "AR"),
    ("Rachin Ravindra", "KKR", "AR"),
    ("Ramandeep Singh", "KKR", "AR"),
    ("Sunil Narine", "KKR", "AR"),
    ("Blessing Muzarabani", "KKR", "BOWL"),
    ("Vaibhav Arora", "KKR", "BOWL"),
    ("Matheesha Pathirana", "KKR", "BOWL"),
    ("Kartik Tyagi", "KKR", "BOWL"),
    ("Prashant Solanki", "KKR", "BOWL"),
    ("Saurabh Dubey", "KKR", "BOWL"),
    ("Navdeep Saini", "KKR", "BOWL"),
    ("Umran Malik", "KKR", "BOWL"),
    ("Varun Chakaravarthy", "KKR", "BOWL"),

    # Lucknow Super Giants (LSG)
    ("Rishabh Pant", "LSG", "WK-BAT"),
    ("Aiden Markram", "LSG", "BAT"),
    ("Himmat Singh", "LSG", "BAT"),
    ("Matthew Breetzke", "LSG", "BAT"),
    ("Mukul Choudhary", "LSG", "WK-BAT"),
    ("Akshat Raghuwanshi", "LSG", "BAT"),
    ("Josh Inglis", "LSG", "WK-BAT"),
    ("Nicholas Pooran", "LSG", "WK-BAT"),
    ("Mitchell Marsh", "LSG", "AR"),
    ("Abdul Samad", "LSG", "AR"),
    ("Shahbaz Ahamad", "LSG", "AR"),
    ("Arshin Kulkarni", "LSG", "AR"),
    ("Wanindu Hasaranga", "LSG", "AR"),
    ("Ayush Badoni", "LSG", "AR"),
    ("Mohammad Shami", "LSG", "BOWL"),
    ("Avesh Khan", "LSG", "BOWL"),
    ("M. Siddharth", "LSG", "BOWL"),
    ("Digvesh Singh", "LSG", "BOWL"),
    ("Akash Singh", "LSG", "BOWL"),
    ("Prince Yadav", "LSG", "BOWL"),
    ("Arjun Tendulkar", "LSG", "BOWL"),
    ("Anrich Nortje", "LSG", "BOWL"),
    ("Naman Tiwari", "LSG", "BOWL"),
    ("Mayank Yadav", "LSG", "BOWL"),
    ("Mohsin Khan", "LSG", "BOWL"),

    # Mumbai Indians (MI)
    ("Rohit Sharma", "MI", "BAT"),
    ("Surya Kumar Yadav", "MI", "BAT"),
    ("Robin Minz", "MI", "WK-BAT"),
    ("Sherfane Rutherford", "MI", "BAT"),
    ("Ryan Rickelton", "MI", "WK-BAT"),
    ("Quinton de Kock", "MI", "WK-BAT"),
    ("Danish Malewar", "MI", "BAT"),
    ("N. Tilak Varma", "MI", "BAT"),
    ("Hardik Pandya", "MI", "AR"),
    ("Naman Dhir", "MI", "AR"),
    ("Mitchell Santner", "MI", "AR"),
    ("Raj Angad Bawa", "MI", "AR"),
    ("Atharva Ankolekar", "MI", "AR"),
    ("Mayank Rawat", "MI", "AR"),
    ("Corbin Bosch", "MI", "AR"),
    ("Will Jacks", "MI", "AR"),
    ("Shardul Thakur", "MI", "AR"),
    ("Trent Boult", "MI", "BOWL"),
    ("Mayank Markande", "MI", "BOWL"),
    ("Deepak Chahar", "MI", "BOWL"),
    ("Ashwani Kumar", "MI", "BOWL"),
    ("Raghu Sharma", "MI", "BOWL"),
    ("Mohammad Izhar", "MI", "BOWL"),
    ("Allah Ghazanfar", "MI", "BOWL"),
    ("Jasprit Bumrah", "MI", "BOWL"),

    # Punjab Kings (PBKS)
    ("Shreyas Iyer", "PBKS", "BAT"),
    ("Nehal Wadhera", "PBKS", "BAT"),
    ("Vishnu Vinod", "PBKS", "WK-BAT"),
    ("Harnoor Pannu", "PBKS", "BAT"),
    ("Pyla Avinash", "PBKS", "BAT"),
    ("Prabhsimran Singh", "PBKS", "WK-BAT"),
    ("Shashank Singh", "PBKS", "BAT"),
    ("Marcus Stoinis", "PBKS", "AR"),
    ("Harpreet Brar", "PBKS", "AR"),
    ("Marco Jansen", "PBKS", "AR"),
    ("Azmatullah Omarzai", "PBKS", "AR"),
    ("Priyansh Arya", "PBKS", "AR"),
    ("Musheer Khan", "PBKS", "AR"),
    ("Suryansh Shedge", "PBKS", "AR"),
    ("Mitch Owen", "PBKS", "AR"),
    ("Cooper Connolly", "PBKS", "AR"),
    ("Ben Dwarshuis", "PBKS", "AR"),
    ("Arshdeep Singh", "PBKS", "BOWL"),
    ("Yuzvendra Chahal", "PBKS", "BOWL"),
    ("Vyshak Vijaykumar", "PBKS", "BOWL"),
    ("Yash Thakur", "PBKS", "BOWL"),
    ("Xavier Bartlett", "PBKS", "BOWL"),
    ("Pravin Dubey", "PBKS", "BOWL"),
    ("Vishal Nishad", "PBKS", "BOWL"),
    ("Lockie Ferguson", "PBKS", "BOWL"),

    # Rajasthan Royals (RR)
    ("Shubham Dubey", "RR", "BAT"),
    ("Vaibhav Suryavanshi", "RR", "BAT"),
    ("Donovan Ferreira", "RR", "WK-BAT"),
    ("Lhuan-dre Pretorious", "RR", "WK-BAT"),
    ("Ravi Singh", "RR", "WK-BAT"),
    ("Aman Rao Perala", "RR", "BAT"),
    ("Shimron Hetmyer", "RR", "BAT"),
    ("Yashasvi Jaiswal", "RR", "BAT"),
    ("Dhruv Jurel", "RR", "WK-BAT"),
    ("Riyan Parag", "RR", "AR"),
    ("Yudhvir Singh Charak", "RR", "AR"),
    ("Ravindra Jadeja", "RR", "AR"),
    ("Dasun Shanaka", "RR", "AR"),
    ("Jofra Archer", "RR", "BOWL"),
    ("Tushar Deshpande", "RR", "BOWL"),
    ("Kwena Maphaka", "RR", "BOWL"),
    ("Ravi Bishnoi", "RR", "BOWL"),
    ("Sushant Mishra", "RR", "BOWL"),
    ("Yash Raj Punja", "RR", "BOWL"),
    ("Vignesh Puthur", "RR", "BOWL"),
    ("Brijesh Sharma", "RR", "BOWL"),
    ("Adam Milne", "RR", "BOWL"),
    ("Kuldeep Sen", "RR", "BOWL"),
    ("Sandeep Sharma", "RR", "BOWL"),
    ("Nandre Burger", "RR", "BOWL"),

    # Royal Challengers Bengaluru (RCB)
    ("Rajat Patidar", "RCB", "BAT"),
    ("Devdutt Padikkal", "RCB", "BAT"),
    ("Virat Kohli", "RCB", "BAT"),
    ("Phil Salt", "RCB", "WK-BAT"),
    ("Jitesh Sharma", "RCB", "WK-BAT"),
    ("Jordan Cox", "RCB", "WK-BAT"),
    ("Krunal Pandya", "RCB", "AR"),
    ("Swapnil Singh", "RCB", "AR"),
    ("Tim David", "RCB", "AR"),
    ("Romario Shepherd", "RCB", "AR"),
    ("Jacob Bethell", "RCB", "AR"),
    ("Venkatesh Iyer", "RCB", "AR"),
    ("Satvik Deswal", "RCB", "AR"),
    ("Mangesh Yadav", "RCB", "AR"),
    ("Vicky Ostwal", "RCB", "AR"),
    ("Vihaan Malhotra", "RCB", "AR"),
    ("Kanishk Chouhan", "RCB", "AR"),
    ("Josh Hazlewood", "RCB", "BOWL"),
    ("Rasikh Dar", "RCB", "BOWL"),
    ("Suyash Sharma", "RCB", "BOWL"),
    ("Bhuvneshwar Kumar", "RCB", "BOWL"),
    ("Nuwan Thushara", "RCB", "BOWL"),
    ("Abhinandan Singh", "RCB", "BOWL"),
    ("Jacob Duffy", "RCB", "BOWL"),
    ("Yash Dayal", "RCB", "BOWL"),

    # Sunrisers Hyderabad (SRH)
    ("Ishan Kishan", "SRH", "WK-BAT"),
    ("Aniket Verma", "SRH", "BAT"),
    ("Smaran Ravichandran", "SRH", "BAT"),
    ("Salil Arora", "SRH", "WK-BAT"),
    ("Heinrich Klaasen", "SRH", "WK-BAT"),
    ("Travis Head", "SRH", "BAT"),
    ("Harshal Patel", "SRH", "AR"),
    ("Kamindu Mendis", "SRH", "AR"),
    ("Harsh Dubey", "SRH", "AR"),
    ("Brydon Carse", "SRH", "AR"),
    ("Shivang Kumar", "SRH", "AR"),
    ("Krains Fuletra", "SRH", "AR"),
    ("Liam Livingstone", "SRH", "AR"),
    ("David Payne", "SRH", "AR"),
    ("Abhishek Sharma", "SRH", "AR"),
    ("Nitish Kumar Reddy", "SRH", "AR"),
    ("Pat Cummins", "SRH", "BOWL"),
    ("Zeeshan Ansari", "SRH", "BOWL"),
    ("Jaydev Unadkat", "SRH", "BOWL"),
    ("Eshan Malinga", "SRH", "BOWL"),
    ("Sakib Hussain", "SRH", "BOWL"),
    ("Onkar Tarmale", "SRH", "BOWL"),
    ("Amit Kumar", "SRH", "BOWL"),
    ("Praful Hinge", "SRH", "BOWL"),
    ("Shivam Mavi", "SRH", "BOWL"),
]

TEAM_MAPPING = {
    "CSK": "Chennai Super Kings",
    "DC": "Delhi Capitals",
    "GT": "Gujarat Titans",
    "KKR": "Kolkata Knight Riders",
    "LSG": "Lucknow Super Giants",
    "MI": "Mumbai Indians",
    "PBKS": "Punjab Kings",
    "RR": "Rajasthan Royals",
    "RCB": "Royal Challengers Bengaluru",
    "SRH": "Sunrisers Hyderabad",
}


def update_players():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # First, clear existing players (keep historical for stats, but mark as not 2026)
    c.execute("UPDATE players SET price = NULL, role = NULL, team_id = NULL")

    # Insert 2026 players
    for player_name, team_code, role in PLAYERS_2026:
        team_name = TEAM_MAPPING[team_code]

        # Get team ID
        c.execute("SELECT id FROM teams WHERE name = ?", (team_name,))
        team_row = c.fetchone()
        if not team_row:
            c.execute("INSERT INTO teams (name) VALUES (?)", (team_name,))
            team_id = c.lastrowid
        else:
            team_id = team_row[0]

        # Check if player exists
        c.execute("SELECT id FROM players WHERE name = ?", (player_name,))
        player_row = c.fetchone()

        if player_row:
            # Update existing player
            c.execute("UPDATE players SET team_id = ?, role = ? WHERE id = ?",
                      (team_id, role, player_row[0]))
        else:
            # Insert new player
            c.execute("INSERT INTO players (name, team_id, role) VALUES (?, ?, ?)",
                      (player_name, team_id, role))

    conn.commit()
    conn.close()
    print(f"✅ Updated {len(PLAYERS_2026)} players for 2026 season")


if __name__ == "__main__":
    update_players()