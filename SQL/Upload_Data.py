import pandas as pd
from sqlalchemy import create_engine, text


# Connect to MySQL
MySQL_Client = "" # Insert MySQL Connection here
engine = create_engine(f"{MySQL_Client}")

# Create a Database before hand or add code to create one


Course = pd.read_excel("Courses_with_ID.xlsx")
Course['course_id'] = pd.to_numeric(Course['course_id'], errors='coerce').astype('Int64')  # Nullable integer type
print(Course.head())
Stats = pd.read_excel("Player_Stats_with_ID.xlsx")
Stats['player_id'] = pd.to_numeric(Stats['player_id'], errors='coerce').astype('Int64')  # Nullable integer type
print(Stats.head())
Leaderboard = pd.read_excel("Top10_Final_with_TourneyCourseID.xlsx")
Leaderboard['player_id'] = pd.to_numeric(Leaderboard['player_id'], errors='coerce').astype('Int64')  # Nullable integer type
Leaderboard['tournament_id'] = pd.to_numeric(Leaderboard['tournament_id'], errors='coerce').astype('Int64') 
print(Leaderboard.head())
Tournaments = pd.read_excel("Tourney_Course_with_IDs.xlsx")
# Ensure course_id is either integer or null
Tournaments['course_id'] = pd.to_numeric(Tournaments['course_id'], errors='coerce').astype('Int64')  # Nullable integer type
Tournaments['tournament_id'] = pd.to_numeric(Tournaments['tournament_id'], errors='coerce').astype('Int64')
print(Tournaments.head())


# Upload tables to MySQL
Course.to_sql("Courses", con=engine, if_exists="replace", index=False)
Stats.to_sql("Player_stats", con=engine, if_exists="replace", index=False)
Leaderboard.to_sql("Leaderboard", con=engine, if_exists="replace", index=False)
Tournaments.to_sql("Tournament", con=engine, if_exists="replace", index=False)

with engine.connect() as conn:



    conn.execute(text("""
        ALTER TABLE Leaderboard MODIFY name VARCHAR(255);
    """))
    conn.execute(text("""ALTER TABLE Tournament MODIFY course_id INT;"""))
    conn.execute(text("""ALTER TABLE Leaderboard MODIFY player_id INT;"""))
    conn.execute(text("""ALTER TABLE Leaderboard MODIFY tournament_id INT;"""))

    conn.execute(text("""UPDATE Player_stats SET player_id = 3014 WHERE player_id = 0;"""))
    conn.execute(text("""UPDATE Leaderboard SET player_id = 3014 WHERE player_id = 0;"""))



    conn.execute(text("""ALTER TABLE Player_stats AUTO_INCREMENT = 3015;"""))
    conn.execute(text("""ALTER TABLE Tournament AUTO_INCREMENT = 529;"""))
    conn.execute(text("""ALTER TABLE Courses AUTO_INCREMENT = 100;"""))
    conn.execute(text("""ALTER TABLE Player_stats MODIFY player_id INT PRIMARY KEY AUTO_INCREMENT;"""))
    conn.execute(text("""ALTER TABLE Tournament MODIFY tournament_id INT PRIMARY KEY AUTO_INCREMENT;"""))
    conn.execute(text("""ALTER TABLE Courses MODIFY course_id INT PRIMARY KEY AUTO_INCREMENT;"""))

    conn.execute(text("""
        ALTER TABLE Tournament
        ADD FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE SET NULL;
    """))

    # Add primary key and foreign keys to Leaderboard
    conn.execute(text("""
        ALTER TABLE Leaderboard
        ADD PRIMARY KEY (name, tournament_id);
    """))

    conn.execute(text("""
        ALTER TABLE Leaderboard
        ADD FOREIGN KEY (player_id) REFERENCES Player_stats(player_id) ON DELETE SET NULL;
    """))

    conn.execute(text("""
        ALTER TABLE Leaderboard
        ADD FOREIGN KEY (tournament_id) REFERENCES Tournament(tournament_id) ON DELETE CASCADE;
    """))

    print("✅ Primary and foreign keys added.")

    print("✅ Primary and foreign keys added.")

