from __future__ import print_function
import time
import math
import mpu6050
import hmc5883l
import bmp085
import thread


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
    if num == 1:
	global mpuDatas
	while True:
		lens = len(mpuDatas)
		print ('mpuDatas lens is ',lens)
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
	while True:
		lens = len(magDatas)
		print ('magDatas lens is ',lens)
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
	while True:
		lens = len(bmpDatas)
		print ('bmpDatas lens is ',lens)
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

def mpu6050Thread(fileToWrite=None):
    # Sensors initialization
    global mpuData
    global mpuDatas
    mpuDatas = list()
    file1  = fileOpen(fileToWrite)
    mpu = mpu6050.MPU6050()
    mpu.setDMPEnabled(True)
    mpu.resetFIFO()
    packetSize = mpu.dmpGetFIFOPacketSize()
    if file1 != None:
        thread.start_new_thread(writeThread,(file1,1))

    while True:
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
def hm5883lThread(fileToWrite=None):
    global magData
    global magDatas
    magDatas = list()
    file1  = fileOpen(fileToWrite)
    if file1 != None:
        thread.start_new_thread(writeThread,(file1,2))
    # HM5883l
    mag = hmc5883l.HMC5883L()
    mag.initialize()
    while True:
        magData = mag.getHeading() 
        magData['time']= float(time.time())
	if file1 != None:
		magDatas.append(magData)
        time.sleep(0.02)

def bmpThread(fileToWrite=None):
    global bmpData
    global bmpDatas
    bmpDatas = list()
    file1  = fileOpen(fileToWrite)
    if file1 != None:
        thread.start_new_thread(writeThread,(file1,3))
    # BMP085
    bmp = bmp085.BMP085()
    # needless of initialization
    while True:
        bmpData = bmp.readData()
        bmpData['time']= float(time.time())
	if file1 != None:
		bmpDatas.append(bmpData)
        time.sleep(0.1)


def main():
    run = True
    global mpuData
    global magData
    global bmpData
    fileMpu = "/mnt/sd/mpu.dat"
    fileMag = "/mnt/sd/mag.dat"
    fileBmp = "/mnt/sd/bmp.dat"
    try:
        thread.start_new_thread(mpu6050Thread,(fileMpu,))
        thread.start_new_thread(hm5883lThread,(fileMag,))
        thread.start_new_thread(bmpThread,(fileBmp,))
    except:
        print("Error with threading")
        run = False
    time.sleep(4)
    while run:
        #print mpuData,
	#print magData,
	#print bmpData
	time.sleep(0.1)

if __name__ == '__main__':
    main()
