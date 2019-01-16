#!/usr/bin/env python
# -*- coding: utf-8 -*-

############### file info ######################################################
# written by Waldemar Kulajev
# used pwm pins red: P9_22, green: P8_13, blue: P8_19
# motor control pin 8.12, led control pin p8.14
# pwm frequency 19000
# red=positive
# green=neutral
# blue=negative
################################################################################

import sys
import os
import tweepy
import jsonpickle
import numpy as np
import pyqtgraph as pg
from collections import deque
from datetime import datetime
from PyQt4 import QtGui, QtCore, QtTest, QtNetwork
from PyQt4.QtCore import QTimer, QCoreApplication, QUrl
import time
import datetime

if __debug__:
	pass
else:
	import Adafruit_BBIO.PWM as PWM  # works only on bbb!
	import Adafruit_BBIO.GPIO as GPIO  # works only on bbb!
try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	_fromUtf8 = lambda s: s


class MainWindow(QtGui.QMainWindow):

	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		if __debug__:
			homePath = "C:\\Users\\Wowa\\Documents\\MEGA\\Software\\PythonTesting\\Assembly_GUI3\\"
		else:
			homePath = "//home//debian//Software//"
		styleSheetFile = homePath + "dark.stylesheet"
		with open(styleSheetFile, "r") as fh:
			qstr = QtCore.QString(fh.read())
			self.setStyleSheet(qstr)

		fh.close()
		self._mainWidget = MainWidget(self)
		self._layout = QtGui.QVBoxLayout()
		self._layout.addWidget(self._mainWidget)
		self.setCentralWidget(self._mainWidget)

		# draw gui,check connection, stat ports
		self._mainWidget.initUI()
		self._mainWidget.checkConnection()
		self._mainWidget.pwmStartport()


# x-axis modification
class TimeAxisItem(pg.AxisItem):
	# balast?
	UNIX_EPOCH_naive = datetime.datetime(1970, 1, 1, 0, 0)  # offset-naive datetime
	# UNIX_EPOCH_offset_aware = datetime.datetime(1970, 1, 1, 0, 0, tzinfo = utc) #offset-aware datetime
	UNIX_EPOCH = UNIX_EPOCH_naive
	TS_MULT_us = 1000000

	def __init__(self, *args, **kwargs):
		super(TimeAxisItem, self).__init__(*args, **kwargs)

	def now_timestamp(ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
		return (int((datetime.datetime.utcnow() - epoch).total_seconds() * ts_mult))

	def int2dt(ts, ts_mult=TS_MULT_us):
		return (datetime.datetime.utcfromtimestamp(float(ts) / ts_mult))

	def tickStrings(self, values, scale, spacing):
		return [["+5min"] for value in values]
	# put timeline debug here
	# return [time.strftime("%d.%m.%y \n %H:%M:%S", time.localtime(value)) for value in values]


class MainWidget(QtGui.QTabWidget):
	def __init__(self, parent=None):
		super(MainWidget, self).__init__(parent)
		self.manuellFlag = False
		self.offlineFlag = True
		self.PWM_const = 19500
		if __debug__:
			self.homePath = "C:\\Users\\Wowa\\Documents\\MEGA\\Software\\PythonTesting\\Assembly_GUI3\\"
		else:
			self.homePath = "//home//debian//Software//"
		self.setFocusPolicy(QtCore.Qt.NoFocus)

	def initUI(self):
		# gui defs

		self.pbar = QtGui.QProgressBar(self)
		self.pbar.setAlignment(QtCore.Qt.AlignCenter)
		self.pbar.setRange(1, 100)
		self.pbar.setFormat('Durchsuche Twitter...')
		self.pbar.setGeometry(230, 200, 250, 50)
		self.pbar.hide()

		self.pbar.setAlignment(QtCore.Qt.AlignCenter)
		self.tab1 = QtGui.QWidget()
		self.tab1.setFocusPolicy(QtCore.Qt.NoFocus)
		self.tab2 = QtGui.QWidget()
		self.tab2.setFocusPolicy(QtCore.Qt.NoFocus)
		self.tab3 = QtGui.QWidget()
		self.tab3.setFocusPolicy(QtCore.Qt.NoFocus)
		self.addTab(self.tab1, "Automatik")
		self.addTab(self.tab2, "Manuell")
		self.addTab(self.tab3, "Programm-Info")
		self.autoTab()
		self.manualTab()
		self.infoTab()

		self.setWindowTitle("Hedonometer GUI")

		# twitter variable defintitions
		# path definitions
		# tweetspath to "tweets.txt"
		self.tweetsPath = (self.homePath + 'tweets.txt')
		# dictionary path to "clearlist.pkl"
		self.dictPath = (self.homePath + 'clearlist.pkl')

		if __debug__:
			self.maxTweets = 300
			self.tweetsSteps = 100
		else:
			self.maxTweets = 500
			self.tweetsSteps = 100

		# critical section, global variables
		self.countRed = 0
		self.countGreen = 0
		self.countBlue = 0
		self.countMatch = 0
		self.countNomatch = 0

		# check internet connection every 30 sec
		self.wifiTimer = QTimer()
		self.wifiTimer.timeout.connect(self.checkConnection)
		self.wifiTimer.start(30000)

	# tab nr1
	def autoTab(self):

		# plot window def
		self.hlayout = QtGui.QHBoxLayout()
		self.data = deque(maxlen=10)
		self.data.append({'red': 0, 'green': 0, 'blue': 0})
		self.win = pg.GraphicsWindow(title="Hedonometer GUI")
		self.hlayout.addWidget(self.win)

		self.plot = self.win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
		self.plot.setMouseEnabled(x=False, y=False)
		self.curve = self.plot.plot()
		self.plot.setLabel('left', "<b>%")

		self.plot.setClipToView(True)
		self.plot.showGrid(x=True, y=False)
		self.win.setAntialiasing(True)
		self.plot.addLegend()
		self.curve1 = self.plot.plot(pen='r', name='Positive Ausdrucke')
		self.curve2 = self.plot.plot(pen='g', name='Neutrale Ausdrucke')
		self.curve3 = self.plot.plot(pen='b', name='Negative Ausdrucke')

		self.setTabText(0, "Automatik")
		self.tab1.setLayout(self.hlayout)

		# timer updating plot, twitter data and pwm output every 5min
		self.tmr = QTimer()
		self.tmr.timeout.connect(self.updatePlot)
		if __debug__:
			self.tmr.start(30000)  # debug:update every 30sec
		else:
			self.tmr.start(300000)  # update every 300sec

	# tab nr2
	def manualTab(self):
		# gui objects
		self.vboxRed = QtGui.QVBoxLayout()
		self.vboxGreen = QtGui.QVBoxLayout()
		self.vboxBlue = QtGui.QVBoxLayout()
		self.vboxMcontrol = QtGui.QVBoxLayout()
		self.hboxManuell = QtGui.QHBoxLayout()
		# wifi label
		self.wifiIndicator = QtGui.QLabel()
		self.wifiIndicator.setPixmap(
			QtGui.QPixmap(self.homePath + "wifi_off.png").scaled(100, 100, QtCore.Qt.KeepAspectRatio,
																 QtCore.Qt.SmoothTransformation))
		self.wifiIndicator.setAlignment(QtCore.Qt.AlignCenter)
		# frames
		self.redGroupbox = QtGui.QGroupBox("Rot")
		self.redGroupboxLayout = QtGui.QVBoxLayout()
		self.redGroupbox.setAlignment(QtCore.Qt.AlignCenter)
		self.redGroupbox.setStyleSheet("font-size: 12pt;")
		self.redGroupbox.setLayout(self.redGroupboxLayout)

		self.greenGroupbox = QtGui.QGroupBox('Gruen')
		self.greenGroupboxLayout = QtGui.QVBoxLayout()
		self.greenGroupbox.setAlignment(QtCore.Qt.AlignCenter)
		self.greenGroupbox.setStyleSheet("font-size: 12pt;")
		self.greenGroupbox.setLayout(self.greenGroupboxLayout)

		self.blueGroupbox = QtGui.QGroupBox('Blau')
		self.blueGroupboxLayout = QtGui.QVBoxLayout()
		self.blueGroupbox.setAlignment(QtCore.Qt.AlignCenter)
		self.blueGroupbox.setStyleSheet("font-size: 12pt;")
		self.blueGroupbox.setLayout(self.blueGroupboxLayout)

		self.controlGroupbox = QtGui.QGroupBox('Steuerung')
		self.controlGroupboxLayout = QtGui.QVBoxLayout()
		self.controlGroupbox.setAlignment(QtCore.Qt.AlignCenter)
		self.controlGroupbox.setStyleSheet("font-size: 12pt;")
		self.controlGroupbox.setLayout(self.controlGroupboxLayout)
		# digit displays
		self.redLcd = QtGui.QLCDNumber(self)
		self.redLcd.setFixedSize(100, 50)
		self.redLcd.display(50)

		self.greenLcd = QtGui.QLCDNumber(self)
		self.greenLcd.setFixedSize(100, 50)
		self.greenLcd.display(50)

		self.blueLcd = QtGui.QLCDNumber(self)
		self.blueLcd.setFixedSize(100, 50)
		self.blueLcd.display(50)
		# sliders
		# red
		self.redSld = QtGui.QSlider(QtCore.Qt.Vertical, self)
		self.redSld.setFocusPolicy(QtCore.Qt.NoFocus)
		self.redSld.setFixedSize(100, 240)
		self.redSld.setMinimum(1)
		self.redSld.setMaximum(100)
		self.redSld.setValue(50)
		self.redSld.setTickInterval(1)
		self.redSld.sliderReleased.connect(self.valuechangeSliderRed)
		# green
		self.greenSld = QtGui.QSlider(QtCore.Qt.Vertical, self)
		self.greenSld.setFocusPolicy(QtCore.Qt.NoFocus)
		self.greenSld.setFixedSize(100, 240)
		self.greenSld.setMinimum(1)
		self.greenSld.setMaximum(100)
		self.greenSld.setValue(50)
		self.greenSld.setTickInterval(1)
		self.greenSld.sliderReleased.connect(self.valuechangeSliderGreen)
		# blue
		self.blueSld = QtGui.QSlider(QtCore.Qt.Vertical, self)
		self.blueSld.setFocusPolicy(QtCore.Qt.NoFocus)
		self.blueSld.setFixedSize(100, 240)
		self.blueSld.setMinimum(1)
		self.blueSld.setMaximum(100)
		self.blueSld.setValue(50)
		self.blueSld.setTickInterval(1)
		self.blueSld.sliderReleased.connect(self.valuechangeSliderBlue)
		# buttons

		self.mcontrolButton = QtGui.QPushButton('Pumpen-Relais', self)
		self.mcontrolButton.setCheckable(True)
		self.mcontrolButton.toggle()
		self.mcontrolButton.setFocusPolicy(QtCore.Qt.NoFocus)

		self.LEDcontrolButton = QtGui.QPushButton('LED-Relais', self)
		self.LEDcontrolButton.setCheckable(True)
		self.LEDcontrolButton.setFocusPolicy(QtCore.Qt.NoFocus)

		self.manuellButton = QtGui.QPushButton('Pumpen Manuell', self)
		self.manuellButton.setCheckable(True)
		self.manuellButton.setFocusPolicy(QtCore.Qt.NoFocus)

		self.grabTwitterButton = QtGui.QPushButton('Twitter lesen', self)
		self.grabTwitterButton.setCheckable(False)
		self.grabTwitterButton.setFocusPolicy(QtCore.Qt.NoFocus)

		self.quitButton = QtGui.QPushButton('Maschine ausschalten', self)
		self.quitButton.setCheckable(False)
		self.quitButton.setFocusPolicy(QtCore.Qt.NoFocus)

		# layout and geometry

		self.redGroupboxLayout.addWidget(self.redLcd)
		self.redGroupboxLayout.addStretch()
		self.redGroupboxLayout.addWidget(self.redSld)
		self.redGroupboxLayout.addStretch()
		self.vboxRed.addWidget(self.redGroupbox)

		self.greenGroupboxLayout.addWidget(self.greenLcd)
		self.greenGroupboxLayout.addStretch()
		self.greenGroupboxLayout.addWidget(self.greenSld)
		self.greenGroupboxLayout.addStretch()
		self.vboxGreen.addWidget(self.greenGroupbox)

		self.blueGroupboxLayout.addWidget(self.blueLcd)
		self.blueGroupboxLayout.addStretch()
		self.blueGroupboxLayout.addWidget(self.blueSld)
		self.blueGroupboxLayout.addStretch()
		self.vboxBlue.addWidget(self.blueGroupbox)

		self.controlGroupboxLayout.addWidget(self.mcontrolButton)
		self.controlGroupboxLayout.addStretch()
		self.controlGroupboxLayout.addWidget(self.LEDcontrolButton)
		self.controlGroupboxLayout.addStretch()
		self.controlGroupboxLayout.addWidget(self.manuellButton)
		self.controlGroupboxLayout.addStretch()
		self.controlGroupboxLayout.addWidget(self.grabTwitterButton)
		self.controlGroupboxLayout.addStretch()
		self.controlGroupboxLayout.addWidget(self.wifiIndicator)
		self.controlGroupboxLayout.addStretch()
		self.vboxMcontrol.addWidget(self.controlGroupbox)
		self.controlGroupboxLayout.addStretch()
		self.vboxMcontrol.addWidget(self.quitButton)
		# hbox
		self.hboxManuell.addLayout(self.vboxRed)
		self.hboxManuell.addStretch()
		self.hboxManuell.addLayout(self.vboxGreen)
		self.hboxManuell.addStretch()
		self.hboxManuell.addLayout(self.vboxBlue)
		self.hboxManuell.addStretch()
		self.hboxManuell.addLayout(self.vboxMcontrol)
		self.hboxManuell.addStretch()
		# signals and slots
		self.redSld.valueChanged.connect(self.redLcd.display)
		self.greenSld.valueChanged.connect(self.greenLcd.display)
		self.blueSld.valueChanged.connect(self.blueLcd.display)

		self.mcontrolButton.clicked[bool].connect(self.motorRelaisControl)
		self.LEDcontrolButton.clicked[bool].connect(self.LEDRelaisControl)
		self.manuellButton.clicked[bool].connect(self.manuellControl)
		self.grabTwitterButton.clicked.connect(self.updatePlot)
		self.quitButton.clicked.connect(self.quitProgram)
		# tab
		self.setTabText(1, "Manuell")
		self.tab2.setLayout(self.hboxManuell)

	# tab nr3
	def infoTab(self):
		# labels
		vboxInfo = QtGui.QVBoxLayout()
		infoText = QtGui.QPlainTextEdit()
		infoText.setBackgroundVisible(False)
		infoText.setReadOnly(True)
		infoText.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
		infoText.setDocumentTitle("Projekt Hedonometer")
		infoText.setPlainText(open(self.homePath + "programminfo.txt").read())
		vboxInfo.addWidget(infoText)
		vboxInfo.setAlignment(QtCore.Qt.AlignCenter)
		infoText.setStyleSheet("border: 2px solid black;"
							   "border-radius: 4px;"
							   "padding: 2px;"
							   "font-size: 12pt;")
		self.setTabText(2, "Info")
		self.tab3.setLayout(vboxInfo)

	# function definitions

	def center(self):
		qr = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def quitProgram(self):
		QtCore.QCoreApplication.quit()
		QtTest.QTest.qWait(3000)
		os.system("/sbin/shutdown -P now")

	def motorRelaisControl(self, pressed):
		if __debug__:
			pass
		else:
			if pressed:
				GPIO.output("P8_12", GPIO.HIGH)  # HIGH/LOW or 1/0
			# print "high"
			else:
				GPIO.output("P8_12", GPIO.LOW)  # HIGH/LOW or 1/0
			# print "low"

	def manuellControl(self, pressed):
		if pressed:
			self.manuellFlag = True
		else:
			self.manuellFlag = False

	def LEDRelaisControl(self, pressed):
		if __debug__:
			pass
		else:
			if pressed:
				GPIO.output("P8_14", GPIO.HIGH)  # HIGH/LOW or 1/0
			else:
				GPIO.output("P8_14", GPIO.LOW)  # HIGH/LOW or 1/0

	def checkConnection(self):
		# check if connection to 8.8.8.8:53 is available
		"""
		Host: 8.8.8.8 (google-public-dns-a.google.com)
		OpenPort: 53/tcp
		Service: domain (DNS/TCP)
		"""
		url = "http://www.google.com"
		req = QtNetwork.QNetworkRequest(QUrl(url))

		self.nam = QtNetwork.QNetworkAccessManager()
		self.nam.finished.connect(self.connectionResponse)
		self.nam.get(req)

	def connectionResponse(self, reply):
		# response to internet connection check
		er = reply.error()

		if er == QtNetwork.QNetworkReply.NoError:
			self.wifiIndicator.setPixmap(
				QtGui.QPixmap(self.homePath + "wifi_on.png").scaled(100, 100, QtCore.Qt.KeepAspectRatio,
																	QtCore.Qt.SmoothTransformation))
			self.offlineFlag = False
		else:
			self.wifiIndicator.setPixmap(
				QtGui.QPixmap(self.homePath + "wifi_off.png").scaled(100, 100, QtCore.Qt.KeepAspectRatio,
																	 QtCore.Qt.SmoothTransformation))
			self.offlineFlag = True
			self.pbar.hide()

	def pwmStartport(self):
		if __debug__: print
		"pwm port started"
		else:
		PWM.start("P9_22", 30, self.PWM_const, 1)
		QtTest.QTest.qWait(3000)
		PWM.start("P8_13", 30, self.PWM_const, 1)
		QtTest.QTest.qWait(3000)
		PWM.start("P8_19", 30, self.PWM_const, 1)
		QtTest.QTest.qWait(3000)
		GPIO.setup("P8_12", GPIO.OUT)
		QtTest.QTest.qWait(3000)
		GPIO.setup("P8_14", GPIO.OUT)
		QtTest.QTest.qWait(3000)
		GPIO.output("P8_12", GPIO.HIGH)  # HIGH/LOW or 1/0
		QtTest.QTest.qWait(3000)
		GPIO.output("P8_14", GPIO.LOW)  # HIGH/LOW or 1/0


def pwmStopport(self):
	if __debug__: print
	"pwm port stop"
	else:
	PWM.stop("P9_22")
	QtTest.QTest.qWait(3000)
	PWM.stop("P8_13")
	QtTest.QTest.qWait(3000)
	PWM.stop("P8_19")
	QtTest.QTest.qWait(3000)
	PWM.cleanup()
	QtTest.QTest.qWait(3000)


def valuechangeSliderRed(self):
	duty = self.redSld.value()
	if (self.manuellFlag == True):
		_out = int(0.7 * duty + 30)
		if __debug__: print
		"P9_22", _out
		else:
		PWM.set_duty_cycle("P9_22", _out)

else: pass


def valuechangeSliderGreen(self):
	duty = self.greenSld.value()
	if (self.manuellFlag == True):
		_out = int(0.7 * duty + 30)
		if __debug__: print
		"P8_13", _out
		else:
		PWM.set_duty_cycle("P8_13", _out)

else: pass


def valuechangeSliderBlue(self):
	duty = self.blueSld.value()
	if (self.manuellFlag == True):
		_out = int(0.7 * duty + 30)
		if __debug__: print
		"P8_19", _out
		else:
		PWM.set_duty_cycle("P8_19", _out)

else: pass


def writePWMport(self, red, green, blue):
	if (self.manuellFlag == False):
		if __debug__:
			_outR = int(red * 0.7 + 30)
			_outG = int(green * 0.7 + 30)
			_outB = int(blue * 0.7 + 30)
			print("P9_22", _outR, "P8_13", _outG, "P8_19", _outB)
		else:
			_outR = int(red * 0.7 + 30)
			PWM.set_duty_cycle("P9_22", _outR)
			QtTest.QTest.qWait(1500)
			_outG = int(green * 0.7 + 30)
			PWM.set_duty_cycle("P8_13", _outG)
			QtTest.QTest.qWait(1500)
			_outB = int(blue * 0.7 + 30)
			PWM.set_duty_cycle("P8_19", _outB)
	else:
		pass


def updatePlot(self):
	if self.manuellFlag == False:  # fehler
		if self.offlineFlag == True:
			self.pbar.hide()
			self.grabTwitterButton.setDisabled(True)
		else:
			# QtCore.QTimer.singleShot(40000, lambda: self.grabTwitterButton.setDisabled(True))
			self.grabTwitterButton.setDisabled(True)
			self.pbar.setValue(1)
			self.pbar.show()

			self.grabTwitterData()
			self.compareTwitterData()
			self.data.append({'red': self.countRed, 'green': self.countGreen, 'blue': self.countBlue})

			red = [item['red'] for item in self.data]
			green = [item['green'] for item in self.data]
			blue = [item['blue'] for item in self.data]

			self.curve1.setData(y=red)
			self.curve2.setData(y=green)
			self.curve3.setData(y=blue)
			self.pbar.hide()
			self.tmr.start(300000)
			self.grabTwitterButton.setDisabled(False)
			if __debug__:
				self.tmr.start(30000)  # debug:update every 30sec
			else:
				self.tmr.start(300000)
	else:
		self.tmr.stop()


def keyPressEvent(self, event):
	# Did the user press the Escape key?
	if event.key() == QtCore.Qt.Key_Escape:  # QtCore.Qt.Key_Escape is a value that equates to what the operating system passes to python from the keyboard when the escape key is pressed.
		self.close()
		self.pwmStopport()
		print
		"User Escape key exit"
		QtCore.QCoreApplication.quit()


# test foo for global exception control.
# Idee: Input:fehlercode, output:exception
def exceptionControl(self, inputErr):
	pass


def grabTwitterData(self):
	API_KEY = "GbqSuFsshZOEBm2sckzOPUkaX"
	API_SECRET = "SaUPOfw0eMUMhwRbekKsKyQxg7rO3eZ2Lh4g1Ul8UD3Zpc6eZo"
	# Replace the API_KEY and API_SECRET with your application's key and secret.
	auth = tweepy.AppAuthHandler(API_KEY, API_SECRET)
	# Exception bei fehlender internetverbindung!
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	if (not api):
		# stupid solution,but works
		raise tweepy.TweepError("API Connection Error")
		self.checkConnection()
	# raise tweepy.TweepError("Twitter API connection error")
	# sys.exit(0)
	# login procedure finished, grab data here
	searchQuery = '*'  # '*' for random tweets
	maxTweets = self.maxTweets  # Some arbitrary large number
	tweetsPerQry = self.tweetsSteps  # this is the max the API permits
	fName = self.tweetsPath
	language = 'en'

	# If results from a specific ID onwards are reqd, set since_id to that ID.
	# else default to no lower limit, go as far back as API allows
	sinceId = None

	# If results only below a specific ID are, set max_id to that ID.
	# else default to no upper limit, start from the most recent tweet matching the search query.
	maxId = -1L

	tweetCount = 0
	if __debug__:
		print("Downloading max {0} tweets".format(maxTweets))
	else:
		pass
	with open(fName, 'w') as f:
		while tweetCount < maxTweets:
			try:
				if (maxId <= 0):
					if (not sinceId):
						newTweets = api.search(q=searchQuery, lang=language, count=tweetsPerQry)
					else:
						newTweets = api.search(q=searchQuery, lang=language, count=tweetsPerQry, sinceId=sinceId)
				else:
					if (not sinceId):
						newTweets = api.search(q=searchQuery, lang=language, count=tweetsPerQry, maxId=str(maxId - 1))
					else:
						newTweets = api.search(q=searchQuery, lang=language, count=tweetsPerQry, maxId=str(maxId - 1),
											   sinceId=sinceId)
				if not newTweets:
					# raise Exception
					raise tweepy.TweepError("API intern error")
					self.checkConnection()
				for tweet in newTweets:
					f.write(jsonpickle.encode(tweet._json, unpicklable=False) +
							'\n')
				tweetCount += len(newTweets)
				barProgress = float(tweetCount) / maxTweets * 100
				# print barProgress
				self.pbar.setValue(barProgress)
				if __debug__:
					print("Downloaded {0} tweets".format(tweetCount))
				else:
					pass
				maxId = newTweets[-1].id

			except:
				raise tweepy.TweepError("Try-Block error")
				self.checkConnection()
				f.close()
	f.close()


def compareTwitterData(self):
	rot = set()
	gruen = set()
	blau = set()
	countRedL = 0
	countGreenL = 0
	countBlueL = 0
	countMatchL = 0
	countNomatchL = 0

	try:
		with open(self.dictPath, "r") as dictionary, open(self.tweetsPath, "r") as datafile:

			# einlesen der code liste
			for line in dictionary:
				words = line.strip("\n").split(":")
				if words[0] == "gruen":
					gruen.add(words[1])
				elif words[0] == "rot":
					rot.add(words[1])
				elif words[0] == "blau":
					blau.add(words[1])
			# einlesen und filtern der tweets liste
			for line in datafile:
				fliestext = line.strip("\n").split('"')
				ausdruck = fliestext[7].split(" ")  # list position 7 = fliesstext
				# bis hierhin filtern, dann vergleich der woerter

				if bool(rot.intersection(ausdruck)) == True:
					countRedL = countRedL + 1
					countMatchL = countMatchL + 1
				elif bool(gruen.intersection(ausdruck)) == True:
					countGreenL = countGreenL + 1
					countMatchL = countMatchL + 1
				elif bool(blau.intersection(ausdruck)) == True:
					countBlueL = countBlueL + 1
					countMatchL = countMatchL + 1
				else:
					countNomatchL = countNomatchL + 1

		dictionary.close()
		datafile.close()
	except IOError as err:
		# print "Folgender Fehler trat auf: "+err
		dictionary.close()
		datafile.close()

	self.countRed = float(countRedL) / countMatchL * 100
	self.countGreen = float(countGreenL) / countMatchL * 100
	self.countBlue = float(countBlueL) / countMatchL * 100
	self.writePWMport(self.countRed, self.countGreen, self.countBlue)


def main():
	app = QtGui.QApplication(sys.argv)
	win = MainWindow()

	############blank cursor#################
	# --warning. Think before enabling this--#
	if __debug__:
		pass
	else:
		win.showFullScreen()
		app.setOverrideCursor(QtCore.Qt.BlankCursor)
	########################################

	win.show()

	sys.exit(app.exec_())


if __name__ == '__main__':
	main()