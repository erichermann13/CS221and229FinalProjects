import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import math
import regressionUtil
import predictionParameters

year = predictionParameters.trainYear
dateToPredict = predictionParameters.dateForPrediction
DKFileName = "./SalariesData/DKSalaries" + dateToPredict + ".csv"
playersFileName = "./players_clean" + str(year) + ".csv"
thetaFileName = "./modelParameters.csv"
dataDeviationsFileName = "./avg_std_dev_cols2015.csv"
outputFileName = "./PredictionsData/" + dateToPredict + ".csv"

currGameData = ['Home', 'team_win_pct', 'opponent_win_pct']

minGames = 0
numPreviousGamesToConsider = predictionParameters.numPreviousGamesToConsider
discretizedStates = predictionParameters.discretizedStates

DKData = pd.read_csv(DKFileName)
players = pd.read_csv(playersFileName)
theta = pd.read_csv(thetaFileName)
# theta = theta.ix[0]
dataDeviations = pd.read_csv(dataDeviationsFileName)
pointsAverage = dataDeviations['DKPoints'][0]
pointsStdDev = dataDeviations['DKPoints'][1]

playerNames = DKData['Name']

def runTrainOrTest(playerData, DKPlayerData):
	numElems = len(playerData)
	# Note that a player's information is not super useful if they played only in a few games
	if numElems > minGames:
		trainData = playerData.iloc[numElems-numPreviousGamesToConsider:numElems]
		DKPointsForTest = playerData['DKPointsOriginal'].mean()
		trainData = trainData.drop('DKPointsOriginal', axis=1)

		bucket = -1
		while DKPointsForTest > discretizedStates[bucket + 1]:
			bucket += 1
			if bucket == len(discretizedStates)-1: break

		if bucket != -1:
			thetaToReview = theta.ix[bucket]

			playerAverages = trainData.mean()

			home = True
			teams = DKPlayerData.iloc[0]['GameInfo']
			teams = teams.split(' ')[0].split('@')
			playerTeam = DKPlayerData.iloc[0]['teamAbbrev']
			otherTeam = teams[0]
			if teams[0] == playerTeam:
				home = False
				otherTeam = teams[1]

			for newRow in currGameData:
				value = -1
				if newRow == 'Home':
					if home: value = 1
				if newRow == 'team_win_pct':
					value = regressionUtil.getTeamRecord(playerTeam)
				if newRow == 'opponent_win_pct':
					value = regressionUtil.getTeamRecord(otherTeam)
				playerAverages[newRow + 'Curr'] = value

			hFunction = np.dot(playerAverages, thetaToReview)
			return hFunction*pointsStdDev + pointsAverage

	return 0


predictedScores = []

for aPlayer in playerNames:
	playerData = regressionUtil.cleanPlayerData(aPlayer, players)
	DKPlayerData = DKData.loc[DKData['Name'] == aPlayer]
	predictedScore = runTrainOrTest(playerData, DKPlayerData)
	DKPrediction = DKPlayerData.iloc[0]['AvgPointsPerGame']
	playerPosition = DKPlayerData.iloc[0]['Position']
	playerSalary = DKPlayerData.iloc[0]['Salary']
	print "Player: %s Score: %f DraftKings Prediction: %f" % (aPlayer, predictedScore, DKPrediction)
	predictedScores.append([aPlayer, predictedScore, DKPrediction, playerPosition, playerSalary])

outfile = open(outputFileName, 'wb')
writer = csv.writer(outfile)
writer.writerow(['Player', 'Our Prediction', 'DraftKings Prediction', 'Position', 'Salary'])
writer.writerows(predictedScores)














