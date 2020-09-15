import sys
import json
import io

#PLAYER_COUNT = 16
#SCORING = [ 25, 20, 15, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 ] # Marble League 2020
PLAYER_COUNT = 20
SCORING =  [ 20, 17, 14, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0] # Marble Rally 2020


# Calculate the factorial of a number
# Inputs:
#    n: The number to take the factorial of
# Output:
#    n factorial (n!)
def factorial( n ):
	if n == 0 or n == 1:
		return 1
	
	if n < 0:
		return 0 # what is this nonsense don't give negative numbers that's rude
	
	return n * factorial( n-1 )


# Calculate the score of a given placement distribution
# Inputs:
#    placements: The placement distribution
# Output:
#    The score for the given distribution
def calculate_score( placements ):
	score = 0
	for i in range( len( placements ) ):
		score += SCORING[ i ] * placements[ i ]
	return score


# Calculate the multiplicity of a given placement distribution (calculates multinomial coefficients)
# Inputs:
#    placements: The placement distribution
# Output:
#    The multiplicity of the distribution (the multinomial coefficient)
def calculate_multiplicity( placements ):
	# Find the total number of rounds
	sum = 0
	for i in range( len( placements ) ):
		sum += placements[ i ]
	
	#print( "Sum {0}".format( sum ) )

	# Calculate the multinomial distribution
	multiplicity = factorial( sum )
	for i in range( len( placements ) ):
		multiplicity = multiplicity // factorial( placements[ i ] )
	
	return multiplicity


# Calculate the score distribution with recursion
# Inputs:
#    rounds: The number of remaining rounds
#    placements: The number of remaining placement possibilities
#    current_placements: The current distribution of placements
#    current_distribution: The current distribution that is being updated
def calculate_score_distribution( rounds, placements, current_placements, current_distribution ):
	#print( "Calculating with {0} rounds, {1} placements, {2} current placement dist".format( rounds, placements, current_placements ) )
	#print( "Calculating with {0} rounds, {1} placements".format( rounds, placements ) )

	# Start by checking if we're finished
	if rounds == 0 and placements == 0:
		score = calculate_score( current_placements )
		multiplicity = calculate_multiplicity( current_placements )

		# Add the score to the distribution
		if score in current_distribution:
			current_distribution[ score ] += multiplicity
		else:
			current_distribution[ score ] = multiplicity
		return
	
	# Next check if we have a Problem That Shall Be Ignored Silently
	if placements == 0:
		return
	
	# Recurse!
	for i in range( rounds+1 ):
		# Copy and update the win distribution
		new_placements = current_placements.copy()
		new_placements.append( i )

		# And go onto the next placement set
		calculate_score_distribution( rounds-i, placements-1, new_placements, current_distribution )


# Create a dictionary representing the data for the specified number of players and rounds
# Inputs:
#    rounds: The number of rounds in the league to simulate
# Output:
#    A dictionary representing the final score distribution for the specified parameters
def create_data( rounds ):
	score_distribution = {}

	calculate_score_distribution( rounds, PLAYER_COUNT, [], score_distribution )
	return score_distribution


# Create the data file at filename for the specified number of players and rounds
# Inputs:
#   filename: The name of the file to store the data at
#   rounds:   The number of rounds in the league to simulate
def create_data_file( filename, rounds ):
	# Run the simulation
	data = create_data( rounds )

	# Replace multiplicities with string form
	#for key,value in data.items():
	#	data[ key ] = str( value )

	# Save it to a file
	file = open( filename, "w", encoding="utf-8" )
	json.dump( data, file )
	file.close()


def main():
	create_data_file( sys.argv[ 1 ], int( sys.argv[ 2 ], base=10 ) )


if __name__ == "__main__":
	main()
