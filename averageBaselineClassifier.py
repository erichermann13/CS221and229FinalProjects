import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import math

year = 2016

playersFile = './players_clean' + str(year) + '.csv'
outputFileName = './predictorData' + str(year) + '.csv'

data = pd.read_csv(playersFile)

playerNames = data['player']
uniquePlayers = pd.unique(playerNames)

numPlayers = len(uniquePlayers)
trainFraction = 3.0/4
minGames = 20
minPoints = 5

trainPlayers = uniquePlayers[0:(numPlayers*trainFraction)]
testPlayers = uniquePlayers[(numPlayers*trainFraction):]

dataToIgnore = ['player', 'team', 'date', 'home_team', 'visit_team', 'Unnamed: 0.1', 'game_id', '+/-', 'Unnamed: 0', 
'away_team_losses', 'away_team_wins', 'home_team_losses', 'home_team_score', 'home_team_wins', 'visit_team_score']

theta = [0]*(len(data.iloc[0]) - len(dataToIgnore))
alpha = 0.0005


for j in xrange(0, 50):
	for aPlayer in trainPlayers:
		playerData = data.loc[data['player'] == aPlayer]
		playerData = playerData.drop(dataToIgnore, axis=1)
		# Gets rid of rows where the player didn't play
		playerData = playerData[np.isfinite(playerData['MIN'])]
		numElems = len(playerData)
		# Note that a player's information is not super useful if they played only in a few games
		if numElems > minGames:
			trainSize = int(3*numElems/4.0)
			toTrain = playerData.head(trainSize)
			yGenerator = playerData.tail(numElems - trainSize)
			DKPoints = yGenerator['DKPoints'].mean()

			if DKPoints > minPoints:

				playerAverages = toTrain.mean()
				hFunction = np.dot(playerAverages, theta)
				for i in xrange(0, len(theta)):
					theta[i] = theta[i] + alpha*(DKPoints - hFunction)*playerAverages[i]
				# print theta
				# print playerData.columns.values
	print j
	print theta

# See how well you did

toStore = []

for aPlayer in testPlayers:
	playerData = data.loc[data['player'] == aPlayer]
	playerData = playerData.drop(dataToIgnore, axis=1)
	# Gets rid of rows where the player didn't play
	playerData = playerData[np.isfinite(playerData['MIN'])]
	numElems = len(playerData)
	# Note that a player's information is not super useful if they played only in a few games
	if numElems > minGames:
		trainSize = int(3*numElems/4.0)
		toTrain = playerData.head(trainSize)
		yGenerator = playerData.tail(numElems - trainSize)
		DKPoints = yGenerator['DKPoints'].mean()

		if DKPoints > minPoints:
			playerAverages = toTrain.mean()
			hFunction = np.dot(playerAverages, theta)
			diff = DKPoints - hFunction
			pctError = abs(diff)/DKPoints
			print "%s Predicted Points: %f  Actual Points %f Diff %f Error %f" % (aPlayer, hFunction, DKPoints, diff, pctError)
			toStore.append([aPlayer, hFunction, DKPoints, diff, pctError])

averageError = 0.0
numElems = len(toStore)
for elem in toStore:
	averageError += elem[4]
averageError /= numElems
print "Average Error: %f" % averageError

outfile = open(outputFileName, 'wb')
writer = csv.writer(outfile)
writer.writerow(['Player Name', 'Predicted Points', 'Actual Points', "Difference", "Pct Error"])
writer.writerows(toStore)





