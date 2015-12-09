import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np

year = 2015

playersFile = './players' + str(year) + '.csv'
outputFile = './players_clean' + str(year) + '.csv'
columnDataOutputFile = './avg_std_dev_cols' + str(year) + '.csv'

playerRiskinessFile = './players_riskiness' + str(year) + '.csv'

players = pd.read_csv(playersFile)

players['date'] = pd.to_datetime(players.date)

players = players.sort('date')

# Home column will be 1 if the player was on the home team, 0 otherwise
players['Home'] = np.where(players['team'] == players['home_team'], 1, 0)

colsToDrop = ['game_id', 'id', 'Unnamed: 0']

players = players.drop(colsToDrop, axis=1)

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

# Find the mean and stdDev for each player
playerMeanStdDevData = []
playerNames = players['player']
uniquePlayers = pd.unique(playerNames)
for aPlayer in uniquePlayers:
	playerData = players.loc[players['player'] == aPlayer]
	pointsCol = playerData['DKPoints']
	average = pointsCol.mean()
	stdDev = pointsCol.std()
	playerMeanStdDevData.append([aPlayer, average, stdDev, stdDev/average, 0.0])

overallPointsAverage = 0.0
overallPointsStdDev = 0.0

# Center the columns
for col in colsToCenter:
	if col == 'DKPoints':
		players['DKPointsOriginal'] = players[col]
	currColumn = players[col]
	average = currColumn.mean()
	stdDev = currColumn.std()
	if col == 'DKPoints':
		overallPointsAverage = average
		overallPointsStdDev = stdDev
	print "Column %s, Average %f, stdDev %f" % (col, average, stdDev)
	currColumn -= average
	currColumn /= stdDev
	players[col] = currColumn
	columnAverages.append(average)
	columnStdDevs.append(stdDev)

averageRatio = overallPointsStdDev/overallPointsAverage

for onePlayer in playerMeanStdDevData:
	playerRatio = onePlayer[3]
	onePlayer[4] = playerRatio/averageRatio

players['const'] = 1

outfile = open(columnDataOutputFile, 'wb')
writer = csv.writer(outfile)
writer.writerow(['Statistic:'] + colsToCenter)
writer.writerow(['Averages:'] + columnAverages)
writer.writerow(['Std Devs:'] + columnStdDevs)

outfile = open(playerRiskinessFile, 'wb')
writer = csv.writer(outfile)
writer.writerow(['player', 'avg_points', 'std_dev_points', 'std_avg_ratio', 'riskiness_ratio'])
writer.writerows(playerMeanStdDevData)

quantileData = []
numQuantiles = 5
quantileData.append(['Stat'] + [j for j in xrange(0, numQuantiles + 1)])
for col in colsToCenter:
	toLookAt = players[col]
	quantilePlaces = []
	for i in xrange(0, numQuantiles + 1):
		quantilePlaces.append(toLookAt.quantile((1/float(numQuantiles))*i))
	# print quantilePlaces
	quantileData.append([col] + quantilePlaces)

outfile = open("./quantileData.csv", "wb")
writer = csv.writer(outfile)
writer.writerows(quantileData)

players.to_csv(outputFile)





