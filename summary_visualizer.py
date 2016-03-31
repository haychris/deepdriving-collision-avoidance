from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

f = open('/home/christopher/data_bin/old_summary_car_data.txt')
K = 5

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

g = sns.FacetGrid(df, col='useBrakes', row='useSteering', hue='collision')
g.map(plt.scatter, 'speedDifference', 'Distance')
# g.map(plt.scatter, 'speedDifference', 'Distance', 'scaledDamage')
g.add_legend()
plt.show()


from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC
from sklearn import cross_validation
from sklearn import metrics
x_cols = ['Car0 speed', 'Car1 speed', 'Distance', 'useBrakes', 'useSteering']
y_col = 'collision'
train_x = df[x_cols]
train_y = df[y_col]

classifiers = [RandomForestClassifier(n_estimators=100), AdaBoostClassifier(), SVC(), BernoulliNB()]

for classifier in classifiers:
	print classifier
	preds = cross_validation.cross_val_predict(classifier, train_x, train_y, cv=K)
	print metrics.classification_report(train_y, preds)
	print metrics.confusion_matrix(train_y, preds)


rfc = RandomForestClassifier(n_estimators=100)
rfc.fit(train_x, train_y)
print rfc.feature_importances_

def plot_confusion_matrix(cm, names=None, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    if names is not None:
	    tick_marks = np.arange(len(names))
	    plt.xticks(tick_marks, names, rotation=45)
	    plt.yticks(tick_marks, names)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')



preds = cross_validation.cross_val_predict(rfc, train_x, train_y, cv=K)
import numpy as np
# Compute confusion matrix
cm = metrics.confusion_matrix(train_y, preds)
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
np.set_printoptions(precision=2)
print('Confusion matrix, with normalization')
print(cm_normalized)
plt.figure()
plot_confusion_matrix(cm_normalized, ['No Collision', 'Collision'])
plt.show()