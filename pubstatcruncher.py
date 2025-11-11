# This script is an exploration into processing PUB/PUG match results into player rankings.
# Once I hack together something that seems useful, I may try to tidy this up.

# So far, "single team point whore" glicko ratings are the most useful result. This compares players only to their teammates, so when one team dominates another, the ratings are still fair. However, this still suffers from the problem that certain roles tend to score more than others: for example, a top capper is probably going to have a greater score than a top farmer, even though the farmer is critical to the team's success.

# The next thing I would like to compute is a historical conditional probability of winning a match given that a certain pair or trio of players is on the team.


import yaml
from operator import itemgetter
import glicko2
from more_itertools import pairwise, distinct_combinations

# load file
with open('pubresults.yaml', 'r') as file:
  file_contents = yaml.full_load(file)

# print(yaml.dump(file_contents))
# print(len([key for key in file_contents]))
# print(len(file_contents))
# print(file_contents[0]['mission']) # zero'th match, missionname
# print(file_contents[0]['date'])
# print(file_contents[0]['results'])

# create player dictionary
# playerdata = dict()

# Point Whore Glickos
pwglickos = dict()
# Single Team Whore Glickos
stpwglickos = dict()
# Team Player Glickos
tpglickos = dict()

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

print(first_roles_to_players)
print(any_roles_to_players)

# quit()



player_to_win_count = dict()
player_to_match_count = dict()
duo_to_win_count = dict()
duo_to_match_count = dict()
trio_to_win_count = dict()
trio_to_match_count = dict()


# loop over all matches
for match in file_contents:
  print()
  print(match['date'], match['mission'])
  winning_team_score = 0
  winning_team_name = None
  results = match['results']
  # match
  merged_match_player_results = list()
  for team in results:
    print('team:', team)
    if results[team]['score'] > winning_team_score:
      winning_team_score = results[team]['score']
      winning_team_name = team
    # print('input unsorted')
    # for player in results[team]['players']:
    #   print('player:', player)
    
    # results[team]['players'].sort(key=itemgetter(2), reverse=True)

    # print('input sorted')
    # print('appending to list this thing',results[team]['players'],type(results[team]['players']), type(results[team]['players'][0]))

    team_player_results = list()

    # parse the string as a tuple
    for player in results[team]['players']:
      player_split = player.split(", ")
      # print('player_split:',player_split)
      player_tuple = (player_split[0], int(player_split[1]))
      # print('xx:"',player,'"')
      # print('xx:',player_tuple)

      # todo consider removing the bottom 20% or something, to filter out people who had connection problems

      merged_match_player_results.append(player_tuple)
      team_player_results.append(player_tuple)

      # initialize glicko objects for each player, if not already initialized
      if player_tuple[0] not in pwglickos:
        pwglickos[player_tuple[0]] = glicko2.Player()
      if player_tuple[0] not in stpwglickos:
        stpwglickos[player_tuple[0]] = glicko2.Player()
      if player_tuple[0] not in tpglickos:
        tpglickos[player_tuple[0]] = glicko2.Player()

    # per team point whore glicko updates
    team_player_results.sort(key=itemgetter(1), reverse=True)
    for better_player, worse_player in pairwise(team_player_results):
      # score ties
      lose = 0
      win = 1
      if better_player[1] == worse_player[1]:
        lose = 0.5
        win = 0.5
      # print('bp:', better_player)
      # print('wp:', worse_player)
      worse_player_glicko = stpwglickos[worse_player[0]]
      stpwglickos[better_player[0]].update_player([worse_player_glicko.rating], [worse_player_glicko.rd], [win])
      better_player_glicko = stpwglickos[better_player[0]]
      stpwglickos[worse_player[0]].update_player([better_player_glicko.rating], [better_player_glicko.rd], [lose])

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

    # TRIOS
    for trio in distinct_combinations(results[team]['players'], 3):
      trio0split = trio[0].split(", ")
      trio1split = trio[1].split(", ")
      trio2split = trio[2].split(", ")
      player_name_trio=(trio0split[0],trio1split[0],trio2split[0])
      # print('trio ',player_name_trio,' appeared in match ',match)
      if not player_name_trio in trio_to_win_count:
        trio_to_win_count[player_name_trio] = 0
      if not player_name_trio in trio_to_match_count:
        trio_to_match_count[player_name_trio] = 0
      trio_to_match_count[player_name_trio]+=1
      if team == winning_team_name:
        trio_to_win_count[player_name_trio]+=1

  # for player in merged_match_player_results:
  #   print('inplayer:', player)

  # Sort all of the players in the match by their scores
  merged_match_player_results.sort(key=itemgetter(1), reverse=True)

  for better_player, worse_player in pairwise(merged_match_player_results):
    # score ties
    lose = 0
    win = 1
    if better_player[1] == worse_player[1]:
      lose = 0.5
      win = 0.5

    # print('bp:', better_player)
    # print('wp:', worse_player)
    worse_player_glicko = pwglickos[worse_player[0]]
    pwglickos[better_player[0]].update_player([worse_player_glicko.rating], [worse_player_glicko.rd], [win])
    better_player_glicko = pwglickos[better_player[0]]
    pwglickos[worse_player[0]].update_player([better_player_glicko.rating], [better_player_glicko.rd], [lose])

  # for player in merged_match_player_results:
  #   print(player[0], pwglickos[player[0]].rating, pwglickos[player[0]].rd)

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

  for losing_team_player in results[losing_team_name]['players']:
    losing_player_split = losing_team_player.split(", ")
    losing_player_tuple = (losing_player_split[0], int(losing_player_split[1]))
    # print('losing_team_player:',losing_player_tuple[0])
    for winning_team_player in results[winning_team_name]['players']:
      winning_player_split = winning_team_player.split(", ")
      winning_player_tuple = (winning_player_split[0], int(winning_player_split[1]))
      # print('winning_team_player:',winning_player_tuple[0])
      # if winning_player_split[1] > losing_player_split[1]:
      tpglickos[losing_player_tuple[0]].update_player([tpglickos[winning_player_tuple[0]].rating],[tpglickos[winning_player_tuple[0]].rd],[lose])
      tpglickos[winning_player_tuple[0]].update_player([tpglickos[losing_player_tuple[0]].rating],[tpglickos[losing_player_tuple[0]].rd],[win])
    
  
# Sort by glicko ratings and print them out
pwglickolist = list(pwglickos.items())
pwglickolist.sort(key=lambda rating: rating[1].rating, reverse=True)
print('Point Whore Ratings, sorted:\n', [(x[0], str(round(x[1].rating))) for x in pwglickolist])

# Sort by glicko ratings and print them out
stpwglickolist = list(stpwglickos.items())
stpwglickolist.sort(key=lambda rating: rating[1].rating, reverse=True)
# print('Single Team Point Whore Ratings, sorted:\n', [(x[0], str(round(x[1].rating))) for x in stpwglickolist])
print('\nSingle Team Point Whore Ratings',"\n".join([ str((x[0], str(round(x[1].rating)), str(round(x[1].rd)))) for x in stpwglickolist]))

# Sort by glicko ratings and print them out
tpglickolist = list(tpglickos.items())
tpglickolist.sort(key=lambda rating: rating[1].rating, reverse=True)
print('\nTeam Player Ratings, sorted:')
print("\n".join([ str((x[0], str(round(x[1].rating)), str(round(x[1].rd)))) for x in tpglickolist]))

print('\nPer role single team point whore ratings:\n')
for role, players in first_roles_to_players.items():
  # print('unsorted:',role,players)
  players.sort(key=lambda p: stpwglickos[p].rating if p in stpwglickos else 1400, reverse=True)
  print('sorted:',role,players)

# Print conditional probabilities
player_to_win_rate = dict()
for matchkvp in player_to_match_count.items():
  # Only use data with at least 10 samples (matches)
  if matchkvp[1] < 30:
    continue
  player_to_win_rate[matchkvp[0]] = player_to_win_count[matchkvp[0]] / matchkvp[1]
player_to_win_rate_sorted = list(player_to_win_rate.items())
player_to_win_rate_sorted.sort(key=lambda p: p[1], reverse=True)
print('Best player win rates:\n','\n'.join([str(x) for x in player_to_win_rate_sorted]))
# print(player_to_match_count)
# print(player_to_win_count)

duo_to_win_rate = dict()
for matchkvp in duo_to_match_count.items():
  # Only use data with at least 10 samples (matches)
  if matchkvp[1] < 17:
    continue
  duo_to_win_rate[matchkvp[0]] = duo_to_win_count[matchkvp[0]] / matchkvp[1]
duo_to_win_rate_sorted = list(duo_to_win_rate.items())
duo_to_win_rate_sorted.sort(key=lambda p: p[1], reverse=True)
print('Best duo win rates:\n','\n'.join([str(x) for x in duo_to_win_rate_sorted]))
# print(duo_to_match_count)
# print(duo_to_win_count)



trio_to_win_rate = dict()
for matchkvp in trio_to_match_count.items():
  # Only use data with at least 10 samples (matches)
  if matchkvp[1] < 9:
    continue
  trio_to_win_rate[matchkvp[0]] = trio_to_win_count[matchkvp[0]] / matchkvp[1]
trio_to_win_rate_sorted = list(trio_to_win_rate.items())
trio_to_win_rate_sorted.sort(key=lambda p: p[1], reverse=True)
print('Best trio win rates:\n','\n'.join([str(x) for x in trio_to_win_rate_sorted]))
# print(trio_to_match_count)
# print(trio_to_win_count)
