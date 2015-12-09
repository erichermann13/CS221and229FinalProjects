import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import math
from scipy.spatial import distance
import copy
import predictionParameters

year = predictionParameters.trainYear

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
numPreviousGamesToConsider = predictionParameters.numPreviousGamesToConsider
numIterations = 20
convergenceConstant = 0.05

discretizedStates = predictionParameters.discretizedStates

trainPlayers = uniquePlayers[0:(numPlayers*trainFraction)]
testPlayers = uniquePlayers[(numPlayers*trainFraction):]

dataToIgnore = predictionParameters.dataToIgnore

playerBoxScoreData = ['+/-', '3PA', '3PM', 'AST', 'BLK', 'DKPoints', 'DREB', 'FGA', 'FGM', 'FTA', 'FTM', 
'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TO']
teamBoxScoreData = ['home_team_score', 'visit_team_score', 'Home',
'team_win_pct', 'opponent_win_pct']
# Note that some data is really relevant for the current game being played
currGameData = ['Home', 'team_win_pct', 'opponent_win_pct']

thetaInterior = [0]*((len(data.iloc[0]) - (len(dataToIgnore)+1)) + len(currGameData))
theta = []
for i in xrange(0, len(discretizedStates)):
	theta.append(copy.deepcopy(thetaInterior))

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
			DKPointsForTest = trainData['DKPointsOriginal'].mean()
			trainData = trainData.drop('DKPointsOriginal', axis=1)

			bucket = -1
			while DKPointsForTest > discretizedStates[bucket + 1]:
				bucket += 1
				if bucket == len(discretizedStates)-1: break

			if bucket != -1:
				thetaToReview = theta[bucket]

				playerAverages = trainData.mean()

				for newRow in currGameData:
					playerAverages[newRow + 'Curr'] = playerData.iloc[k][newRow]

				# headers = playerAverages.axes[0]
				# print headers

				hFunction = np.dot(playerAverages, thetaToReview)
				convertedDKPoints = convertBack(DKPoints)
				convertedHFunction = convertBack(hFunction)
				if trainBool:
					for i in xrange(0, len(thetaToReview)):
						thetaToReview[i] = thetaToReview[i] + alpha*(convertedDKPoints - convertedHFunction)*playerAverages[i]
				else:
					diff = abs(convertedDKPoints - convertedHFunction)
					if convertedDKPoints > discretizedStates[0]:
						pctError = abs(diff)/convertedDKPoints
						toOutput.append([aPlayer, convertedHFunction, convertedDKPoints, diff, pctError])




# Train
for j in xrange(0, numIterations):
	thetaCurr = copy.deepcopy(theta)
	for aPlayer in trainPlayers:
		playerData = cleanPlayerData(aPlayer)
		runTrainOrTest(playerData, True, None)

	print "Iteration %d" % j
	intermediateDistance = []
	intermediateTotalLength = []
	for i in xrange(0, len(theta)):
		intermediateDistance.append(distance.euclidean(thetaCurr[i], theta[i]))
		intermediateTotalLength.append(distance.euclidean(0, theta[i]))
	dist = distance.euclidean(0, intermediateDistance)
	totalLength = distance.euclidean(0, intermediateTotalLength)
	diff = dist/totalLength
	print "Euclidean Dist: %f Diff: %f" % (dist, diff)
	print theta
	if diff < convergenceConstant: break

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
	averageDiff = 0.0
	numElems = len(storedElems)
	for elem in storedElems:
		averageError += elem[4]*elem[4]
		averageDiff += elem[3]*elem[3]
	averageError /= numElems
	averageDiff /= numElems
	averageError = math.sqrt(averageError)
	averageDiff = math.sqrt(averageDiff)
	return (averageError, averageDiff)

trainError = getAverageError(trainToStore)
testError = getAverageError(toStore)

print "Average Train Error: %f AverageDiff: %f" % (trainError[0], trainError[1])
print "Average Test Error: %f Average Diff: %f" % (testError[0], testError[1])

outfile = open(outputFileName, 'wb')
writer = csv.writer(outfile)
writer.writerow(['Player Name', 'Predicted Points', 'Actual Points', "Difference", "Pct Error"])
writer.writerows(toStore)

headers = ['+/-', '3PA', '3PM', 'AST', 'BLK', 'DKPoints', 'DREB', 'FGA', 'FGM', 'FTA', 'FTM', 'MIN', 'OREB', 
'PF', 'PTS', 'REB', 'STL', 'TO', 'home_team_score', 'visit_team_score', 'Home', 'team_win_pct', 'opponent_win_pct', 'const', 
'HomeCurr', 'team_win_pctCurr', 'opponent_win_pctCurr']

# for i in xrange(0, len(discretizedStates)):
# 	thetaCurr = theta[i]
# 	for j in xrange(0, len(headers)):
# 		print "%s: %f" % (headers[j], thetaCurr[j])

newOutfile = open(thetaFileName, 'wb')
writer = csv.writer(newOutfile)
writer.writerow(headers)
for i in xrange(0, len(discretizedStates)):
	writer.writerow(theta[i])






