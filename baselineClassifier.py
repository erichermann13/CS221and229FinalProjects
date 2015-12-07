import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import math

year = 2015

playersFile = './players_clean' + str(year) + '.csv'
outputFileName = './predictorData' + str(year) + '.csv'

dataDeviationsFileName = "./avg_std_dev_cols" + str(year) + ".csv"

thetaFileName = './modelParameters.csv'

data = pd.read_csv(playersFile)

dataDeviations = pd.read_csv(dataDeviationsFileName)
pointsAverage = dataDeviations['DKPoints'][0]
pointsStdDev = dataDeviations['DKPoints'][1]

playerNames = data['player']
uniquePlayers = pd.unique(playerNames)

numPlayers = len(uniquePlayers)
trainFraction = 3.0/4
minGames = 20
minPoints = 20
numPreviousGamesToConsider = 5
numIterations = 5

trainPlayers = uniquePlayers[0:(numPlayers*trainFraction)]
testPlayers = uniquePlayers[(numPlayers*trainFraction):]

dataToIgnore = ['player', 'team', 'date', 'home_team', 'visit_team', 'Unnamed: 0.1', 'game_id', '+/-', 'Unnamed: 0', 
'away_team_losses', 'away_team_wins', 'home_team_losses', 'home_team_score', 'home_team_wins', 'visit_team_score']
newDataToIgnore = ['player', 'team', 'date', 'home_team', 'visit_team', 'Unnamed: 0.1', 'game_id', 'Unnamed: 0', 
'away_team_losses', 'away_team_wins', 'home_team_losses', 'home_team_wins', 'home_win_pct', 'away_win_pct']

playerBoxScoreData = ['+/-', '3PA', '3PM', 'AST', 'BLK', 'DKPoints', 'DREB', 'FGA', 'FGM', 'FTA', 'FTM', 
'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TO']
teamBoxScoreData = ['home_team_score', 'visit_team_score', 'Home',
'team_win_pct', 'opponent_win_pct']
# Note that some data is really relevant for the current game being played
currGameData = ['Home', 'team_win_pct', 'opponent_win_pct']

dataToIgnore = newDataToIgnore

theta = [0]*((len(data.iloc[0]) - (len(dataToIgnore)+1)) + len(currGameData))
alpha = 0.00005
headers = []

def convertBack(number):
	return number*pointsStdDev + pointsAverage

def cleanPlayerData(aPlayer):
	playerData = data.loc[data['player'] == aPlayer]
	playerData = playerData.drop(dataToIgnore, axis=1)
	# Gets rid of rows where the player didn't play
	playerData = playerData[np.isfinite(playerData['MIN'])]
	return playerData

def runTrainOrTest(playerData, trainBool, toOutput):
	numElems = len(playerData)
	# Note that a player's information is not super useful if they played only in a few games
	if numElems > minGames:
		for k in xrange(numPreviousGamesToConsider, numElems):
			trainData = playerData.iloc[k-numPreviousGamesToConsider:k]
			DKPoints = playerData.iloc[k]['DKPoints']
			DKPointsForTest = playerData.iloc[k]['DKPointsOriginal']
			trainData = trainData.drop('DKPointsOriginal', axis=1)

			if DKPointsForTest > minPoints:

				playerAverages = trainData.mean()

				# toConsider = 'DKPoints'
				# for i in xrange(0, numPreviousGamesToConsider):
				# 	playerAverages[toConsider + str(i)] = trainData.iloc[i][toConsider]

				# columns = trainData.columns.values.tolist()
				# for col in columns:
				# 	for i in xrange(4, numPreviousGamesToConsider):
				# 		playerAverages[col + str(i)] = trainData.iloc[i][col]

				for newRow in currGameData:
					playerAverages[newRow + 'Curr'] = playerData.iloc[k][newRow]

				headers = playerAverages.axes[0]

				hFunction = np.dot(playerAverages, theta)
				if trainBool:
					for i in xrange(0, len(theta)):
						theta[i] = theta[i] + alpha*(convertBack(DKPoints) - convertBack(hFunction))*playerAverages[i]
				else:
					diff = convertBack(DKPoints) - convertBack(hFunction)
					pctError = abs(diff)/convertBack(DKPoints)
					# print "%s Predicted Points: %f  Actual Points %f Diff %f Error %f" 
					# % (aPlayer, convertBack(hFunction), convertBack(DKPoints), diff, pctError)
					toOutput.append([aPlayer, convertBack(hFunction), convertBack(DKPoints), diff, pctError])




# Train
for j in xrange(0, numIterations):
	for aPlayer in trainPlayers:
		playerData = cleanPlayerData(aPlayer)
		# print aPlayer
		runTrainOrTest(playerData, True, None)

	print j
	print theta

# See how well you did
toStore = []

for aPlayer in testPlayers:
	playerData = cleanPlayerData(aPlayer)
	runTrainOrTest(playerData, False, toStore)

trainToStore = []

for aPlayer in trainPlayers:
	playerData = cleanPlayerData(aPlayer)
	runTrainOrTest(playerData, False, trainToStore)

def getAverageError(storedElems):
	averageError = 0.0
	numElems = len(storedElems)
	for elem in storedElems:
		averageError += elem[4]
	averageError /= numElems
	return averageError


print "Average Train Error: %f" % getAverageError(trainToStore)
print "Average Test Error: %f" % getAverageError(toStore)

outfile = open(outputFileName, 'wb')
writer = csv.writer(outfile)
writer.writerow(['Player Name', 'Predicted Points', 'Actual Points', "Difference", "Pct Error"])
writer.writerows(toStore)

newHeaders = []
for val in headers:
	newHeaders.append(val)
headers = newHeaders

headers = ['+/-', '3PA', '3PM', 'AST', 'BLK', 'DKPoints', 'DREB', 'FGA', 'FGM', 'FTA', 'FTM', 'MIN', 'OREB', 
'PF', 'PTS', 'REB', 'STL', 'TO', 'home_team_score', 'visit_team_score', 'Home', 'team_win_pct', 'opponent_win_pct', 
'HomeCurr', 'team_win_pctCurr', 'opponent_win_pctCurr']

newOutfile = open(thetaFileName, 'wb')
writer = csv.writer(newOutfile)
writer.writerow(headers)
writer.writerow(theta)






