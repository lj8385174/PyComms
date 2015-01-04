import time
import math
import mpu6050
import hmc5883l
import bmp085
import thread


def mpu6050Thread():
    # Sensors initialization
    global mpuData
    mpu = mpu6050.MPU6050()
    mpu.setDMPEnabled(True)
    mpu.resetFIFO()
    packetSize = mpu.dmpGetFIFOPacketSize()
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
            # track FIFO count here in case there is > 1 packet available
            # (this lets us immediately read more without waiting for an interrupt)        
            fifoCount -= packetSize 
def hm5883lThread():
    global magData
    # HM5883l
    mag = hmc5883l.HMC5883L()
    mag.initialize()
    while True:
        magData = mag.getHeading() 
        magData['time']= float(time.time())
        time.sleep(0.02)

def bmpThread():
    global bmpData
    # BMP085
    bmp = bmp085.BMP085()
    # needless of initialization
    while True:
        bmpData = bmp.readData()
        bmpData['time']= float(time.time())
        time.sleep(0.1)


def main():
    run = True
    global mpuData
    global magData
    global bmpData
    try:
        thread.start_new_thread(mpu6050Thread,())
        thread.start_new_thread(hm5883lThread,())
        thread.start_new_thread(bmpThread,())
    except:
        print "Error with threading"
        run = False
    time.sleep(4)
    while run:
        print mpuData,
	print magData,
	print bmpData
	time.sleep(0.1)

if __name__ == '__main__':
    main()
