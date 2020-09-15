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


def main():
  test_filename = sys.argv[ 1 ]
  team_count = int( sys.argv[ 2 ] )
  round_count = int( sys.argv[ 3 ] )

  data = read_json_file( test_filename )
  data = preprocess_score_distribution( data, team_count, round_count )

  total_odds = 0.0
  for score in data:
    total_odds += data[ score ]

  print( total_odds )


if __name__ == "__main__":
  main()