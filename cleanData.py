import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np

year = 2016

playersFile = './players' + str(year) + '.csv'
outputFile = './players_clean' + str(year) + '.csv'
columnDataOutputFile = './avg_std_dev_cols' + str(year) + '.csv'

players = pd.read_csv(playersFile)

players['date'] = pd.to_datetime(players.date)

players = players.sort('date')

# Home column will be 1 if the player was on the home team, 0 otherwise
players['Home'] = np.where(players['team'] == players['home_team'], 1, 0)

del players['id']

# Change: I'm centering the data with 0 mean and dividing by standard deviation

colsToCenter = ['+/-', '3PA', '3PM', 'AST', 'BLK', 'DKPoints', 'DREB', 'FGA', 'FGM', 'FTA', 'FTM', 
'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TO', 
'home_team_score', 'visit_team_score', 'Home', 'home_win_pct', 'away_win_pct', 'team_win_pct', 'opponent_win_pct']

homeWinPercentageCol = players['home_team_wins']/(players['home_team_losses'] + players['home_team_wins'])
awayWinPercentageCol = players['away_team_wins']/(players['away_team_losses'] + players['away_team_wins'])

players['home_win_pct'] = homeWinPercentageCol
players['away_win_pct'] = awayWinPercentageCol

players['home_intermediary'] = players['Home']*players['home_win_pct']
players['away_intermediary'] = (1 - players["Home"])*players['away_win_pct']

players['team_win_pct'] = players[['home_intermediary', 'away_intermediary']].max(axis=1)

players['opp_home_intermediary'] = (1 - players["Home"])*players['home_win_pct']
players['opp_away_intermediary'] = players['Home']*players['away_win_pct']

players['opponent_win_pct'] = players[['opp_home_intermediary', 'opp_away_intermediary']].max(axis=1)

toDrop = ['home_intermediary', 'away_intermediary', 'opp_home_intermediary', 'opp_away_intermediary']

players = players.drop(toDrop, axis=1)

columnAverages = []
columnStdDevs = []

for col in colsToCenter:
	if col == 'DKPoints':
		players['DKPointsOriginal'] = players[col]
	currColumn = players[col]
	average = currColumn.mean()
	stdDev = currColumn.std()
	print "Column %s, Average %f, stdDev %f" % (col, average, stdDev)
	currColumn -= average
	currColumn /= stdDev
	players[col] = currColumn
	columnAverages.append(average)
	columnStdDevs.append(stdDev)

# print players

outfile = open(columnDataOutputFile, 'wb')
writer = csv.writer(outfile)
writer.writerow(['Statistic:'] + colsToCenter)
writer.writerow(['Averages:'] + columnAverages)
writer.writerow(['Std Devs:'] + columnStdDevs)

players.to_csv(outputFile)





