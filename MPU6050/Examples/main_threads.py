from __future__ import print_function
import time
import math
import mpu6050
import hmc5883l
import bmp085
import thread
from gpsdData import *

global stop 

def fileOpen(fileToWrite,bufferring = 100):
    if fileToWrite!=None:
	try:
	    file1 = open(fileToWrite,'w',bufferring)
	except:
            print('file open failed')
            return None
	else:
	    return file1
    return None

def writeThread(file1,num):
    global stop 
    try:
	    if num == 1:
		global mpuDatas
		while stop==False:
			lens = len(mpuDatas)
			print ('mpuDatas len is ',lens)
			if lens !=0:
			     for i in range(0,lens-1):
				data = mpuDatas.pop(0)
				print(data['q']['w'],
				      data['q']['x'],
				      data['q']['y'],
				      data['q']['z'],
				      data['ypr']['yaw'] * 180 / math.pi,
				      data['ypr']['pitch'] * 180 / math.pi,
				      data['ypr']['roll'] * 180 / math.pi,
				      data['time'],
				      file = file1)
			time.sleep(1)
	    elif num == 2:
		global magDatas
		while stop==False:
			lens = len(magDatas)
			print ('magDatas len is ',lens)
			if lens !=0:
			     for i in range(0,lens-1):
				data = magDatas.pop(0)
				print(
				      data['x'],
				      data['y'],
				      data['z'],
				      data['time'],
				      file = file1)
			time.sleep(1)
	    elif num == 3:
		global bmpDatas
		while stop==False:
			lens = len(bmpDatas)
			print ('bmpDatas len is ',lens)
			if lens !=0:
			     for i in range(0,lens-1):
				data = bmpDatas.pop(0)
				print(
				      data['temp'],
				      data['pre'],
				      data['alt'],
				      data['time'],
				      file = file1)
			time.sleep(1)
	    elif num == 4:
		global gpsDatas
		while stop==False:
			lens = len(gpsDatas)
			print ('gpsDatas len is ',lens)
			if lens !=0:
			     for i in range(0,lens-1):
				data = gpsDatas.pop(0)
				print(
				      data['lat'],
				      data['lon'],
				      data['alt'],
				      data['timeUtc'],
				      data['time'],
				      file = file1)
			time.sleep(1)
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            stop  =  True
            print('stop')

def mpu6050Thread(fileToWrite=None):
    # Sensors initialization global mpuData
    global mpuDatas
    global stop 
    mpuDatas = list()
    if fileToWrite != None:
        file1  = fileOpen(fileToWrite)
    mpu = mpu6050.MPU6050()
    mpu.setDMPEnabled(True)
    mpu.resetFIFO()
    packetSize = mpu.dmpGetFIFOPacketSize()
    if file1 != None:
        thread.start_new_thread(writeThread,(file1,1))

    try:
	    while stop==False:
		# Get INT_STATUS byte
		mpuIntStatus = mpu.getIntStatus()
		if mpuIntStatus >= 2: # check for DMP data ready interrupt (this should happen frequently) 
		    # get current FIFO count
		    fifoCount = mpu.getFIFOCount()
		    
		    # check for overflow (this should never happen unless our code is too inefficient)
		    if fifoCount == 1024:
			# reset so we can continue cleanly
			mpu.resetFIFO()
			print('FIFO overflow!')
			
		    # wait for correct available data length, should be a VERY short wait
		    fifoCount = mpu.getFIFOCount()
		    while fifoCount < packetSize:
			fifoCount = mpu.getFIFOCount()

		    result = mpu.getFIFOBytes(packetSize)
		    q = mpu.dmpGetQuaternion(result)
		    g = mpu.dmpGetGravity(q)
		    ypr = mpu.dmpGetYawPitchRoll(q, g)
		    mpuData={'q':q,
			   'ypr':ypr,
			  'time':float(time.time())
				}
		    if file1 != None:
			mpuDatas.append(mpuData)
		    # track FIFO count here in case there is > 1 packet available
		    # (this lets us immediately read more without waiting for an interrupt)        
		    fifoCount -= packetSize 
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            stop  =  True
            print('stop')
def hm5883lThread(fileToWrite=None):
    global magData
    global magDatas
    global stop 
    magDatas = list()
    file1  = fileOpen(fileToWrite)
    if file1 != None:
        thread.start_new_thread(writeThread,(file1,2))
    # HM5883l
    mag = hmc5883l.HMC5883L()
    try:
	    while stop==False:
		magData = mag.getHeading() 
		magData['time']= float(time.time())
		if file1 != None:
			magDatas.append(magData)
		time.sleep(0.02)
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            stop  =  True
            print('stop')

def bmpThread(fileToWrite=None):
    global bmpData
    global bmpDatas
    global stop 
    bmpDatas = list()
    file1  = fileOpen(fileToWrite)
    if file1 != None:
        thread.start_new_thread(writeThread,(file1,3))
    # BMP085
    bmp = bmp085.BMP085()
    # needless of initialization
    try:
	    while stop==False:
		bmpData = bmp.readData()
		bmpData['time']= float(time.time())
		if file1 != None:
			bmpDatas.append(bmpData)
		time.sleep(0.2)
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            stop  =  True
            print('stop')
def gpsThread(fileToWrite=None):
    global gpsData
    global gpsDatas
    global gpsp
    global stop 
    gpsDatas = list()
    file1  = fileOpen(fileToWrite)
    if file1 != None:
        thread.start_new_thread(writeThread,(file1,4))
    # GPs read Data
    try:
        while stop==False:
	    if(len(gpsp.gpsd.utc)!=0):
	        gpsData = dict()
    	        gpsData['lat']  =  gpsp.gpsd.fix.latitude
	        gpsData['lon'] =  gpsp.gpsd.fix.longitude
	        gpsData['timeUtc']   =  gpsp.gpsd.utc
                gpsData['alt']  =  gpsp.gpsd.fix.altitude
                gpsData['time']= float(time.time())
	        if file1 != None:
	            gpsDatas.append(gpsData)
	    if(stop==True):
		print('stop')
            time.sleep(0.2)
    except (KeyboardInterrupt, SystemExit):
	    stop = True;
            print('stop')
def main():
    run = True
    global mpuData
    global magData
    global bmpData
    global gpsData
    global gpsp
    global stop
    fileMpu = "/mnt/sd/mpu.dat"
    fileMag = "/mnt/sd/mag.dat"
    fileBmp = "/mnt/sd/bmp.dat"
    fileGps = "/mnt/sd/gps.dat"
    try:
	stop = False
    	mpu = mpu6050.MPU6050()
	mpu.dmpInitialize()
    	mag = hmc5883l.HMC5883L()
    	mag.initialize()
	gpsp=GpsPoller()
	gpsp.start()
    except:
	print('Error with MPU initialization')
    try:
        thread.start_new_thread(mpu6050Thread,(fileMpu,))
        thread.start_new_thread(hm5883lThread,(fileMag,))
        thread.start_new_thread(bmpThread,(fileBmp,))
        thread.start_new_thread(gpsThread,(fileGps,))
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print ("\nKilling Thread...")
        gpsp.running = False
        gpsp.join() # wait for the thread to finish what it's doin
    except:
        print("Error with threading")
        run = False
    try:
            time.sleep(4)
	    while stop==False:
		#print mpuData,
		#print magData,
		#print bmpData
		if(stop==True):
			print('stop')
		time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
	    stop = True;
            print('stop')
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doin


if __name__ == '__main__':
    main()
