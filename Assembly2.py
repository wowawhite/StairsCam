#!/usr/bin/env	python3
# -*- coding: <UTF-8> -*-


from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import socket
import binascii



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
#clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # good idea?

# only this part should be repeated



# matrix calculation

# global coordinates x=50, y=64
#Mat = np.random.rand(50, 64)  # random matrix 2D


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

x = np.arange(64)
y = np.arange(50)

p4 = gl.GLSurfacePlotItem(x=x, y = y, shader='heightColor', computeNormals=False, smooth=False)

#p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)
#p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)

# whats this?
#p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
p4.shader()['colorMap'] = np.array([2, 20, 5, 2, 10, 10, 2, 0, 20])

# translate coordinates starting point (x,y,z)
# optimum (-5,-5,0)
p4.translate(-25, -25, 0)
w.addItem(p4)

printflag = True


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

	print("Sending data request D")
	clientSocket.sendall(letter_D)

	# receiving process. tricking recv into loop
	print("Waiting for response")
	dt = np.dtype('>f4')

	buf = bytearray(package_length)
	view = memoryview(buf)
	#usefuldata = np.empty(3294, dtype=dt)
	amount_received = 0
	try:

		while amount_received < package_length:
			# error => msg_bin is overwritten everytime I call recv
			chunk = clientSocket.recv_into(view, package_length)
			#chunk_bin = clientSocket.recv_into(usefuldata, int(package_length))
			amount_received += chunk


		#print("Data received. %s bytes" % amount_received)
		#print(len(usefuldata))
		#print(type(usefuldata))
	except socket.timeout:
		print("Timeout Exception")
	except socket.error as sockerr:
		print("Socket error: %s" % str(sockerr))

	if socket:
		#print("Closing connection")
		clientSocket.sendall(letter_q)
		clientSocket.close()
	print(len(view))
	#usefuldata = np.fromstring(view, dt)
	usefuldata = np.asarray(view, dt)
	stage1 = usefuldata[94:3294]/10
	print(usefuldata.shape)
	useful_matrix = (np.reshape(stage1, (64, 50)))
	print(useful_matrix.shape)
	#print(useful_matrix[0:64, 0:0])
	#print(useful_matrix)
	global printflag
	if printflag == True:
		np.savetxt('text.txt', useful_matrix, fmt='%.0f')
		printflag=False
		print("Printed textfile")


	global p4

	p4.setData(z=useful_matrix)


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1000)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
