import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd

year = 2015
teamsFile = './teams.csv'
BASE_URL = 'http://espn.go.com/nba/team/schedule/_/name/{0}/year/{1}/seasontype/2/{2}'
BASE_GAME_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'

csvfile = open(teamsFile, 'rb')
reader = csv.reader(csvfile)
teamsList = list(reader)

game_id = []
dates = []
home_team = []
home_team_score = []
visit_team = []
visit_team_score = []
for i in xrange(1, len(teamsList)):
  currRow = teamsList[i]
  _team = currRow[0]
  websiteText = requests.get(BASE_URL.format(currRow[1], year, currRow[2]))
  table = BeautifulSoup(websiteText.text).table
  # print table.prettify()
  for row in table.find_all('tr')[1:]:
    # print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    columns = row.find_all('td')
    try:
      _id = columns[2].a['href'].split('?id=')[1]
      # print _id
      _home = True if columns[1].li.text == 'vs' else False
      # print _home
      _other_team = columns[1].find_all('a')[1]['href']
      _other_team = _other_team.split('/')[-1:][0]
      for j in xrange(1, len(teamsList)):
        aRow = teamsList[j]
        if aRow[2] == _other_team:
          _other_team = aRow[0]
          break
      # _other_team = teamsList[0][teamsList[2] == _other_team]
      # print _other_team
      # _other_team = _other_team.values[0]
      
      _score = columns[2].a.text.split(' ')[0].split('-')
      # print _score
      _won = True if columns[2].span.text == 'W' else False
      # print _won
      game_id.append(_id)
      home_team.append(_team if _home else _other_team)
      visit_team.append(_team if not _home else _other_team)

      d = datetime.strptime(columns[0].text, '%a, %b %d')
      dates.append(date(year, d.month, d.day))
      # print dates[-1]

      if _home:
        if _won:
          home_team_score.append(_score[0])
          visit_team_score.append(_score[1])
        else:
          home_team_score.append(_score[1])
          visit_team_score.append(_score[0])
      else:
        if _won:
          home_team_score.append(_score[1])
          visit_team_score.append(_score[0])
        else:
          home_team_score.append(_score[0])
          visit_team_score.append(_score[1])


      # Note that some items in columns will not actually be games
    except:
      pass

 
dic = {'id': game_id, 'date': dates, 'home_team': home_team, 'visit_team': visit_team, 
        'home_team_score': home_team_score, 'visit_team_score': visit_team_score}
        
games = pd.DataFrame(dic).drop_duplicates(cols='id').set_index('id')
print(games)
games.to_csv('./games.csv')
