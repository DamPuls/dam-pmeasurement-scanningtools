# -*- coding: utf-8 -*-
"""
Created on Wed May 21 15:48:52 2025

@author: MathieuGUYOT
"""

import Sequence
import scope_pico 
from Scan import ScanParams,Scan
from scope_pico import scope_pico 
from acquisition import acquisition_pico 
from Motors_3Bop import MotorParams, Motor_3Bop
from acquisition import acquisition_pico
from generator_trig import generator_trig  
import matplotlib.pyplot as plt
import time 
p0 = [10,10,10]
dirx = [1.0,0.0,0.0]
diry = [0.0,1.0,0.0]
dirz = [0.0,0.0,1.0]
nx = 3
ny = 3
nz = 3

###
#motort init 
###
my_motor_params = MotorParams()
my_motor_3Bop = Motor_3Bop(my_motor_params)
my_motor_3Bop.connect()
my_motor_3Bop
#my_motor_3Bop.define_current_position
my_motor_3Bop.homeAxis(0)
my_motor_3Bop.homeAxis(1)
my_motor_3Bop.homeAxis(2)

###
#config channel
##
# sc=scope_pico()
# sc=scope_pico()
# acq=acquisition_pico(sc)
# trig_shot=generator_trig(sc)
# sc.connect()
# sc.config_channel()
# sc.config_trigger()
# acq.config_acquisition()
# trig_shot.config_trig()


myScanParams = ScanParams()
myScanParams.p0 = p0
myScanParams.dirX = dirx
myScanParams.dirY = diry
myScanParams.dirZ = dirz
myScanParams.nx = nx
myScanParams.ny = ny
myScanParams.nz = nz
myScan = Scan(my_motor_3Bop,myScanParams)
gridSize = myScan.grid.gridSize
seqDimensions =  myScan.sequence.getDimensions()
print('sequence Dimensions: ', seqDimensions)
print('gridSize: ', gridSize)
print('length X: {:.3f}, Y: {:.3f}, Z: {:.3f}'.format(myScan.grid.lengthX,myScan.grid.lengthY,myScan.grid.lengthZ))
print('gridSize: ', gridSize)
myScan.moveToStart()

##
#Start scanning 
##
t1=time.time()
for i in range(gridSize):
	myScan.moveForward()
	print(my_motor_3Bop.getCurrentPosition())
	toto=my_motor_3Bop.getCurrentPosition()
	str_position='_X_'+str(toto[0])+'_Y_'+str(toto[1])+'_Z_'+str(toto[2])+'_'
	#acq.running_block()
	#trig_shot.gene_trig()
	#acq.get_data()
	#plt.plot(acq.time_line,acq.data)
	plt.show()
t2=time.time()
print (t2-t1)
my_motor_3Bop.disconnect()
#sc.close()