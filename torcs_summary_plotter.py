import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class AnimatedScatter(object):
    """An animated scatter plot using matplotlib.animations.FuncAnimation."""
    def __init__(self):
        self.stream = self.data_stream()
        self.f = open('/home/christopher/data_bin/summary_car_data.txt')


        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=5, 
                                           init_func=self.setup_plot, blit=True)

    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        dat = next(self.stream)
        x = dat[:, 0]
        y = dat[:, 1]
        s = dat[:, 2]
        c = dat[:, 3]
        self.scat = self.ax.scatter(x, y, c=c, s=s, animated=True)
        # self.ax.axis([0, 100, 0, 100])

        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def get_next_data_point(self):
        cur_row = []
        while True:
            line = self.f.readline()
            if line == '':
                continue
            if line == '.\n':
                return cur_row
            else:
                split = line.split()
                value = float(split[-1])
                cur_row.append(value)
    def data_stream(self):
        """Generate a random walk (brownian motion). Data is scaled to produce
        a soft "flickering" effect."""
        data = np.zeros((1,4))
        # x = data[:, 0]
        # y = data[:, 1]
        # s = data[:, 2]
        # c = data[:, 3]
        count = 0

        while True:
            cur_row = self.get_next_data_point()
            data[count] = cur_row[:4]
            count += 1
            cur_size = len(data)
            if count >= cur_size:
                new_rows = np.zeros((cur_size,4))
                data = np.vstack([data, new_rows])
            yield data

    def update(self, i):
        """Update the scatter plot."""
        data = next(self.stream)

        # Set x and y data...
        self.scat.set_offsets(data[:,:2])
        # Set sizes...
        self.scat._sizes = (0.1 * abs(data[:,2]))**1.5 + 10
        # Set colors..
        self.scat.set_array(data[:,3])

        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def show(self):
        plt.show()

if __name__ == '__main__':
    a = AnimatedScatter()
    a.show()