import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import seaborn as sns

class AnimatedLineSubPlots(object):
    """An animated line plot using matplotlib.animations.FuncAnimation."""
    def __init__(self, *data_streams, **options):
        self.lims = []
        self.data_streams = data_streams
        self.data_views = [self.data_view_stream(stream) for stream in self.data_streams]

        self.xlen = int(math.ceil(math.sqrt(len(self.data_streams))))
        self.ylen = int(math.ceil(1.0*len(self.data_streams) / self.xlen))
        self.fig, self.axes = plt.subplots(self.xlen, self.ylen, figsize=(20, 10))
        if 'fps' in options:
            self.FPS = options['fps']
        else:
            self.FPS = 10000000
        if 'fpr' in options:
            self.frames_per_redraw = options['fpr']
        else:
            self.frames_per_redraw = 1000
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=1000./self.FPS, 
                                           init_func=self.setup_plot, blit=True)

    def setup_plot(self):
        """Initial drawing of the line plot."""
        self.ani_scats = []
        self.subplot_scats = []
        for i in range(len(self.data_views)):
            data, num_samples = next(self.data_views[i])
            num_lines = len(data[0]) / 2
            scats =[]
            for j in range(num_lines):
                x = data[:num_samples, 2*j]
                y = data[:num_samples, 2*j+1]
                scat, = self.axes[i%self.xlen][i/self.xlen].scatter(x, y)
                scats.append(scat)
            self.ani_scats.extend(scats)
            self.subplot_scats.append(scats)
        return self.ani_scats

    def data_view_stream(self, data_stream):
        """Data view generator for animation"""
        first_data = next(data_stream)
        num_columns = len(first_data)
        data = np.zeros((2,num_columns))
        data[0] = first_data

        xlim = [float("inf"), -float("inf")]
        ylim = [float("inf"), -float("inf")]
        self.lims.append((xlim, ylim))
        count = 1
        while True:
            cur_row = next(data_stream)
            data[count] = cur_row
            xlim[0] = min(min(cur_row[::2]), xlim[0])
            xlim[1] =  max(max(cur_row[::2]), xlim[1])
            ylim[0] = min(min(cur_row[1::2]), ylim[0])
            ylim[1] = max(max(cur_row[1::2]), ylim[1])

            count += 1
            cur_size = len(data)
            if count >= cur_size:
                new_rows = np.zeros((cur_size, num_columns))
                data = np.vstack([data, new_rows])
            yield data, count

    def update(self, frame_num):
        """Update the plot."""
        for i in range(len(self.data_views)):
            data, num_samples = next(self.data_views[i])
            num_lines = len(data[0]) / 2

            for j in range(num_lines):
                x = data[:num_samples, 2*j]
                y = data[:num_samples, 2*j+1]
                self.subplot_lines[i][j].set_xdata(x)
                self.subplot_lines[i][j].set_ydata(y)

            if frame_num % 10 == 0:
                self.axes[i%self.xlen][i/self.xlen].set_xlim(self.lims[i][0])
                self.axes[i%self.xlen][i/self.xlen].set_ylim(self.lims[i][1])
        if frame_num % self.frames_per_redraw == 0:
            plt.draw()

        return self.ani_lines

    def show(self, block=True):
        plt.show(block=block)