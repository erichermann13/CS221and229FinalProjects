import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import math
import predictionParameters

theYear = 2016
thePlayersFileName = "./players_clean" + str(theYear) + ".csv"
teamsFileName = "./teams.csv"
theDataDeviationsFileName = "./avg_std_dev_cols2015.csv"
dataToIgnore = predictionParameters.dataToIgnore


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
	if teamAbbrev =='uta': teamAbbrev = 'utah'

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

