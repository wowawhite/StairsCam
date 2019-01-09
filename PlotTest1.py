#!/usr/bin/env	python3
# -*- coding: <UTF-8> -*-


from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np


# matrix calculation


Mat = np.random.rand(50, 64)  # random matrix 2D
Mat = Mat*10



## reshape nicht notwendig
np.set_printoptions(precision=2)


## Create a GL View widget to display data
app = QtGui.QApplication([])


w = gl.GLViewWidget()
w.show()
w.setWindowTitle('pyqtgraph example: GLSurfacePlot')
w.setCameraPosition(distance=40)

## Add a grid to the view
g = gl.GLGridItem()

# grid scale
g.scale(1, 1, 1)

g.setDepthValue(1)  # draw grid after surfaces since they may be translucent

w.addItem(g)



x = Mat[:, :1]  # 0-63 Mat[:1, :].shape = (1, 64)
y = Mat[:1, :]  # 0-49
z = Mat



p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)
#p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)

# whats this?
#p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])

# translate coordinates starting point (x,y,z)
# optimum (-5,-5,0)
p4.translate(-5, -5, 0)
w.addItem(p4)



def update():
	global p4, z, index

	p4.setData(z=z)


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1000)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
