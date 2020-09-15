import sys
import json
import io


# Read JSON file
# Inputs:
#    filename: The JSON file to read
# Output:
#    The data read from the file
def read_json_file( filename ):
  file = open( filename, "r", encoding="utf-8" )
  data = json.load( file )
  file.close()
  return data


# Write JSON file
# Inputs:
#    filename: The JSON file to write
#    data:     The data to write
# Output:
#    N/A, the file is written
def write_json_file( filename, data ):
  file = open( filename, "w", encoding="utf-8" )
  json.dump( data, file )
  file.close()


# Process the score distribution by converting multiplicities to probabilities
# Inputs:
#    score_distribution: The distribution of scores in dictionary score -> multiplicity form
#    team_count:         The number of teams participating
#    round_count:        The number of rounds
# Outputs:
#    The new score distribution
def preprocess_score_distribution( score_distribution, team_count, round_count ):
  new_distribution = {}
  outcome_space = pow( team_count, round_count )

  for score in score_distribution:
    new_distribution[ int( score ) ] = score_distribution[ score ] / outcome_space
  
  return new_distribution


# Calculate winning odds for each team
# Inputs:
#    score_distribution: The distribution of scores
#    team_input: The input team data mapping team name to starting score
# Output:
#    Dictionary mapping team name to first, second, and third place odds
def calculate_winning_odds( score_distribution, team_input ):
  team_output = {}

  for team in range( len( team_input ) ):
    team_output[ list( team_input.keys() )[ team ] ] = calculate_team_odds( team, score_distribution, team_input )
  
  return team_output


# Calculate the odds of a team winning
# Inputs:
#    team:               The # of the team we're calculating for
#    score_distribution: The score distribution being used
#    team_input:         The input from all the teams
# Output:
#    The data for the team (odds of first, second, and third)
def calculate_team_odds( team, score_distribution, team_input ):
  team_odds = {}
  team_odds[ "first" ] = calculate_team_first_odds( team, score_distribution, team_input )
  team_odds[ "second" ] = calculate_team_second_odds( team, score_distribution, team_input )
  team_odds[ "third" ] = calculate_team_third_odds( team, score_distribution, team_input )
  team_odds[ "podium" ] = team_odds[ "first" ] + team_odds[ "second" ] + team_odds[ "third" ]
  return team_odds


# Calculate the odds of a team winning first
# Inputs:
#    team:               The # of the team we're calculating for
#    score_distribution: The score distribution being used
#    team_input:         The input from all the teams
# Output:
#    The odds of winning
def calculate_team_first_odds( team, score_distribution, team_input ):
  return compare_teams( team, [], score_distribution, team_input )


# Calculate the odds of a team winning second
# Inputs:
#    team:               The # of the team we're calculating for
#    score_distribution: The score distribution being used
#    team_input:         The input from all the teams
# Output:
#    The odds of winning
def calculate_team_second_odds( team, score_distribution, team_input ):
  odds = 0.0

  for team_2 in range( len( team_input ) ):
    if team_2 == team:
      continue
      
    odds += compare_teams( team, [ team_2 ], score_distribution, team_input )
  
  return odds


# Calculate the odds of a team winning third
# Inputs:
#    team:               The # of the team we're calculating for
#    score_distribution: The score distribution being used
#    team_input:         The input from all the teams
# Output:
#    The odds of winning
def calculate_team_third_odds( team, score_distribution, team_input ):
  odds = 0.0

  for team_2 in range( len( team_input ) ):
    if team_2 == team:
      continue

    for team_3 in range( len( team_input ) ):
      if team_3 == team or team_3 <= team_2:
        continue

      odds += compare_teams( team, [ team_2, team_3 ], score_distribution, team_input )
  
  return odds


# Find the odds that one team did worse than a set of listed teams but better than the rest
# Inputs:
#    team:               The # of the team we're checking against others
#    better_teams:       Array of the #s of the potentially better teams
#    score_distribution: The distribution of scores
#    team_input:         The input data for the teams
# Output:
#    Odds of the team losing to the specified teams but winning against the rest of the teams
def compare_teams( team, better_teams, score_distribution, team_input ):
  odds = 0.0

  for score in score_distribution:
    score_odds = compare_teams_at_score( team, better_teams, score, score_distribution, team_input )
    score_odds *= score_distribution[ score ]
    odds += score_odds
  
  return odds


# Find the odds that, at a given pick from the score distribution, a team will do worse than specific teams and better than the rest
# Inputs:
#    team:               The # of the team we're checking against others
#    better_teams:       Array of the #s of the potentially better teams
#    score:              The score picked from the distribution that we're checking as our base
#    score_distribution: The distribution of scores
#    team_input:         The inputs for the various teams
# Output:
#    The odds that, at the given score, the team will do worse than specified teams but better than the rest
def compare_teams_at_score( team, better_teams, score, score_distribution, team_input ):
  odds = 1.0

  for i in range( len( team_input ) ):
    if i == team:
      continue
    
    if i in better_teams:
      odds *= 1.0 - probability_team_greater( team, i, score, score_distribution, team_input )
    else:
      odds *= probability_team_greater( team, i, score, score_distribution, team_input )
  
  return odds


# ...
def probability_team_greater( team, other_team, score, score_distribution, team_input ):
  team_name = list( team_input.keys() )[ team ]
  other_team_name = list( team_input.keys() )[ other_team ]
  base_score = score + team_input[ team_name ]
  odds = 0.0

  for sc in score_distribution:
    other_score = sc + team_input[ other_team_name ]
    if base_score >= other_score:
      odds += score_distribution[ sc ]

  return odds


# Normalize the odds so 1st, 2nd, and 3rd places each have a total 100% odds
def normalize_odds( data ):
  first_sum = 0.0
  second_sum = 0.0
  third_sum = 0.0

  for team in data:
    first_sum += data[ team ][ "first" ]
    second_sum += data[ team ][ "second" ]
    third_sum += data[ team ][ "third" ]
  
  for team in data:
    data[ team ][ "first" ] /= first_sum
    data[ team ][ "second" ] /= second_sum
    data[ team ][ "third" ] /= third_sum
  
  return data


def round_odds( data ):
  for team in data:
    data[ team ][ "first" ] = round( data[ team ][ "first" ], 4 )
    data[ team ][ "second" ] = round( data[ team ][ "second" ], 4 )
    data[ team ][ "third" ] = round( data[ team ][ "third" ], 4 )
    podium = data[ team ][ "first" ] + data[ team ][ "second" ] + data[ team ][ "third" ]
    data[ team ][ "podium" ] = podium
  
  return data


def main():
  distribution_filename = sys.argv[ 1 ]
  team_input_filename = sys.argv[ 2 ]
  round_count = int( sys.argv[ 3 ] )
  team_output_filename = sys.argv[ 4 ]

  # Read the score distribution file and team input data
  team_input = read_json_file( team_input_filename )
  team_count = len( team_input )
  score_distribution = read_json_file( distribution_filename )
  score_distribution = preprocess_score_distribution( score_distribution, team_count, round_count )

  # Calculate odds and write out
  team_output = calculate_winning_odds( score_distribution, team_input )
  team_output = normalize_odds( team_output )
  team_output = round_odds( team_output )
  write_json_file( team_output_filename, team_output )


if __name__ == "__main__":
  main()
