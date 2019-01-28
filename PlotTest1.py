#!/usr/bin/env	python3
# -*- coding: <UTF-8> -*-


from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np


# matrix calculation

# global coordinates x=50, y=64
Mat = np.random.rand(50, 64)  # random matrix 2D
#Mat = np.zeros((50,64), dtype=float)
#Mat[49,63] = 1

Mat = Mat*10


## reshape nicht notwendig
np.set_printoptions(precision=2)


## Create a GL View widget to display data
app = QtGui.QApplication([])


w = gl.GLViewWidget()
w.resize(1400, 900)
w.show()
w.setWindowTitle('pyqtgraph example: GLSurfacePlot')
w.setCameraPosition(distance=200)

## Add a grid to the view
gx = gl.GLGridItem()

# grid scale

# (z,x,?) (local coordinates system)
gx.scale(5, 5, 0)
#gx.setDepthValue(10)  # draw grid after surfaces since they may be translucent
gx.rotate(90, 0, 1, 0)
# translation (x, y, z)global coordinates
gx.translate(-50, 0, 50)
w.addItem(gx)
gy = gl.GLGridItem()
gy.scale(5, 5, 0)
gy.rotate(90, 1, 0, 0)
gy.translate(0, -50, 50)
w.addItem(gy)
gz = gl.GLGridItem()
gz.scale(5, 5, 0)
gz.translate(0, 0, 0)
w.addItem(gz)



#x = Mat[:, :1]  # 0-63 Mat[:1, :].shape = (1, 64)
#y = Mat[:1, :]  # 0-49

y = np.arange(64)
x = np.arange(50)
z = Mat

"""

colors = np.ones((64, 50, 10), dtype=float)
colormap = np.linspace(np.amin(Mat), np.amax(Mat), 10)
for i in range(10):
	colors[:,:,i] = colormap[i]


p4 = gl.GLSurfacePlotItem(x=x, y = y, shader = 'shaded', colors = colors.reshape(64*50,10), computeNormals=False, smooth=False)
"""

colors = np.ones((64, 50, 4), dtype=float)
colormap = np.linspace(np.amin(Mat), np.amax(Mat), 4)
for i in range(4):
	colors[:,:,i] = colormap[i]


# shader: shaded, heightColor

p4 = gl.GLSurfacePlotItem(x=x, y = y, shader = 'shaded',
                            colors = colors.reshape(64*50,4),computeNormals=True, smooth=True)


#p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)
#p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)

# whats this?
#p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
#p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])

# translate coordinates starting point (x,y,z)
# optimum (-5,-5,0)
p4.translate(-25, -25, 0)
w.addItem(p4)



def update():
	global p4, z

	p4.setData(z=z)


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1000)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
