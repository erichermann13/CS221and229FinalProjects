import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import math
from scipy.spatial import distance
import copy

year = 2015

playersFile = './players_clean' + str(year) + '.csv'
outputFileName = './predictorData' + str(year) + '.csv'

dataDeviationsFileName = "./avg_std_dev_cols" + str(year) + ".csv"

quantileDataFile = "./quantileData.csv"

data = pd.read_csv(playersFile)

quantiles = pd.read_csv(quantileDataFile)

dataDeviations = pd.read_csv(dataDeviationsFileName)
pointsAverage = dataDeviations['DKPoints'][0]
pointsStdDev = dataDeviations['DKPoints'][1]

playerNames = data['player']
uniquePlayers = pd.unique(playerNames)

numPlayers = len(uniquePlayers)
trainFraction = 3.0/4
minGames = 20
numPreviousGamesToConsider = 5

discretizedStates = [1]

trainPlayers = uniquePlayers[0:(numPlayers*trainFraction)]
testPlayers = uniquePlayers[(numPlayers*trainFraction):]

dataToConsider = ['+/-', '3PA', '3PM', 'AST', 'BLK', 'DKPoints', 'DREB', 'FGA', 'FGM', 'FTA', 'FTM', 
'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TO', 'home_team_score', 'visit_team_score', 'Home', 'home_win_pct', 
'away_win_pct', 'team_win_pct', 'opponent_win_pct']
toRemove = ['home_team_score', 'visit_team_score', 'Home', 'home_win_pct', 'away_win_pct', 'team_win_pct', 'opponent_win_pct']
dataToConsider = [x for x in dataToConsider if x not in toRemove]
moarToRemove = ['+/-', '3PA', '3PM', 'FGM', 'FTA', 'FTM', 'OREB']
dataToConsider = [x for x in dataToConsider if x not in moarToRemove]
dataToConsider = ['DKPoints', 'AST', 'DKPoints', 'BLK', 'MIN']

allData = data.axes[1].get_values()
# print allData
dataToIgnore = [x for x in allData if x not in dataToConsider]
# print dataToIgnore

bayesDict = {}

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

			playerAverages = trainData.mean()
			dictKey = []
			for value in dataToConsider:
				playerValue = playerAverages[value]
				toCompare = quantiles.loc[quantiles['Stat'] == value]
				quantile = 0
				for i in xrange(1, len(toCompare.columns)):
					currQuantileValue = toCompare.iloc[0][i]
					if playerValue > currQuantileValue:
						quantile += 1
					else: break
				dictKey.append((value, quantile))

			dictKey = tuple(dictKey)


			# for newRow in currGameData:
			# 	playerAverages[newRow + 'Curr'] = playerData.iloc[k][newRow]
			convertedDKPoints = convertBack(DKPoints)

			if trainBool:
				if dictKey in bayesDict:
					val = bayesDict[dictKey]
					val[1] = (val[1]*val[0] + convertedDKPoints)/(val[0] + 1)
					val[0] = val[0] + 1
					bayesDict[dictKey] = val

				else:
					val = [1, convertedDKPoints]
					bayesDict[dictKey] = val
			else:
				predictedPoints = 0
				if dictKey in bayesDict:
					predictedPoints = bayesDict[dictKey][1]
				diff = abs(predictedPoints - convertedDKPoints)
				if convertedDKPoints > discretizedStates[0]:
					pctError = diff/convertedDKPoints
					toOutput.append([aPlayer, predictedPoints, convertedDKPoints, diff, pctError])




# Train
for aPlayer in trainPlayers:
	print aPlayer
	playerData = cleanPlayerData(aPlayer)
	runTrainOrTest(playerData, True, None)

# See how well you did
toStore = []

for aPlayer in testPlayers:
	playerData = cleanPlayerData(aPlayer)
	runTrainOrTest(playerData, False, toStore)

# trainToStore = []

# for aPlayer in trainPlayers:
# 	playerData = cleanPlayerData(aPlayer)
# 	runTrainOrTest(playerData, False, trainToStore)

def getAverageError(storedElems):
	averageError = 0.0
	averageDiff = 0.0
	errorWithoutZeros = 0.0
	diffWithoutZeros = 0.0
	errorsAndDiffsAbove = [[0.0, 0.0]]*len(discretizedStates)
	numAtLevel = [0]*len(discretizedStates)
	numNonZeros = 0
	percentNonZeros = 0.0
	numElems = len(storedElems)
	for elem in storedElems:
		averageError += elem[4]
		averageDiff += elem[3]

		if elem[1] != 0:
			errorWithoutZeros += elem[4]
			diffWithoutZeros += elem[3]
			numNonZeros += 1
			for i in xrange(0, len(discretizedStates)):
				if elem[2] > discretizedStates[i]:
					numAtLevel[i] += 1
					toAppend = errorsAndDiffsAbove[i]
					toAppend[0] = toAppend[0] + elem[4]
					toAppend[1] = toAppend[1] + elem[3]
					errorsAndDiffsAbove[i] = toAppend

	averageError /= numElems
	averageDiff /= numElems

	if numNonZeros != 0:
		errorWithoutZeros /= numNonZeros
		diffWithoutZeros /= numNonZeros
		percentNonZeros = float(numNonZeros)/numElems

		for j in xrange(0, len(discretizedStates)):
			currErrorLevel = errorsAndDiffsAbove[j]
			print numAtLevel[j]
			numAtLevel[j] = 1
			currErrorLevel[0] /= numAtLevel[j]
			currErrorLevel[1] /= numAtLevel[j]
			errorsAndDiffsAbove[j] = currErrorLevel

	return (averageError, averageDiff, errorWithoutZeros, diffWithoutZeros, percentNonZeros, errorsAndDiffsAbove)

# trainError = getAverageError(trainToStore)
testError = getAverageError(toStore)

# print "Average Train Error: %f AverageDiff: %f" % (trainError[0], trainError[1])
print "Average Test Error: %f Average Diff: %f Without Zeros Error: %f Without Zeros Diff: %f Percent \
Non Zeros: %f" % (testError[0], testError[1], testError[2], testError[3], testError[4])

print testError[5]

outfile = open(outputFileName, 'wb')
writer = csv.writer(outfile)
writer.writerow(['Player Name', 'Predicted Points', 'Actual Points', "Difference", "Pct Error"])
writer.writerows(toStore)






