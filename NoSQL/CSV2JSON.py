import pandas as pd


# The ouptut JSON files are already included in the folder so no need to run this

PSI = pd.read_csv('Player Season Info.csv')
PSI = PSI.drop(columns=['birth_year'])
json = PSI.to_json('Player_Season_Info.json', orient='records', lines=True)

PT = pd.read_csv('Player Totals.csv')
json_PT = PT.to_json('Player_Totals.json', orient='records', lines=True)

TT = pd.read_csv('Team Totals.csv')
json_TT = TT.to_json('Team_Totals.json', orient='records', lines=True)

