#!/usr/bin/env	python3
# -*- coding: <UTF-8> -*-


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
#clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 20000)  # chang rcv buf size
clientSocket.settimeout(1.5)
# clientSocket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)


## reshape nicht notwendig
np.set_printoptions(precision=2)


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
#bytedata = np.empty(13176, dtype=dt)
amount_received = 0
#toread = 13176
toread = 4
bytedata = b''
try:
	"""

	while amount_received < package_length:
		# error => msg_bin is overwritten everytime I call recv
		chunk_bin = clientSocket.recv_into(usefuldata, int(package_length))
		amount_received += chunk_bin

	

	while toread:
		# error => msg_bin is overwritten everytime I call recv
		nbytes = clientSocket.recv_into(bytedata, 4)
		#view = view[nbytes:]
		toread -= nbytes
"""
	while amount_received < package_length:
		# error => msg_bin is overwritten everytime I call recv
		chunk_bin = clientSocket.recv(package_length)
		bytedata += chunk_bin
		amount_received += len(chunk_bin)


	print("Data received. %s bytes" % amount_received)
	print(len(bytedata))


except socket.timeout:
	print("Timeout Exception")
except socket.error as sockerr:
	print("Socket error: %s" % str(sockerr))

if socket:
	print("Closing connection")
	clientSocket.sendall(letter_q)
	clientSocket.close()

usefuldata = np.fromstring(bytedata, dt)
print(usefuldata.shape)
cutheader = usefuldata[94:3295]
print(cutheader.shape)
useful_matrix = np.reshape(cutheader, (50, 64))
np.savetxt('text.txt', useful_matrix, fmt='%.0f')






