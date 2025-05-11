from pymongo import MongoClient
import json

# Connect to the MongoDB server
MongoDB_Client = "" # Insert MongoDB Connection here
client = MongoClient(f"{MongoDB_Client}")

# List all databases
print(client.list_database_names())

# Access a specific DB and collection
client.drop_database("NBA")
db = client["NBA"]  # or whatever database you want
PS = db["Player_Season"]
PT = db["Player_Totals"]
TT = db["Team_Totals"]

with open("Player_Season_info.json", "r") as f:
    PS_J = [json.loads(line) for line in f]

with open("Player_Totals.json", "r") as f:
    PT_J = [json.loads(line) for line in f]

with open("Team_Totals.json", "r") as f:
    TT_J = [json.loads(line) for line in f]




PS.insert_many(PS_J)
PT.insert_many(PT_J)
TT.insert_many(TT_J)


# Indexes 
PT.create_index([("player_id", 1), ("season", 1)])  # for lookups + season filter

PS.create_index([("player_id", 1), ("season", 1)])  # for lookups + filtering
PS.create_index([("tm", 1)])                        # for filtering by team

TT.create_index([("season", 1)])                    # for seasonal queries
TT.create_index([("abbreviation", 1)])          