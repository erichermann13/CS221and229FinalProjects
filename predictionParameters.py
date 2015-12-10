import math

predictionYear = 2016
trainYear = 2015
dateForPrediction = "12.9.2015"

# For naiveBayes, if used
numQuantiles = 5

# For regression and then making predictions
numPreviousGamesToConsider = 5
discretizedStates = [10, 20, 30]
dataToIgnore = ['player', 'team', 'date', 'home_team', 'visit_team', 'Unnamed: 0', 
'away_team_losses', 'away_team_wins', 'home_team_losses', 'home_team_wins', 'home_win_pct', 'away_win_pct', 'position']