#!/usr/bin/env	python3
# -*- coding: <UTF-8> -*-


from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import socket
import binascii
import matplotlib.pyplot as plt


# check out IP of camera
cameraIP = "192.0.0.69"
controlport = 8080
videoport = 50002
# protocol parameter
package_length = 13176  # in bytes
header_length = 94
data_length = 3200
server_address = (cameraIP, videoport)
# protocol commands
letter_D = binascii.a2b_qp('D')  # seems to be the same as
letter_Z = 'Z'.encode('ascii')  # cartesian z distance
letter_q = 'q'.encode('ascii')  # stop socket connection
# numpy parameter


# socket configuration
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.setblocking(True)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 20000)  # chang rcv buf size
clientSocket.settimeout(1.5)
# clientSocket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # good idea?


# matrix calculation

# global coordinates x=50, y=64

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

x = np.arange(64)
y = np.arange(50)

colors = np.ones((64, 50, 4), dtype=float)

colors[:,:,0] = 0
colors[:,:,1] = 1
colors[:,:,2] = 3
colors[:,:,3] = 5

# shader: shaded, heightColor

p4 = gl.GLSurfacePlotItem(x=x, y = y, shader = 'shaded',
                            colors = colors.reshape(64*50,4),computeNormals=True, smooth=True)
# , colors=rgba_img

#p4 = gl.GLSurfacePlotItem(x=x, y = y, shader='heightColor', computeNormals=False, smooth=False)

#p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)
#p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)

# whats this?
#p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
#p4.shader()['colorMap'] = np.array([2, 20, 5, 2, 10, 10, 2, 0, 20])

# translate coordinates starting point (x,y,z)
# optimum (-5,-5,0)
p4.translate(-25, -25, 0)
w.addItem(p4)


def update():
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientSocket.setblocking(True)
	#clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 20000)  # chang rcv buf size
	clientSocket.settimeout(1.5)
	try:
		clientSocket.connect(server_address)
	except socket.error as sockerr:
		print("Socket error: %s" % str(sockerr))
	except Exception as e:
		print("Other exception: %s" % str(e))

	#print("Sending data request D")
	clientSocket.sendall(letter_D)

	# receiving process. tricking recv into loop
	#print("Waiting for response")
	dt = np.dtype('>f4')

	bytedata = b''
	amount_received = 0
	try:

		while amount_received < package_length:
			# error => msg_bin is overwritten everytime I call recv
			chunk_bin = clientSocket.recv(package_length)
			bytedata += chunk_bin
			amount_received += len(chunk_bin)

	except socket.timeout:
		print("Timeout Exception")
	except socket.error as sockerr:
		print("Socket error: %s" % str(sockerr))

	if socket:
		#print("Closing connection")
		clientSocket.sendall(letter_q)
		clientSocket.close()

	usefuldata = np.fromstring(bytedata, dt)
	#print(usefuldata.shape)
	cutheader = usefuldata[94:3295]*3
	#print(cutheader.shape)
	useful_matrix = np.reshape(cutheader, (50, 64))
	reshapedmatrix = np.transpose(useful_matrix)

	global p4

	p4.setData(z=reshapedmatrix)


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1000)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
