import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import math
import os

year = 2016
pathToSalariesData = "/Users/Eric/CS221and229FinalProjects/SalariesData"

minPoints = 40



dataToIgnore = ['Unnamed: 0', 'Unnamed: 0.1', '+/-', '3PA', '3PM', 'AST', 'BLK', 'DREB', 'FGA', 'FGM', 
'FTA', 'FTM', 'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TO', 'game_id',  'date', 'home_team', 
'home_team_losses', 'home_team_score', 'home_team_wins', 'visit_team', 'visit_team_score', 'Home', 'Name', 'GameInfo']

playersFile = './players_clean' + str(year) + '.csv'

playersData =  pd.read_csv(playersFile)
playersData['date'] = pd.to_datetime(playersData.date)

errors = []
diffs = []

for DKFile in os.listdir(pathToSalariesData):

	if DKFile[0] != '.':	
		dateList = DKFile.split('s')[1]
		testDate = datetime.strptime(dateList, '%m.%d.%Y.c')

		DKData = pd.read_csv("./SalariesData/" + DKFile)

		dataFromDate = playersData.loc[playersData['date'] == testDate]

		newFrame = pd.merge(dataFromDate, DKData, left_on = 'player', right_on  = 'Name')

		newFrame = newFrame.drop(dataToIgnore, axis=1)

		newFrame = newFrame[newFrame.DKPointsOriginal != 0]
		newFrame = newFrame[np.isfinite(newFrame['DKPointsOriginal'])]

		newFrame = newFrame[newFrame['DKPointsOriginal'] > minPoints]

		newFrame['Difference'] = newFrame['AvgPointsPerGame'] - newFrame['DKPointsOriginal']
		diffSeries = newFrame['Difference'].abs()

		newFrame['Error'] = newFrame['Difference']/newFrame['DKPointsOriginal']
		errorSeries = newFrame['Error'].abs()



		if not math.isnan(errorSeries.mean()):
			numElems = errorSeries.size
			averageError = 0.0
			averageDiff = 0.0
			for i in xrange(0, numElems):
				averageError += errorSeries.iloc[i]**2
				averageDiff += diffSeries.iloc[i]**2
			averageError = math.sqrt(averageError/numElems)
			averageDiff = math.sqrt(averageDiff/numElems)
			print "%s: Average Error %f Average Diff: %f" % (str(testDate), averageError, averageDiff)
			# print "Avg Error/Avg Diff: %f" % (averageError/averageDiff)
			errors.append(averageError)
			diffs.append(averageDiff)

overallError = 0.0
overallDiff = 0.0
for i in xrange(0, len(errors)):
	overallError += errors[i]**2
	overallDiff += diffs[i]**2
overallError = math.sqrt(overallError/len(errors))
overallDiff = math.sqrt(overallDiff/len(diffs))

print "Overall: Average Error %f Average Diff %f" % (overallError, overallDiff)







