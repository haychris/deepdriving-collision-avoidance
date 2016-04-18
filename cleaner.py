from collections import defaultdict
import pandas as pd

def get_data(f, num_categories=5):
	data = defaultdict(list)
	for line in f:
		if line in '.\n':
			continue
		split = line.split(':')
		key = split[0]
		value = float(split[1])
		data[key].append(value)

	df = pd.DataFrame(data)
	df['curCar deltaDamage'] = df['curCar final_damage'] - df['curCar starting_damage']
	df['obstacleCarAhead deltaDamage'] = df['obstacleCarAhead final_damage'] - df['obstacleCarAhead starting_damage']

	df['totalDamage'] = df['curCar deltaDamage'] + df['obstacleCarAhead deltaDamage']
	df['scaledDamage'] = df['totalDamage'] / 100
	df['speedDifference'] = df['curCar starting_speed'] - df['obstacleCarAhead starting_speed']
	df['collision'] = (df['curCar deltaDamage'] > 0) & (df['obstacleCarAhead deltaDamage'] > 0)

	df['discretizedBrakes'] = [round(num*(num_categories/10.0), 1)/(num_categories/10.0) for num in df['useBrakes']]
	df['discretizedSteering'] = [round(num*(num_categories/10.0), 1)/(num_categories/10.0) for num in df['useSteering']]

	df['collisionOrOffroad'] = df['collision'] | df['curCar went_offroad']
	df['collision_offroad'] = df['collision'] + 2*df['curCar went_offroad']
	df = df.replace({'collision_offroad': {0: 'None', 1: 'Collision', 2: 'Offroad', 3: 'Collision & Offroad'}})

	# df['collision'] = (df['curCar deltaDamage'] > 0)


	# remove negative starting distances
	df['starting_distance'] = df['starting_distance'].where(df['starting_distance'] > 0, float('NaN'))
	df['starting_distance'] = df['starting_distance'].where(df['starting_distance'] < 1000, float('NaN'))

	df = df.dropna()
	training = df[df['Training'] == 1]
	testing = df[df['Training'] == 0]
	return training, testing