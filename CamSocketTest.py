#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

def Main():
	#check out IP of camera
	cameraIP = "192.F168.178.69"
	controlport = 8080
	videoport = 50002

	package_length = 13176
	header_length = 376
	data_length = 12800
	letter_D = 'D'.encode('ascii')
	letter_q = 'q'.encode('ascii')

	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientSocket.setblocking(True)
	clientSocket.connect((cameraIP, videoport))
	clientSocket.settimeout(60000)
	#mySocket.listen(13176)  # connection timeout 5 times try

	print("Sending data request D")
	clientSocket.sendall(letter_D)
	print("Waiting for response")
	data = clientSocket.recv(package_length)
	#if data.:

	print("Data received/n")
	#while i <= len(data):

	#print ("Data received/n")
	clientSocket.sendall(letter_q)

	#clientSocket.shutdown()
	clientSocket.close()

	with open("check.txt", 'wb') as f:
		f.write(data)
		print("Wrote data to file")
	f.close()

if __name__ == '__main__':
	Main()