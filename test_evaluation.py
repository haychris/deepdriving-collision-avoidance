import matplotlib.pyplot as plt
import seaborn as sns
from cleaner import get_data

f = open('/home/christopher/data_bin/train_test_1car_randomforestdecisions.txt')
train, test = get_data(f)
df = test
x_cols = ['curCar starting_speed', 'starting_distance', 'discretizedBrakes', 'discretizedSteering']
# df['bad'] = df['collision'] + 2*df['curCar went_offroad']
# sns.stripplot(x='speedDifference', y='starting_distance', data=df, hue='collision')
# plt.scatter(df['speedDifference'], df['starting_distance'], c=df['bad'])
# sns.jointplot(x="speedDifference", y="starting_distance",  color='collision_offroad', hue_order=['None', 'Collision', 'Offroad', 'Collision & Offroad'],data=df)
# plt.show()



g = sns.FacetGrid(df, hue='collision_offroad', hue_order=['None', 'Collision', 'Offroad', 'Collision & Offroad'])
g.map(plt.scatter, 'speedDifference', 'starting_distance')
g.add_legend()
plt.show()
