README

To make a prediction of scores for players on a particular day, first download the DraftKings NBA player salary data for that day into “./SalariesData/(MO.DAY.YEAR)”.  Then, change the date in the predictionParameters.py file to the date you want to predict for and run runPredictor.py. This will output score predictions into “./PredictionsData/(current date)”.

Explanation of Files:
(in some order of importance)

regressionSolver.py - This file does the learning to find theta values for our linear regression problem, and computes the error for the training and test sets. It stores the theta values in modelParameters.csv

csp_make_teams.py - This file takes data from the PredictionsData folder (where the predictions from the linear regression problem are stored every day) and outputs the optimal team based on the constraints and the data

naiveBayes.py - This file runs a modified version of multinomial naive Bayes to predict player scores, also computing error and also storing values in modelParameters.csv

makePredictions.py - Takes the DraftKings data on who’s playing that day and computes the predicted number of DraftKings points each player will score based on the regression parameter values

runPredictor.py - This file provides a simple way to run the scripts necessary to predict player scores on a particular day

predictionParameters.py - This file contains constants used by several scripts so they don’t need to be changed in each one individually each time

getTeams.py, getGames.py, getPlayers.py - Scrape the NBA team, player, and game data from ESPN.com. Data is added to teams.csv, games(year).csv, and players(year).csv

cleanData.py - Takes data from players(year).csv and centers each column with zero mean and unit standard deviation. Also adds a couple of useful columns

compareToDKData.py - Analyzes DraftKings’ predictions accuracy by comparing predicted DK scores to actual DraftKings points players scored on a given night

evaluate_csp.py - Uses our CSP to create teams with Draftkings' predictions and compares the scores of our teams to the scores of the teams created by FantasySports

util.py, regressionUtil.py - Contain functions useful to the regression and CSP problems

backtracking.py - Contains the backtracking search algorithm. We eventually implemented beam search.

baseline.py - Our original baseline algorithm

SalariesData - A folder containing all of the downloaded DraftKings salary data each day we’ve managed to download it

PredictionsData - A folder containing files with our outputted score predictions for each player playing for each particular night

avg_std_dev_cols(year).csv - Contains the average and standard deviation of the different categories of player data

games(year).csv, teams.csv, players(year).csv, players_clean(year).csv - Contain scraped data from ESPN.com on NBA players, games, and teams for a given year. The _clean files are after running through cleanData.py

modelParameters.csv - Contains the theta values for linear regression. Each row is a discretized subspace of the overall space (the first row is theta values for players scoring on average between 10 and 20 points)

players_riskiness(year).csv - Contain a measure of the “riskiness” of a player, calculated by taking the ratio of a players’ points standard deviation over their points mean, and dividing that ratio by the average ratio of points standard deviation over mean for all players

predictorData(year).csv - Contains outputted data on what the predicted DraftKings scores were for each player, and the error, for both the training and test set. This csv is populated by regressionSolver.py

 




