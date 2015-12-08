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

minPoints = 20



dataToIgnore = ['Unnamed: 0', 'Unnamed: 0.1', '+/-', '3PA', '3PM', 'AST', 'BLK', 'DREB', 'FGA', 'FGM', 
'FTA', 'FTM', 'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TO', 'game_id',  'date', 'home_team', 
'home_team_losses', 'home_team_score', 'home_team_wins', 'visit_team', 'visit_team_score', 'Home', 'Name', 'GameInfo']

playersFile = './players_clean' + str(year) + '.csv'

playersData =  pd.read_csv(playersFile)
playersData['date'] = pd.to_datetime(playersData.date)

errors = []

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

		newFrame['Difference'] = newFrame['AvgPointsPerGame'] - newFrame['DKPointsOriginal']

		newFrame['Error'] = newFrame['Difference']/newFrame['DKPointsOriginal']
		newFrame['Error'] = newFrame['Error'].abs()

		newFrame = newFrame[newFrame['DKPointsOriginal'] > minPoints]

		averageError = newFrame['Error'].mean()
		if not math.isnan(averageError):
			print "Average Error on %s:  %f" % (str(testDate), averageError)
			errors.append(averageError)

print "Overall Average Error %f" % np.mean(errors)







