import numpy as np  

from cleaner import get_data

K = 5
f = open('/home/christopher/data_bin/train_test_1car_randomforestdecisions.txt')
train, test = get_data(f)
df = test


from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor

from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC, SVR
from sklearn import cross_validation
from sklearn import metrics

from sknn.mlp import Classifier, Layer, Regressor
from sklearn.cross_validation import LeaveOneOut, StratifiedKFold
from sklearn import preprocessing

def equalize_train_labels(y):
	import random
	neg_indices = []
	pos_indices = []
	for i, val in enumerate(y):
		if val > 0:
			pos_indices.append(i)
		else:
			neg_indices.append(i)
	if len(pos_indices) > len(neg_indices):
		pos_indices = random.sample(pos_indices, len(neg_indices))
	else:
		neg_indices = random.sample(neg_indices, len(pos_indices))
	return sorted(pos_indices+neg_indices)


        
def k_fold_predict_proba(clf, x, y, k):
	x = np.array(x)
	y = np.array(y)
	pred_probas = np.zeros(len(y))
	skf = StratifiedKFold(y, k, shuffle=False, random_state=False)
	for train_indices, test_indices in skf:
	    clf.fit(x[train_indices],y[train_indices])
	    pred_probas[test_indices] = clf.predict_proba(x[test_indices])
	return pred_probas

def cutoff_for_desired_recall(y, pred_probas, desired_recall=0.95):
	precision, recall, thresholds = metrics.precision_recall_curve(y, pred_probas)
	reversed_recall = np.array(list(reversed(recall)))
	reversed_thresh = np.array(list(reversed(thresholds)))
	thresh_index = np.argmax(reversed_recall >= desired_recall)
	if reversed_thresh[thresh_index-1] == 0:
		return reversed_thresh[thresh_index-2]
	return reversed_thresh[thresh_index-1]



def proba_analysis(y, pred_probas, cut_off):
	preds = [proba >= cut_off for proba in pred_probas]
	print metrics.classification_report(y, preds)
	# precision, recall, thresholds = metrics.precision_recall_curve(y, pred_probas)
	# print precision
	# print recall

def makeTrainData(x_cols, y_col):
	train_x = np.array(df[x_cols])
	train_y = np.array(df[y_col])
	return train_x, train_y

def classification_test(X, Y, equalize=True):
	if equalize:
		indices_to_use = equalize_train_labels(Y)
		partial_x = X[indices_to_use]
		partial_y = Y[indices_to_use]
	else:
		partial_x = X
		partial_y = Y
	norm_train_x = preprocessing.MinMaxScaler((-1,1)).fit_transform(partial_x)
	# nn0 = Classifier(layers=[Layer("Sigmoid", units=10),Layer("Softmax")],learning_rate=0.01, n_iter=100)

	max_layer_size = len(x_cols)**2
	max_layers = [Layer("Sigmoid", units=max_layer_size/4),
				  Layer("Rectifier", units=max_layer_size/2),
				  # Layer("Sigmoid", units=max_layer_size/2),
				  # Layer("Sigmoid", units=max_layer_size/4),
				  Layer("Softmax")]
	nn = Classifier(layers=max_layers,learning_rate=0.08, n_iter=300)


	classifiers = [('Random Forest Classifier', RandomForestClassifier(n_estimators=100), False), 
				   ('AdaBoost Classifier', AdaBoostClassifier(), False), 
				   ('SVC', SVC(probability=True), False), 
				   ('Bernoulli NB', BernoulliNB(), False),
				   ('Neural Net w/ Sigmoid -> Rectifier -> Softmax', nn, True)]

	for name, clf, norm in classifiers:
		if norm:
			train_x = norm_train_x
		else:
			train_x = partial_x
		print name
		pred_probas = k_fold_predict_proba(clf, train_x, partial_y, K)
		cutoff = cutoff_for_desired_recall(partial_y, pred_probas)
		proba_analysis(partial_y, pred_probas, cutoff)
		preds = cross_validation.cross_val_predict(clf, train_x, partial_y, cv=K)
		print metrics.classification_report(partial_y, preds)

def regression_test(X, Y):
	norm_train_x = preprocessing.MinMaxScaler((-1,1)).fit_transform(X)

	max_layer_size = len(x_cols)**2
	max_layers = [Layer("Sigmoid", units=max_layer_size/4),
				  Layer("Sigmoid", units=max_layer_size/2),
				  # Layer("Sigmoid", units=max_layer_size/2),
				  # Layer("Sigmoid", units=max_layer_size/4),
				  Layer("Linear")]
	nn = Regressor(layers=max_layers,learning_rate=0.08, n_iter=300)

	regressors = [('Random Forest Regressor', RandomForestRegressor(n_estimators=100), False), 
				   ('AdaBoost Regressor', AdaBoostRegressor(), False), 
				   ('SVR', SVR(), False), 
				   ('Neural Net w/ Sigmoid -> Sigmoid -> Linear', nn, True)]

	for name, reg, norm in regressors:
		if norm:
			train_x = norm_train_x
		else:
			train_x = X
		print name

		preds = cross_validation.cross_val_predict(reg, train_x, Y, cv=K)
		print 'R^2:', metrics.r2_score(Y, preds)
		



x_cols = ['curCar starting_speed', 'starting_distance', 'discretizedBrakes', 'discretizedSteering']

print '################# CLASSIFICATION TEST FOR %s #################' %  'collision'
classification_test(*makeTrainData(x_cols, 'collision'))

print '################# CLASSIFICATION TEST FOR %s #################' %  'curCar went_offroad'
classification_test(*makeTrainData(x_cols, 'curCar went_offroad'))

print '################# CLASSIFICATION TEST FOR %s #################' %  'collisionOrOffroad'
classification_test(*makeTrainData(x_cols, 'collisionOrOffroad'))

print '################# REGRESSION TEST FOR %s #################' %  'curCar maxAccel'
regression_test(*makeTrainData(x_cols, 'curCar maxAccel'))

print '################# REGRESSION TEST FOR %s #################' %  'curCar avgAccel'
regression_test(*makeTrainData(x_cols, 'curCar avgAccel'))