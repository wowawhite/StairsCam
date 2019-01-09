#!/usr/bin/python3
# -*- coding: <UTF-8> -*-
# This is client.py file# import socket
#TODO serialize binary to float data
#TODO plot data
#TODO read camera every sec
#TODO write as class
#

import numpy as np
import socket

def read_camera():
	#check out IP of camera
	cameraIP = "192.168.178.69"
	controlport = 8080
	videoport = 50002
	# protocol parameter
	package_length = 13176 # in bytes

	header_length = 376
	data_length = 12800
	# protocol commands
	letter_D = 'D'.encode('ascii')  # radial distance
	letter_Z = 'Z'.encode('ascii')  # cartesian z distance
	letter_q = 'q'.encode('ascii')  # stop socket connection
	# numpy parameter
	dt = np.dtype('b')  # byte, native byte order
	#data_bytes = np.array(package_length, dt)

	"""
	https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.dtypes.html
	dt = np.dtype('b')  # byte, native byte order
	dt = np.dtype('>H') # big-endian Funsigned short
	dt = np.dtype('<f') # little-endian single-precision float
	dt = np.dtype('d')  # double-precision floating-point number
	"""

	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#clientSocket.setblocking(1)
	# put exception handling for no connection here
	clientSocket.settimeout(1.2)
	clientSocket.connect((cameraIP, videoport))

	# connection timeout how much needed?

	print("Sending data request")
	clientSocket.sendall(letter_Z)

	print("Waiting for response")
	try:

		msg_bin = clientSocket.recv(package_length)
		#msg = msg_bin.decode(encoding='ascii')
		# wholedata = np.fromstring(, 'b')
		# The return value is a string representing the data received.
	except socket.timeout:
		print("Timeout Exception")

	clientSocket.sendall(letter_q)
	#clientSocket.shutdown()
	clientSocket.close()

	print("Data received/n")
	print(len(msg_bin))
	print(type(msg_bin))




	"""
	dummyWrite = (byte"nope")
	with open("C:/Users/Wowa/Documents/MEGA/Software/Pycharm/PythonLearning/check.txt", 'wb') as f:
		f.write(dummyWrite)
		print("Wrote data to file")
	f.close()
	"""
if __name__ == '__main__':
	read_camera()
