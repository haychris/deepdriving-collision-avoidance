import matplotlib.pyplot as plt
import seaborn as sns
from cleaner import get_data

f = open('/home/christopher/data_bin/summary_car_data.txt')
df = get_data(f)
x_cols = ['curCar starting_speed', 'starting_distance', 'discretizedBrakes', 'discretizedSteering']
g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='collision')
g.map(plt.scatter, 'speedDifference', 'starting_distance')
g.add_legend()
plt.show()


g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='curCar went_offroad')
g.map(plt.scatter, 'curCar starting_speed', 'starting_distance')
g.add_legend()
plt.show()


g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='collisionOrOffroad')
g.map(plt.scatter, 'curCar starting_speed', 'starting_distance')
g.add_legend()
plt.show()