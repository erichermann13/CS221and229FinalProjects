import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import math

year = 2016
testDate = datetime.strptime('31Oct2015', '%d%b%Y')

dataToIgnore = ['Unnamed: 0', 'Unnamed: 0.1', '+/-', '3PA', '3PM', 'AST', 'BLK', 'DREB', 'FGA', 'FGM', 
'FTA', 'FTM', 'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TO', 'game_id',  'date', 'home_team', 
'home_team_losses', 'home_team_score', 'home_team_wins', 'visit_team', 'visit_team_score', 'Home', 'Name', 'GameInfo']

playersFile = './players_clean' + str(year) + '.csv'
DKFile = './SalariesData/DKSalaries' + str(testDate.month) + '.' + str(testDate.day) + '.' + str(testDate.year) + '.csv'

playersData =  pd.read_csv(playersFile)
DKData = pd.read_csv(DKFile)

playersData['date'] = pd.to_datetime(playersData.date)

dataFromDate = playersData.loc[playersData['date'] == testDate]

newFrame = pd.merge(dataFromDate, DKData, left_on = 'player', right_on  = 'Name')

newFrame = newFrame.drop(dataToIgnore, axis=1)

# newFrame = newFrame[newFrame.AvgPointsPerGame != 0]
newFrame = newFrame[newFrame.DKPoints != 0]
newFrame = newFrame[np.isfinite(newFrame['DKPoints'])]

newFrame['Difference'] = newFrame['AvgPointsPerGame'] - newFrame['DKPoints']

newFrame['Error'] = newFrame['Difference']/newFrame['DKPoints']

print newFrame

averageError = newFrame['Error'].mean()
print averageError







