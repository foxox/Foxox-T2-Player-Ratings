# This script is an exploration into processing PUB/PUG match results into player rankings.
# Once I hack together something that seems useful, I may try to tidy this up.


import yaml
from operator import itemgetter
from more_itertools import pairwise, distinct_combinations

print()

# load file
with open('pubresults.yaml', 'r') as file:
  file_contents = yaml.full_load(file)

class PlayerResult:
  def __init__(self, yaml_player_result):
    self.name = yaml_player_result[0]
    self.score = yaml_player_result[1]
  
  def __str__(self):
    return "PlayerResult(name={}, score={})".format(self.name, self.score)

class TeamResult:
  def __init__(self, yaml_team_result):
    self.score = yaml_team_result['score']
    self.players = [PlayerResult(player) for player in yaml_team_result['players']]
  
  def __str__(self):
    return "TeamResult(score={}, players={})".format(self.score, self.players)

class MatchResult:
  def __init__(self, yaml_match_result):
    self.date = yaml_match_result['date']
    self.mission = yaml_match_result['mission']
    
    results = yaml_match_result['results']
    self.team_results = dict()
    for (team, team_result) in results.items():
      self.team_results[team] = TeamResult(team_result)
  
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
print("any_roles_to_players['defense']:",any_roles_to_players['defense'])
print("any_roles_to_players['offense']:",any_roles_to_players['offense'])
for (role, related_roles) in role_relationships.items():
  if role not in any_roles_to_players:
    any_roles_to_players[role] = list()
  for related_role in related_roles:
    any_roles_to_players[role].append(any_roles_to_players[related_role])
print("expanded any_roles_to_players['defense']:",any_roles_to_players['defense'])
print("any_roles_to_players['offense']:",any_roles_to_players['offense'])

player_to_win_count = dict()
player_to_match_count = dict()
duo_to_win_count = dict()
duo_to_match_count = dict()
trio_to_win_count = dict()
trio_to_match_count = dict()


# loop over all matches
for match in file_contents:

  match_result = MatchResult(match)
  print(match_result)

  winning_team_score = 0
  winning_team_name = None
  results = match['results']
  # match
  for team in results:
    # print('team:', team)
    if results[team]['score'] > winning_team_score:
      winning_team_score = results[team]['score']
      winning_team_name = team


  # WIN RATE STATS GATHERING. SINGLES, DUOS, TRIOS, ETC.
  for team in results:
    
    # SINGLES
    for player in results[team]['players']:
      player_split = player.split(", ")
      playername = player_split[0]
      # player_tuple = (player_split[0], int(player_split[1]))
      # 0 is name, 1 is score

      if not playername in player_to_match_count:
        player_to_match_count[playername] = 0
      if not playername in player_to_win_count:
        player_to_win_count[playername] = 0
      player_to_match_count[playername]+=1
      if team == winning_team_name:
        player_to_win_count[playername]+=1
    
    # DUOS
    for duo in distinct_combinations(results[team]['players'], 2):
      duo0split = duo[0].split(", ")
      duo1split = duo[1].split(", ")
      player_name_duo=(duo0split[0],duo1split[0])
      # print('Duo ',player_name_duo,' appeared in match ',match)
      if not player_name_duo in duo_to_win_count:
        duo_to_win_count[player_name_duo] = 0
      if not player_name_duo in duo_to_match_count:
        duo_to_match_count[player_name_duo] = 0
      duo_to_match_count[player_name_duo]+=1
      if team == winning_team_name:
        duo_to_win_count[player_name_duo]+=1


  # Count a team win as an individual win for each winning team player against all losing team players (and vice versa for losses)
  # todo: maybe it should only count as a personal win if your personal score is higher than the other team's player
  assert(len(results) == 2)
  winning_team_name = 0
  losing_team_name = 0
  lose = 0
  win = 1
  team_names = list(results.keys())
  if results[team_names[0]]['score'] > results[team_names[1]]['score']:
    winning_team_name = team_names[0]
    losing_team_name = team_names[1]
  elif results[team_names[0]]['score'] < results[team_names[1]]['score']:
    winning_team_name = team_names[1]
    losing_team_name = team_names[0]
  else:
    lose = 0.5
    win = 0.5

   

# Print conditional probabilities
player_to_win_rate = dict()
match_count_high_threshold = 40
match_count_low_threshold = 27
for matchkvp in player_to_match_count.items():
  if matchkvp[1] < match_count_high_threshold:
    continue
  player_to_win_rate[matchkvp[0]] = player_to_win_count[matchkvp[0]] / matchkvp[1]
player_to_win_rate_sorted = list(player_to_win_rate.items())
player_to_win_rate_sorted.sort(key=lambda p: p[1], reverse=True)
print('Higher confidence Best (and worst) player win rates:\n','\n'.join([str(x) for x in player_to_win_rate_sorted]))

player_to_win_rate = dict()
for matchkvp in player_to_match_count.items():
  if matchkvp[1] > match_count_high_threshold or matchkvp[1] < match_count_low_threshold:
    continue
  player_to_win_rate[matchkvp[0]] = player_to_win_count[matchkvp[0]] / matchkvp[1]
player_to_win_rate_sorted = list(player_to_win_rate.items())
player_to_win_rate_sorted.sort(key=lambda p: p[1], reverse=True)
print('Lower confidence Best (and worst) player win rates:\n','\n'.join([str(x) for x in player_to_win_rate_sorted]))

print('')

# As above but per role
for role, players in first_roles_to_players.items():
  # print([str((p,player_to_match_count[p])) for p in players if p in player_to_match_count])
  player_match_counts = [player_to_match_count[p] for p in players if p in player_to_match_count]
  player_match_counts.sort()

  top_third_match_count = player_match_counts[len(player_match_counts)*2//3]
  middle_third_match_count = player_match_counts[len(player_match_counts)//3]
  # print('Role:',role,'player match counts:',player_match_counts,'top third cutoff:',top_third_match_count,'middle third cutoff:',middle_third_match_count)

  significant_players = [(p, player_to_win_count[p] / player_to_match_count[p]) for p in players if p in player_to_match_count and player_to_match_count[p] >= top_third_match_count]
  significant_players.sort(key=lambda p: p[1], reverse=True)
  print('Higher confidence',role,[p[0]+' '+format(p[1],'.2f') for p in significant_players])
  
  significant_players = [(p, player_to_win_count[p] / player_to_match_count[p]) for p in players if p in player_to_match_count and player_to_match_count[p] >= middle_third_match_count and player_to_match_count[p] < top_third_match_count]
  significant_players.sort(key=lambda p: p[1], reverse=True)
  print('Middle confidence',role,[p[0]+' '+format(p[1],'.2f') for p in significant_players])

  significant_players = [(p, player_to_win_count[p] / player_to_match_count[p]) for p in players if p in player_to_match_count and player_to_match_count[p] < middle_third_match_count and player_to_match_count[p] > 1]
  significant_players.sort(key=lambda p: p[1], reverse=True)
  print('Lower  confidence',role,[p[0]+' '+format(p[1],'.2f') for p in significant_players])

  print()

print()

duo_to_win_rate = dict()
duo_count_threshold = 22
for matchkvp in duo_to_match_count.items():
  if matchkvp[1] < duo_count_threshold:
    continue
  duo_to_win_rate[matchkvp[0]] = duo_to_win_count[matchkvp[0]] / matchkvp[1]
duo_to_win_rate_sorted = list(duo_to_win_rate.items())
duo_to_win_rate_sorted.sort(key=lambda p: p[1], reverse=True)
print('Duo win rates (n >= ',duo_count_threshold,'):\n','\n'.join([str(x) for x in duo_to_win_rate_sorted]))

print()

