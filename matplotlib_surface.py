#!/usr/bin/env	python3
# -*- coding: <UTF-8> -*-

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np


Mat = np.random.rand(50,64)  # random matrix 2D
## reshape nicht notwendig
np.set_printoptions(precision=2)


fig = plt.figure()
ax = fig.gca(projection='3d')

X = np.arange(Mat[:1, :].size, dtype='int')  # 0-63
Y = np.arange(Mat[:, :1].size, dtype='int')  # 0-49
X, Y = np.meshgrid(X, Y)
Z = Mat

fig = plt.figure()
ax = fig.gca(projection='3d')

surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, linewidth=1, antialiased=False)

#  legend
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()

