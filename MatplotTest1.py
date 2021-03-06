
from numpy.random import uniform, seed
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import numpy as np
# make up data.

import numpy as np
import socket
import binascii


def Main():
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
	dt = np.dtype('b')  # byte, native byte order
	# data_bytes = np.array(package_length, dt)

	"""
	https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.dtypes.html
	dt = np.dtype('b')  # byte, native byte order
	dt = np.dtype('>H') # big-endian Funsigned short
	dt = np.dtype('<f') # little-endian single-precision float
	dt = np.dtype('d')  # double-precision floating-point number
	"""

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
	dt = np.float32
	usefuldata = np.empty(3294, dtype=dt)
	amount_received = 0
	try:

		while amount_received < package_length:
			# error => msg_bin is overwritten everytime I call recv
			chunk_bin = clientSocket.recv_into(usefuldata, int(package_length))
			amount_received += chunk_bin
			print(amount_received)

		print("Data received. %s bytes" % amount_received)
		print(len(usefuldata))
		print(type(usefuldata))
	except socket.timeout:
		print("Timeout Exception")
	except socket.error as sockerr:
		print("Socket error: %s" % str(sockerr))

	if socket:
		print("Closing connection")
		clientSocket.sendall(letter_q)
		clientSocket.close()

	cutmatrix = usefuldata[94:3294]
	print(cutmatrix[0:50])
	useful_matrix = (np.reshape(cutmatrix, (64, 50)))


	fig = plt.figure(figsize=(64, 50))

	ax = fig.add_subplot(111)
	ax.set_title('colorMap')
	plt.imshow(useful_matrix)
	ax.set_aspect('equal')
	plt.colorbar(orientation='vertical')
	plt.show()



	plt.matshow(useful_matrix)
	plt.grid()
	plt.show()


if __name__ == '__main__':
	Main()
















#npts = int(raw_input('enter # of random points to plot:'))
