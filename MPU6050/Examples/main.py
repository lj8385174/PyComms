import time
import math
import mpu6050

# Sensor initialization
mpu = mpu6050.MPU6050()
mpu.dmpInitialize()
mpu.setDMPEnabled(True)
mpu.setI2CBypassEnabled(False)
mpu.setSlaveAddress(0,0x1e)
print 'slave0\'s address: ',mpu.getSlaveAddress(0)
mpu.getWaitForExternalSensorEnabled()
print 'mpu\'s temperature is ',mpu.getTemperature()
mpu.setSlaveRegister(0,0x03)
mpu.setSlaveDataLength(0,2)
mpu.setSlaveEnabled(0,True)
print 'slave0 is enabled'
time.sleep(1)
print 'a data: ',mpu.getExternalSensorByte(74)

