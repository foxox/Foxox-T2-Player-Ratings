# This script is an exploration into processing PUB/PUG match results into player rankings.
# Once I hack together something that seems useful, I may try to tidy this up.


from datetime import datetime
import yaml
from operator import itemgetter
from more_itertools import pairwise, distinct_combinations


def str_to_date(date_str):
  return datetime.strptime(date_str, "%Y-%m-%d").date()


print()

# load file
with open('pubresults.yaml', 'r') as file:
  file_contents = yaml.full_load(file)

class PlayerResult:
  def __init__(self, yaml_player_result):
    player_split = yaml_player_result.split(", ")
    self.name = player_split[0]
    self.score = player_split[1]
    # print('PlayerResult name:', self.name, 'score:', self.score)
  
  def __str__(self):
    return "PlayerResult(name={}, score={})".format(self.name, self.score)

class TeamResult:
  def __init__(self, yaml_team_result, is_winner):
    self.score = yaml_team_result['score']
    self.player_results = [PlayerResult(player) for player in yaml_team_result['players']]
    self.is_winner = is_winner
  
  def __str__(self):
    return "TeamResult(score={}, players={}, is_winner={})".format(self.score, self.players, self.is_winner)

class MatchResult:
  def __init__(self, yaml_match):
    self.date = str_to_date(str(yaml_match['date'])) # Just in case the date is still a string, parse it into a date object.
    self.mission = yaml_match['mission']
    
    yaml_match_results = yaml_match['results']
    self.team_results = list()

    # Find the winning team.
    team_name_list = list(yaml_match_results.keys())
    assert(len(team_name_list) == 2) # There must be exactly two teams in a match result
    winning_team_name = team_name_list[0] if yaml_match_results[team_name_list[0]]['score'] > yaml_match_results[team_name_list[1]]['score'] else team_name_list[1]

    # Finish populating the team_results
    self.team_results = [TeamResult(yaml_team_result, team_name == winning_team_name) for (team_name, yaml_team_result) in yaml_match_results.items()]

  
  def __str__(self):
    return "MatchResult(date={}, mission={}, team_results={})".format(self.date, self.mission, self.team_results)


# Guesses at player primary roles based on information provided by the community and my observations
players_to_roles = {
  'stormcrow':['ld','lof'],
  'jacob':['ld','lo','cap'],
  'bizzy':['ld','lo'],
  'slush':['cap'],
  'astralis':['cap','flex'],
  'domestic':['ld','chase'],
  'danno':['ho','ho'],
  'hybrid':['lof','ho'],
  'vaxity':['ho','shrike'],
  'mistcane':['ld','cap'],
  'nevares':['cap'],
  'haggis':['ho'],
  'devil':['cap','ho'],
  'efx':['ld','lof'],
  'hexy':['ld','shrike'],
  'halo2':['ho'],
  'blake':['lof'],
  'future':['flex'],
  'thaen':['offense'],
  'strazz':['hof'],
  'history':['cap','shrike','ho'],
  'sliderzero':['shrike','flex'],
  'jerry':['ld'],
  'wingedwarrior':['ld','snipe'],
  'sylock':['ho'],
  'darrell':['ld'],
  'pedro':['ld'],
  'coorslightman':['ld'],
  'hautsoss':['flex'],
  'sajent':['ld','ho'],
  'turtle':['ld'],
  'irvin':['cap'],
  'redeye':['lo','ho','flex'],
  'mlgru':['shrike','ho','cap'],
  'actionswanson':['flex'],
  'bendover':['ho'],
  'warchilde':['ho'],
  'johnwayne':['flex'],
  'lsecannon':['farm'],
  'hp':['ld','lof'],
  'sake':['ld'],
  'anthem':['ho'],
  'taco':['ho'],
  'exogen':['cap'],
  'mp40':['hd'],
  'gunther':['ho'],
  'ipkiss':['snipe'],
  'alterego':['hd'],
  'homer':['ho'],
  'spartanonyx':['ld'],
  'bish':['ho'],
  'flyersfan':['ld'],
  'geekofwires':['ho'],
  'aromatomato':['ho'],
  'heat':['ho','hd','farm'],
  'daddyroids':['ld'],
  'pupecki':['ld'],
  'yuanz':['farm','hd','ho'],
  'm80':['lof'],
  'andycap':['hof'],
  'tetchy':['cap','shrike'],
  'systeme':['hd','farm','ho'],
  'friendo':['hof','farm','ld','ho'],
  'coastal':['shrike','ld'],
  'caution':['ho','cap'],
  'jx':['ld'],
  'nightwear':['flex'],
  'piata':['ho'],
  'foxox':['snipe','farm'],
  'elliebackwards':['ld'],
  'nutty':['ld'],
  'sweetcheeks':['farm'],
  'carpenter':['hd','ld'],
  'eeor':['ld'],
  'cooter':['cap'],
  'flakpyro':['flex','d'],
  'doug':['ld','ho','snipe'],
  'raynian':['ho','mo'],
  'legelos':['ld'],
  '7thbishop':['cap','hd'],
  'dirkdiggler':['ho'],
  'lazer':['ld'],
  'iroc':['ld'],
  'ember':['ld'],
  '2short':['hd','ho','cap'],
  'earth':['tank','hd','hof'],
  'lolcaps':['cap'],
  'aftermath':['ld'],
  'fnatic':['ld'],
  'cooljuke':['snipe'],
  'sterio':['ld'],
  'jazz':['ho','ld','cap'],
}

first_roles_to_players = dict()
any_roles_to_players = dict()
for player,roles in players_to_roles.items():
  if roles[0] is None:
    # print('')
    continue
  # first_role_players = first_roles_to_players[roles[0]]
  if not roles[0] in first_roles_to_players:
    first_roles_to_players[roles[0]] = list()
  # print('adding', player,'to role',roles[0])
  first_roles_to_players[roles[0]].append(player)

  for role in roles:
    if not role in any_roles_to_players:
      any_roles_to_players[role] = list()
    any_roles_to_players[role].append(player)

# Some roles imply other roles or role categories, such as HO implying O.
# D doesn't include farm and O doesn't include cap
role_relationships = {'defense':['tank','hd','lof','hof','ld','flex','shrike','snipe'],'offense':['shrike','ho','snipe','flex','lo','snipe']}
any_roles_to_players['defense'] = list()
# print("any_roles_to_players['defense']:",any_roles_to_players['defense'])
# print("any_roles_to_players['offense']:",any_roles_to_players['offense'])
for (role, related_roles) in role_relationships.items():
  if role not in any_roles_to_players:
    any_roles_to_players[role] = list()
  for related_role in related_roles:
    any_roles_to_players[role].append(any_roles_to_players[related_role])
# print("expanded any_roles_to_players['defense']:",any_roles_to_players['defense'])
# print("any_roles_to_players['offense']:",any_roles_to_players['offense'])
  

def compute_stats_for_time_period(start_date, end_date):

  player_to_win_count = dict()
  player_to_match_count = dict()
  duo_to_win_count = dict()
  duo_to_match_count = dict()

  match_results = [MatchResult(match) for match in file_contents]

  # loop over all matches
  for match_result in match_results:
    if match_result.date < start_date or match_result.date > end_date:
      continue

    # WIN RATE STATS GATHERING. SINGLES, DUOS, TRIOS, ETC.
    for team_result in match_result.team_results:
      
      # SINGLES
      for player_result in team_result.player_results:
        if not player_result.name in player_to_match_count:
          player_to_match_count[player_result.name] = 0
        if not player_result.name in player_to_win_count:
          player_to_win_count[player_result.name] = 0
        player_to_match_count[player_result.name]+=1
        if team_result.is_winner:
          player_to_win_count[player_result.name]+=1
      
      # DUOS
      for duo in distinct_combinations(team_result.player_results, 2):
        player_name_duo = tuple([duo[0].name, duo[1].name])
        # print('Duo ',player_name_duo,' appeared in match ',match_result.mission,' on date ',match_result.date)
        if not player_name_duo in duo_to_win_count:
          duo_to_win_count[player_name_duo] = 0
        if not player_name_duo in duo_to_match_count:
          duo_to_match_count[player_name_duo] = 0
        duo_to_match_count[player_name_duo]+=1
        if team_result.is_winner:
          duo_to_win_count[player_name_duo]+=1
  
  return (player_to_win_count, player_to_match_count, duo_to_win_count, duo_to_match_count)



# Print stat results

(all_time_player_to_win_count, all_time_player_to_match_count, all_time_duo_to_win_count, all_time_duo_to_match_count) = compute_stats_for_time_period(str_to_date('2000-01-01'), str_to_date('2100-01-01'))
all_time_player_names = list(all_time_player_to_match_count.keys())

# Print player win rates CSV style by quarter
# CSV format:
# Player,Q1 2025,Q2 2025,Q3 2025,Q4 2025,Q1 2026
# Foxox,#N/A,0.3,0.4,0.5,0.45
# Pupecki,#N/A,0.2,0.3,#N/A,0.55
quarters = [('Q1 2025','2025-01-01','2025-03-31'),('Q2 2025','2025-04-01','2025-06-30'),('Q3 2025','2025-07-01','2025-09-30'),('Q4 2025','2025-10-01','2025-12-31'),('Q1 2026','2026-01-01','2026-03-31')]
csv_header = 'Player'
csv_per_player = dict()
for quarter in quarters:
  quarter_name = quarter[0]
  quarter_start_date = str_to_date(quarter[1])
  quarter_end_date = str_to_date(quarter[2])
  csv_header+=','+quarter_name
  (player_to_win_count, player_to_match_count, duo_to_win_count, duo_to_match_count) = compute_stats_for_time_period(quarter_start_date, quarter_end_date)
  for player in all_time_player_names:
    # If there is csv row for the player yet, initialize it.
    if not player in csv_per_player:
      csv_per_player[player] = []
    # If the player played at least one match in the quarter, add their win rate to the csv. Otherwise, add #N/A.
    if player in player_to_match_count and player_to_match_count[player] > 0:
      csv_per_player[player].append(player_to_win_count[player] / player_to_match_count[player])
    else:
      csv_per_player[player].append('#N/A')
print(csv_header)
for player in all_time_player_names:
  print(player+','+','.join([str(x) for x in csv_per_player[player]]))

num_top_players_to_show = 5 # The number of top players to show in each category.

player_match_counts = list(all_time_player_to_match_count.values())
player_match_counts.sort(reverse=True)
top_single_tenth_match_count = player_match_counts[num_top_players_to_show]
top_players = [(p, all_time_player_to_win_count[p] / all_time_player_to_match_count[p]) for p in all_time_player_to_match_count.keys() if p in all_time_player_to_match_count and all_time_player_to_match_count[p] >= top_single_tenth_match_count]
top_players.sort(key=lambda p: p[1], reverse=True)
print('Highest confidence singles',[p[0]+' '+format(p[1],'.2f') for p in top_players[:num_top_players_to_show]])

duo_match_counts = list(all_time_duo_to_match_count.values())
duo_match_counts.sort(reverse=True)
top_duo_match_count = duo_match_counts[num_top_players_to_show]
top_duos = [(p, all_time_duo_to_win_count[p] / all_time_duo_to_match_count[p]) for p in all_time_duo_to_match_count.keys() if p in all_time_duo_to_match_count and all_time_duo_to_match_count[p] >= top_duo_match_count]
top_duos.sort(key=lambda p: p[1], reverse=True)
print('Highest confidence duos',[str(p[0])+' '+format(p[1],'.2f') for p in top_duos[:num_top_players_to_show]])


print()

