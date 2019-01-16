#!/usr/bin/python3
# -*- coding: <UTF-8> -*-
# This is client.py file# import socket


import numpy as np
import socket
import binascii
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import sys




class Widget(QT)


def read_camera():
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
	letter_q = 'q'.encode('ascii')  # stop socket connection


	# socket configuration
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientSocket.setblocking(False)
	# clientSocket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
	clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 20000)  # chang rcv buf size
	# clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # good idea?
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
	dt = ('>i4')
	np.set_printoptions(precision=0)
	usefuldata = np.empty(3294, dtype=dt)
	amount_received = 0
	try:

		while amount_received < package_length:
			# error => msg_bin is overwritten everytime I call recv
			chunk_bin = clientSocket.recv_into(usefuldata, int(package_length))
			amount_received += chunk_bin
			print(amount_received)

		print("Data received. %s bytes" % amount_received)
	except socket.timeout:
		print("Timeout Exception")
	except socket.error as sockerr:
		print("Socket error: %s" % str(sockerr))

	if socket:
		print("Closing connection")
		clientSocket.sendall(letter_q)
		clientSocket.close()

	useful_matrix = np.reshape(usefuldata[94:3294], (64, 50))

	return useful_matrix


	# gui part starting here


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

	x = useful_matrix[:, :1]  # 0-63 Mat[:1, :].shape = (1, 64)
	y = useful_matrix[:1, :]  # 0-49
	z = useful_matrix

	p4 = gl.GLSurfacePlotItem(x=x[:, 0], y=y[0, :], shader='heightColor', computeNormals=False, smooth=False)
	# p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)

	# whats this?
	# p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
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




if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
