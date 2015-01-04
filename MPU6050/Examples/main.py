import time
import math
import mpu6050
import hmc5883l
import bmp085

## Copied from 6axis_dmp.py
## It will set to the HM5883l bypassthrough mode

# Sensors initialization
mpu = mpu6050.MPU6050()
mpu.dmpInitialize()

# HM5883l
mag = hmc5883l.HMC5883L()
mag.initialize()

# BMP085
bmp = bmp085.BMP085()
# needless of initialization

mpu.setDMPEnabled(True)
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
        
        #get the magnetic intensity correspondingly
        magData = mag.getHeading() 
        print q['w'],q['x'],q['y'],q['z'],
        print(ypr['yaw'] * 180 / math.pi),
        print(ypr['pitch'] * 180 / math.pi),
        print(ypr['roll'] * 180 / math.pi),
        print magData['x'],magData['y'],magData['z']
    
        # track FIFO count here in case there is > 1 packet available
        # (this lets us immediately read more without waiting for an interrupt)        
        fifoCount -= packetSize  


