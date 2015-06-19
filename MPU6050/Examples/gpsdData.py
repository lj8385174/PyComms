#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0

import os
from gps import *
from time import *
import time
import threading

class GpsPoller(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
		self.current_value = None
		self.running = True #setting the thread running to true

	def run(self):
		while self.running:
			self.gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

if __name__ == '__main__':
	os.system('clear') #clear the terminal (optional)
	gpsp = GpsPoller() # create the thread
	try:
		gpsp.start() # start it up
		while True:
			#It may take a second or two to get good data
			#print gpsd.fix.latitude,', ',gpsd.fix.longitude,'	Time: ',gpsd.utc

			os.system('clear')
			
			print 'len of time:' , len(gpsp.gpsd.utc)
			print
			print ' GPS reading'
			print '----------------------------------------'
			print 'latitude    ' , gpsp.gpsd.fix.latitude
			print 'longitude   ' , gpsp.gpsd.fix.longitude
			print 'time utc    ' , gpsp.gpsd.utc,' + ', gpsp.gpsd.fix.time
			print 'time utc+8    ' , gpsp.gpsd.utc
			print 'altitude (m)' , gpsp.gpsd.fix.altitude
			print 'eps         ' , gpsp.gpsd.fix.eps
			print 'epx         ' , gpsp.gpsd.fix.epx
			print 'epv         ' , gpsp.gpsd.fix.epv
			print 'ept         ' , gpsp.gpsd.fix.ept
			print 'speed (m/s) ' , gpsp.gpsd.fix.speed
			print 'climb       ' , gpsp.gpsd.fix.climb
			print 'track       ' , gpsp.gpsd.fix.track
			print 'mode        ' , gpsp.gpsd.fix.mode
			print
			print 'sats        ' , gpsp.gpsd.satellites

			time.sleep(0.1) #set to whatever

	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
		print "\nKilling Thread..."
		gpsp.running = False
		gpsp.join() # wait for the thread to finish what it's doing
	print "Done.\nExiting."
