from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

f = open('/home/christopher/data_bin/old_summary_car_data.txt')

print 'Cleaning data'
data = defaultdict(list)
for line in f:
	if line in '.\n':
		continue
	split = line.split(':')
	key = split[0]
	value = float(split[1])
	data[key].append(value)

df = pd.DataFrame(data)
df['totalDamage'] = df['Car0 damage'] + df['Car1 damage']
df['scaledDamage'] = df['totalDamage'] / 100
df['speedDifference'] = df['Car1 speed'] - df['Car0 speed']
df['collision'] = (df['Car0 damage'] > 10) & (df['Car1 damage'] > 10)

df['Distance'] = df['Distance'].where(df['Distance'] > 0, float('NaN'))

df = df.dropna()


print 'Fitting model'
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC
from sklearn import cross_validation
from sklearn import metrics
x_cols = ['Car0 speed', 'Car1 speed', 'Distance', 'useBrakes', 'useSteering']
y_col = 'collision'
train_x = df[x_cols]
train_y = df[y_col]

rfc = RandomForestClassifier(n_estimators=100)
rfc.fit(train_x, train_y)

#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import numpy as np

print 'Establishing server'

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
print 'Waiting for requests'

x = np.zeros((1,len(x_cols)))
behaviors = [(0,0), (0,1), (1,0), (1,1)]
probs = np.zeros(len(behaviors))

request_size = len(x_cols) - len(behaviors[0])
while True:
	#  Wait for next request from client
	message = socket.recv()
	print("Received request: \"%s\"" % message)

	#  Do some 'work'
	split = message.split()
	# print split
	# if len(split) != request_size:
	# 	print 'ERROR, incorrect request size'
	# 	min_proba_behavior = behaviors[np.argmin(probs)]
	# 	string_behavior = [str(num) for num in min_proba_behavior]
	# 	result = ' '.join(string_behavior) + '\n'
	# 	#  Send reply back to client
	# 	socket.send(result)
	# 	continue
	# request = [float(num) for num in split]
	# x[0, :len(request)] = request
	try:
		for i,num in enumerate(split):
			x[0, i] = float(num)
	except ValueError as e:
		print 'ERROR, incorrect request size'
		min_proba_behavior = behaviors[np.argmin(probs)]
		string_behavior = [str(num) for num in min_proba_behavior]
		result = ' '.join(string_behavior) + '\n'
		#  Send reply back to client
		socket.send(result)
		continue
	if np.any(np.isnan(x)):
		print 'ERROR, NaN'
		min_proba_behavior = behaviors[np.argmin(probs)]
		string_behavior = [str(num) for num in min_proba_behavior]
		result = ' '.join(string_behavior) + '\n'
		#  Send reply back to client
		socket.send(result)
		continue

	for i, behavior in enumerate(behaviors):
		x[0, len(split):] = behavior
		prob = rfc.predict_proba(x)
		probs[i] = prob[0,1]
		# prob_collision = prob[0,1]
		# probs[i] = prob_collision
	print probs
	min_proba_behavior = behaviors[np.argmin(probs)]
	string_behavior = [str(num) for num in min_proba_behavior]
	result = ' '.join(string_behavior) + '\n'
	print result
	#  Send reply back to client
	socket.send(result)