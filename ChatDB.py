# Imports 
from openai import OpenAI
from sqlalchemy import create_engine, text
from pymongo import MongoClient
import json

# Insert Connections and API key here
openAI_Key = "" # Insert key here
MongoDB_Client = "" # Insert MongoDB Connection here
MySQL_Client = "" # Insert MySQL Connection here


# Establish connections to the databases and clients
client = OpenAI(api_key=f"{openAI_Key}")
mongo_client = MongoClient(f"{MongoDB_Client}")
sql_conn = create_engine(f"{MySQL_Client}")


# TODO: Input database schema 
def mysql_query(prompt, model='gpt-4o'):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system',
            'content': """
                    This is the schema for a MySQL database, write queries for the specified questions and return the query and nothing else.
                    courses(Primary key course_id, course, par, yardage, yardage_4_5, yardage_3, adj_score_to_par, adj_par_3_score, adj_par_4_score, adj_par_5_score, adj_driving_distance, adj_sd_distance, adj_driving_accuracy, putt_sg)
                    Tournament( Primary key tournament_id, tournament, course, year, course_id
                        FOREIGN KEY (course_id) REFERENCES Courses(course_id))
                    Player_stats(Primary key player_id, name, year, events_played, first_place, second_place, third_place, top_10, top_25, drive_avg, drive_acc, putt_avg, sand_saves_pct, birdies_per_round, holes_per_eagle, scoring_avg, strokes_gained_tee_green, strokes_gained_total, total_driving)
                    Leaderboard(Primary key (name, tournament_id), name, finish, year, player_id, tournament_id,
                        FOREIGN KEY (player_id) REFERENCES Player_stats(player_id) ON DELETE SET NULL
                        FOREIGN KEY (tournament_id) REFERENCES Tournament(tournament_id) ON DELETE CASCADE
                    Note: For Leaderboard (finish) if players were tied for a position there will be a T in front of the position. Example tied for 2 would be indicated as T2 and no tie would just be 2, leaderboard only includes the top 10 players.
                    course_id, player_id, tournament_id are on autoincrement so no need to include them in the insert statements.
                    Return ONLY the raw query and NOTHING else. Do NOT use markdown formatting like ```sql.
                    Account for multiple tables having the same column names. Use the table name as a prefix to the column name. For example, if both tables have a column called "name", use "Player_stats.name" and "Leaderboard.name".
                    """},
            {'role': 'user',
            'content': prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def mongodb_query(prompt, model='gpt-4o'):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system',
            'content':  """

                    You are a MongoDB query generator. Based on a user's natural language question, Return only a valid JSON object, using double quotes for all keys and strings. Do not return Python-style dictionaries.
                    In find queries, make sure to add the projection step to return only the fields that are needed. The projection should be included in the filter key and never include object ids. For example, if you want to return only the player name and points, use: {"player": 1, "pts": 1}. The filter key should contain the query conditions. The sort key should be a list of tuples with field names and directions (1 for ascending, -1 for descending). The limit key should be an integer.
                    The DB may have duplicates so be sure to use distinct or limit where appropriate. The JSON object should contain the following keys:

                        Valid keys include:
                        - type: "find", "aggregate", "update", "insert", or "delete"
                        - collection: (string)
                        - filter: (object)
                        - sort: list of [field, direction]
                        - limit: integer
                        - pipeline: array of aggregation stages, always include projection when using aggregate
                        - update: update object
                        - document: document to insert
                        - projection: projection object, always project object ids as 0 example: {"_id": 0, "player": 1, "pts": 1}

                        Return only valid single JSON. Do not include markdown, triple backticks, or any extra explanation.
                        If the user request includes multiple related pieces of information about the same entity (e.g., a player's stats and teams), return a single aggregation pipeline that combines all requested information using $lookup and $group. Do not return multiple separate JSON objects.

                        Always include a 'collection' key to specify which MongoDB collection to use.

                        Examples:

                        User: Get the top 5 players by points in 2023  
                        Output:
                        {
                        'type': 'find',
                        'collection': 'Player_Totals',
                        'filter': {'season': 2023},
                        'sort': {'pts': -1},
                        'limit': 5
                        }

                        User: What was the average points per player in 2023?  
                        Output:
                        {
                        'type': 'aggregate',
                        'collection': 'Player_Totals',
                        'pipeline': [
                            {'$match': {'season': 2023}},
                            {'$group': {'_id': '$player', 'avg_pts': {'$avg': '$pts'}}}
                        ]
                        }
                    This is the schema, the database is a collection of basketball statistics and player/team information. The collections are as follows:
                    Collections:

                    Player_Season, Example ({"season":1947,"player_id":1,"player":"Al Brightman","pos":"F","age":23.0,"lg":"BAA","tm":"BOS","experience":1})

                    Player_Totals, Example ({"season":2025,"player_id":5025.0,"player":"A.J. Green","g":66,"gs":6.0,"mp":1495.0,"fg":164,"fga":388,"fg_percent":0.423,"x3p":138.0,"x3pa":333.0,"x3p_percent":0.414,"x2p":26,"x2pa":55,"x2p_percent":0.473,"ft":20,"fta":24,"ft_percent":0.833,"orb":16.0,"drb":134.0,"trb":150.0,"ast":97,"stl":36.0,"blk":6.0,"tov":37.0,"pf":144,"pts":486})

                    Team_Totals, Example ({"season":2025,"lg":"NBA","team":"Atlanta Hawks","abbreviation":"ATL","playoffs":false,"g":74.0,"mp":17860.0,"fg":3198.0,"fga":6802.0,"fg_percent":0.47,"x3p":987.0,"x3pa":2773.0,"x3p_percent":0.356,"x2p":2211.0,"x2pa":4029.0,"x2p_percent":0.549,"ft":1339.0,"fta":1729.0,"ft_percent":0.774,"orb":882.0,"drb":2410.0,"trb":3292.0,"ast":2183.0,"stl":726.0,"blk":384.0,"tov":1151.0,"pf":1411.0,"pts":8722.0})

                    Note: In the Team_Totals team is the full name and abbreviation is what you want to use when join with Player_Season. abbreviation in Team_Totals corresponds to tm in Player_Season. Player tm is not located in Player_Totals, you have to get that from Player_Season
                    Note: Season totals are located in the Player_Totals for each season, do not sum points unless the user specifically asks for it accross seasons.
                    

                    

                    If user is requesting schema information, return a string with the requested information and not a json object else return a json object.

                    Do not return markdown or any other formatting. Do not include any extra information or explanations. Do not include the word "query" in your response.
                    """ },
            {'role': 'user',
            'content': prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# TODO: Database functions
def sql_func(prompt):
    query = mysql_query(prompt)
    print(f'Your request translated into a query: {query}')
    if any(word in query.lower() for word in ['insert', 'update', 'delete']):
        try:
            with sql_conn.begin() as conn:
                conn.execute(text(query))
            print('The Database has successfully been modified.')
        except Exception as e:
            print(f'An error occurred: {e}')
            return e
    else:
        # TODO: Pass query to database
        with sql_conn.connect() as conn:
            result_obj = conn.execute(text(query))
        # TODO: Return result?
        result = list(result_obj)
        if len(result) == 0:
            print('No results found or no data to return.')
        else:
            print(f'Your requested information: {result}')
            return result_obj.fetchall()

def mongodb_func(prompt):
    raw_query = mongodb_query(prompt)
    print(type(raw_query))
    try:
        query = json.loads(raw_query)
        print(f'Your request translated into a query: {query}')
        # TODO: pass query to database
        db = mongo_client['NBA']
        collection = db[query["collection"]]
        if query["type"] == "aggregate":
            cursor = collection.aggregate(query["pipeline"])
            result = list(cursor)
            print(f'Your requested information: {result}')

        elif query["type"] == "update":
            result = collection.update_many(query["filter"], query["update"])
            print(f'Updated {result.modified_count} documents.')
            return result.modified_count
        
        elif query["type"] == "insert":
            if isinstance(query["document"], dict):
                result = collection.insert_one(query["document"])
                print(f'Inserted document with id: {result.inserted_id}')
            else:
                result = collection.insert_many(query["document"])
                print(f'Inserted {len(result.inserted_ids)} documents with ids: {result.inserted_ids}')

        elif query["type"] == "delete":
            result = collection.delete_many(query["filter"])
            print(f'Deleted {result.deleted_count} documents.')
            return result.deleted_count

        else:
            cursor = collection.find(query["filter"],  query["projection"])
            if "sort" in query and query['sort']  != []:
                cursor = cursor.sort(query["sort"])
            if "limit" in query and query['limit']  != 0:
                cursor = cursor.limit(query["limit"])

            result = list(cursor)
            if len(result) == 0:
                print('No results found or no data to return.')
            else:
                print(f'Your requested information: {result}')
                return result
    except json.JSONDecodeError as e:
        print(raw_query)
        return raw_query



    
def intro():
    db_type = input('Welcome to SportsDB! Would you like to know about golf or basketball? (type "exit" to quit) > ').lower().strip()
    
    while db_type not in ['basketball', 'golf', 'exit']:
        db_type = input('Please only enter either "basketball" or "golf". > ').lower().strip()

    return db_type

def main():
    db_type = intro()

    while db_type != 'exit':
        prompt = ''
        while prompt != 'exit':
            if db_type not in ['basketball', 'golf']:
                db_type = input('Please only enter either "basketball" or "golf".').lower().strip()

            if db_type == 'golf':
                prompt = input('What golf data would you like to know? Or what would you like to modify about the golf database?')
                if prompt != 'exit':
                    sql_func(prompt)
            else:
                prompt = input('What basketball data would you like to know? Or what would you like to modify about the basketball database?')
                if prompt != 'exit':
                    mongodb_func(prompt)
        db_type = intro()
    print('Thanks for using SportsDB!')
   

if __name__ == "__main__":
    main()



