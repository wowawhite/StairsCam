#!/usr/bin/python3
# -*- coding: <UTF-8> -*-
# This is client.py file# import socket
 # TODO check shape of np array. obviously its diffrent
 # TODO scale Z data. now incoming floats about 1.000.000.000
 # maybe cast to int for speed?


import numpy as np
import socket
import binascii
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import sys

from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QLabel
from PyQt5.QtCore import QTimer


class Window(QMainWindow):
	def __init__(self):
		super().__init__()

		self.initUI()

	def initUI(self):

		#self.statusbar = self.statusBar()
		#self.statusbar.showMessage('Ready')

		#lbl1 = QLabel('IFM O3D201 Interface', self)
		#lbl1.move(15, 10)

		#self.setGeometry(300, 300, 250, 150)
		#self.setWindowTitle('Absolute')



		# opengl defs here

		# gui part starting here

		## Create a GL View widget to display data

		self.w = gl.GLViewWidget()
		self.w.show()
		self.w.setWindowTitle('pyqtgraph example: GLSurfacePlot')
		self.w.setCameraPosition(distance=200)

		## Add a grid to the view
		self.g = gl.GLGridItem()

		# grid scale
		self.g.scale(10, 10, 10)

		self.g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
		#self.g.size(700,400 )
		self.w.addItem(self.g)

		self.y = np.arange(50)
		self.x = np.arange(64)

		self.p4 = gl.GLSurfacePlotItem(x=self.x, y=self.y, shader='heightColor', computeNormals=False, smooth=False)
		# p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)

		# whats this?
		# p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
		self.p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])

		# translate coordinates starting point (x,y,z)
		# optimum (-5,-5,0)
		self.p4.translate(-5, -5, 0)
		self.w.addItem(self.p4)

		# old show here
		self.show()

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(1000)



	def read_camera(self):
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
		clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 13176)  # chang rcv buf size
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


		useful_matrix = (np.reshape(usefuldata[94:3294], (64, 50)))/100000000

		return useful_matrix

	def keyPressEvent(self, event):
		# Did the user press the Escape key?
		if event.key() == QtCore.Qt.Key_Escape:  # QtCore.Qt.Key_Escape is a value that equates to what the operating system passes to python from the keyboard when the escape key is pressed.
			self.close()
			print("User Escape key exit")
			QtCore.QCoreApplication.quit()

	def update(self):

		self.z = self.read_camera()

		self.p4, self.z

		self.p4.setData(z=self.z)








if __name__ == '__main__':
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		app = QApplication(sys.argv)
		ex = Window()
		sys.exit(app.exec_())
