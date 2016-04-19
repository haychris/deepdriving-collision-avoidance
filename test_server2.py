from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools  
import time


from cleaner import get_data

K = 5
f = open('/home/christopher/data_bin/train_test_1car_randomforestdecisions.txt')
train, test = get_data(f)
df = train

print 'Fitting model'
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC
from sklearn import cross_validation
from sklearn import metrics
x_cols = ['curCar starting_speed', 'starting_distance', 'discretizedBrakes', 'discretizedSteering']
y_col = 'collisionOrOffroad'
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
# behaviors = [(0,0), (0,1), (1,0), (1,1)]
brakesBehaviors = sorted(set(df['discretizedBrakes']))
steeringBehaviors = sorted(set(df['discretizedSteering']))
behaviors = list(itertools.product(brakesBehaviors, steeringBehaviors))

probs = np.zeros(len(behaviors))

request_size = len(x_cols) - len(behaviors[0])
x2 = np.array([(0, 0, beh[0], beh[1]) for beh in behaviors])

while True:
	#  Wait for next request from client
	message = socket.recv()
	t0 = time.time()
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
			x2[:, i] = float(num)
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
	# print x2

	# x2 = [(float(split[0]), float(split[1]), beh[0], beh[1]) for beh in behaviors]
	probs = rfc.predict_proba(x2)
	min_proba_behavior = behaviors[np.argmin(probs[:,1])]

	# for i, behavior in enumerate(behaviors):
	# 	x[0, len(split):] = behavior
	# 	prob = rfc.predict_proba(x)
	# 	probs[i] = prob[0,1]
	# 	import pdb; pdb.set_trace()
	# 	# prob_collision = prob[0,1]
	# 	# probs[i] = prob_collision
	print probs[:,1]
	# min_proba_behavior = behaviors[np.argmin(probs)]
	string_behavior = [str(num) for num in min_proba_behavior]
	result = ' '.join(string_behavior) + '\n'
	print result
	#  Send reply back to client
	socket.send(result)
	print "Processed in %fms" % ((time.time() - t0)*1000)
