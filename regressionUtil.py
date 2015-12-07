import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import math

theYear = 2016
thePlayersFileName = "./players_clean" + str(theYear) + ".csv"
teamsFileName = "./teams.csv"
theDataDeviationsFileName = "./avg_std_dev_cols2015.csv"
dataToIgnore = ['player', 'team', 'date', 'home_team', 'visit_team', 'Unnamed: 0.1', 'game_id', 'Unnamed: 0', 
'away_team_losses', 'away_team_wins', 'home_team_losses', 'home_team_wins', 'home_win_pct', 'away_win_pct']


thePlayers = pd.read_csv(thePlayersFileName)
theTeams = pd.read_csv(teamsFileName)
theDataDeviations = pd.read_csv(theDataDeviationsFileName)
recordAverage = theDataDeviations['team_win_pct'][0]
recordStdDev = theDataDeviations['team_win_pct'][1]

def cleanPlayerData(aPlayer, players):
	playerData = players.loc[players['player'] == aPlayer]
	playerData = playerData.drop(dataToIgnore, axis=1)
	# Gets rid of rows where the player didn't play
	playerData = playerData[np.isfinite(playerData['MIN'])]
	return playerData

def getTeamRecord(teamAbbrev):
	teamAbbrev = teamAbbrev.lower()
	if teamAbbrev == 'was': teamAbbrev = 'wsh'
	if teamAbbrev =='pho': teamAbbrev = 'phx'

	teamNameIndex = theTeams.loc[theTeams['prefix_1'] == teamAbbrev].index.tolist()[0]
	teamName = theTeams.iloc[teamNameIndex]['team']
	teamData = thePlayers.loc[thePlayers['home_team'] == teamName]
	teamWins = teamData['home_team_wins'].max()
	teamLosses = teamData['home_team_losses'].max()
	otherTeamData = thePlayers.loc[thePlayers['visit_team'] == teamName]
	teamWins = max(otherTeamData['away_team_wins'].max(), teamWins)
	teamLosses = max(otherTeamData['away_team_losses'].max(), teamLosses)
	winPercentage = float(teamWins)/(teamWins + teamLosses)
	winPercentage = (winPercentage - recordAverage)/recordStdDev
	return winPercentage





# def runTrainOrTest(playerData, trainBool, predictBool, toOutput):
# 	numElems = len(playerData)
# 	# Note that a player's information is not super useful if they played only in a few games
# 	if numElems > minGames:
# 		for k in xrange(numPreviousGamesToConsider, numElems):
# 			trainData = playerData.iloc[k-numPreviousGamesToConsider:k]
# 			DKPoints = playerData.iloc[k]['DKPoints']
# 			DKPointsForTest = playerData.iloc[k]['DKPointsOriginal']
# 			trainData = trainData.drop('DKPointsOriginal', axis=1)

# 			if DKPointsForTest > minPoints:

# 				playerAverages = trainData.mean()

# 				# toConsider = 'DKPoints'
# 				# for i in xrange(0, numPreviousGamesToConsider):
# 				# 	playerAverages[toConsider + str(i)] = trainData.iloc[i][toConsider]

# 				# columns = trainData.columns.values.tolist()
# 				# for col in columns:
# 				# 	for i in xrange(4, numPreviousGamesToConsider):
# 				# 		playerAverages[col + str(i)] = trainData.iloc[i][col]

# 				for newRow in currGameData:
# 					playerAverages[newRow + 'Curr'] = playerData.iloc[k][newRow]

# 				headers = playerAverages.axes[0]

# 				hFunction = np.dot(playerAverages, theta)
# 				if predictBool:
# 					return convertBack(hFunction)

# 				if trainBool:
# 					for i in xrange(0, len(theta)):
# 						theta[i] = theta[i] + alpha*(convertBack(DKPoints) - convertBack(hFunction))*playerAverages[i]
# 				else:
# 					diff = convertBack(DKPoints) - convertBack(hFunction)
# 					pctError = abs(diff)/convertBack(DKPoints)
# 					# print "%s Predicted Points: %f  Actual Points %f Diff %f Error %f" 
# 					# % (aPlayer, convertBack(hFunction), convertBack(DKPoints), diff, pctError)
# 					toOutput.append([aPlayer, convertBack(hFunction), convertBack(DKPoints), diff, pctError])
