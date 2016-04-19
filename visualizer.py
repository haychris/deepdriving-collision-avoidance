import matplotlib.pyplot as plt
import seaborn as sns
from cleaner import get_data

f = open('/home/christopher/data_bin/train_test_1car_randomforestdecisions.txt')
train, test = get_data(f)
df = train
x_cols = ['curCar starting_speed', 'starting_distance', 'discretizedBrakes', 'discretizedSteering']
# df['bad'] = df['collision'] + 2*df['curCar went_offroad']
g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='collision_offroad', hue_order=['None', 'Collision', 'Offroad', 'Collision & Offroad'])
g.map(plt.scatter, 'speedDifference', 'starting_distance')
g.add_legend()
plt.show()


# g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='collision')
# g.map(plt.scatter, 'speedDifference', 'starting_distance')
# g.add_legend()
# plt.show()


# g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='curCar went_offroad')
# g.map(plt.scatter, 'curCar starting_speed', 'starting_distance')
# g.add_legend()
# plt.show()


# g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='collisionOrOffroad')
# g.map(plt.scatter, 'curCar starting_speed', 'starting_distance')
# g.add_legend()
# plt.show()