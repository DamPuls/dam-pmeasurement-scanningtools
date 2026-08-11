# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Scan
# Purpose:
#
# Author:      ED
#
# Created:     04/03/2017
# Copyright:   (c) ED 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from __future__ import print_function
import logging
import time
import datetime
from Motors_3Bop            import MotorParams,Motors, getMotors
from Sequence               import Sequence,getSequence
from Grid                   import Grid
import configparser
logger = logging.getLogger('AE')
##logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)

class ScanError(Exception):
	"""ScanError error"""
# end class ScanError


class ScanParams(object):
	"""
	Holds the settings needed to create a Scan instance, and saved in the config file.
	Note: only attributes beginning with a lower case letter are saved (no capital, no _)
	"""

	def __init__(self, dic=None):
		if dic is None:
			self.p0                  = [ 0.0, 0.0, 0.0 ]
			self.dirX                = [ 1.0, 0.0, 0.0 ]
			self.dirY                = [ 0.0, 1.0, 0.0 ]
			self.dirZ                = [ 0.0, 0.0, 1.0 ]
			self.nx                  = 1
			self.ny                  = 1
			self.nz                  = 1
			self.sequenceIndex       = 0
			self.sequenceName        = "RectDirect"
		else:
			for k in dic.iterkeys():
				self.__setattr__(k, dic[k])

	def copy(self, data = None):
		if (type(data)==type({})):
			self.p0                  = data["p0"]
			self.dirX                = data["dirX"]
			self.dirY                = data["dirY"]
			self.dirZ                = data["dirZ"]
			self.nx                  = data["nx"]
			self.ny                  = data["ny"]
			self.nz                  = data["nz"]
			self.sequenceIndex       = data["sequenceIndex"]
			self.sequenceName        = data["sequenceName"]

# end class scanParams


class Scan(object):
	"""
	Object to execute movement
	Uses:
			motor
			Sequence
	"""

	def __init__(self, motor, scanParams):
		
		self.params   = scanParams
		self.motor     = motor
		self.config = configparser.ConfigParser()
		   
		self.config.read('config/config_scan.ini')
		self.config_scan()
# 		print(scanParams.p0)
# 		self.grid     = Grid(scanParams.p0,
#                              scanParams.dirX,scanParams.dirY,scanParams.dirZ,
#                              scanParams.nx,scanParams.ny,scanParams.nz)

# 		self.sequence = getSequence(scanParams.sequenceName,self.grid)
# 		self.currentIndex = None
		
	# end def __init__
	
    
	def reload(self,file_ini):
		self.config.read(file_ini)

	# MOVEMENT _____________________________________________________________
	def _moveTo(self):
		self._checkAxes()
		self._checkSequence()

		next_position = self.sequence.getPosition(self.currentIndex)
		self.motor.moveAxisTo(0, next_position[0])
		self.motor.moveAxisTo(1, next_position[1])
		self.motor.moveAxisTo(2, next_position[2])
	# end def _moveTo
		#self.currentIndex = None

	def moveToStart(self):
		self.currentIndex = 0
		self._moveTo()
	# end def moveToStart

	def moveToEnd(self):
		self.currentIndex = self.sequence.gridSize-1
		self._moveTo()
	# end def moveToEnd

	def moveForward(self):
		if self.currentIndex is None:
			self.moveToStart()
		elif self.isAtEnd():
			return False
		else:
			self.currentIndex += 1
			self._moveTo()
		# end if
		return True
	# end def moveForward

	def moveBackward(self):
		if self.currentIndex is None:
			self.moveToEnd()
		elif self.isAtStart():
			return False
		else:
			self.currentIndex -= 1
			self._moveTo()
		# end if
		return True
	# end def moveBackward

	def waitOnMovement(self, tmp=0):
		self.motor.waitOnAxes(tmp)
	# end def waitOnMovement

	def isAtStart(self):
		return self.currentIndex == 0
	# end def isAtStart

	def isAtEnd(self):
		return self.currentIndex == (self.sequence.gridSize-1)
	# end def isAtEnd

	def getPosition(self):
		return self.sequence.getPosition(self.currentIndex)
	# end def getPosition

	def getPositionIndex(self):
		return self.sequence.getGridIndex(self.currentIndex)
	# end def getPositionIndex


	# ERROR FUNCTIONS ______________________________________________________
	def _checkAxes(self):
		if self.motor is None:
			raise ScanError("motor isn't defined")
		# end if
	# end def _checkAxes

	def _checkSequence(self):
		if self.sequence is None:
			raise ScanError("Sequence isn't defined")
		# end if
	# end def _checkSequence
# end class Scan


 ##coding 2025
	def config_scan(self):
		myScanParams = ScanParams()
		Xpo=float(self.config['Cord_p0']['cordp0_axes1'])
		Ypo=float(self.config['Cord_p0']['cordp0_axes2'])
		Zpo=float(self.config['Cord_p0']['cordp0_axes3'])
		myScanParams.p0 = [Xpo,Ypo,Zpo]
		print('p0=')
		print(myScanParams.p0)
		dirx1=float(self.config['DirectionX']['dir_axes1'])
		dirx2=float(self.config['DirectionX']['dir_axes2'])
		dirx3=float(self.config['DirectionX']['dir_axes3'])
		myScanParams.dirX = [dirx1,dirx2,dirx3]
		print('dirx=')
		print(myScanParams.dirX)
		diry1=float(self.config['DirectionY']['dir_axes1'])
		diry2=float(self.config['DirectionY']['dir_axes2'])
		diry3=float(self.config['DirectionY']['dir_axes3'])
		myScanParams.dirY= [diry1,diry2,diry3]
		print('diry=')
		print(myScanParams.dirY)
		dirz1=float(self.config['DirectionZ']['dir_axes1'])
		dirz2=float(self.config['DirectionZ']['dir_axes2'])
		dirz3=float(self.config['DirectionZ']['dir_axes3'])
		myScanParams.dirZ= [dirz1,dirz2,dirz3]
		print('dirz=')
		print(myScanParams.dirZ)
		myScanParams.nx =int( self.config['Number of points']['nx'])
		myScanParams.ny =int(self.config['Number of points']['ny'])
		myScanParams.nz =int(self.config['Number of points']['nz'])
		print('nx='+str(myScanParams.nx)+'ny='+str(myScanParams.ny)+'nz='+str(myScanParams.nz))
		self.grid     = Grid(myScanParams.p0,
                             myScanParams.dirX,myScanParams.dirY,myScanParams.dirZ,
                             myScanParams.nx,myScanParams.ny,myScanParams.nz)
		self.grid.printGrid()
		self.sequence = getSequence(myScanParams.sequenceName,self.grid)
		self.currentIndex = None
if __name__ == '__main__':
	p0 = [10.0,15.0,20.0]
	dirx = [1.0,0.0,0.0]
	diry = [0.0,1.0,0.0]
	dirz = [0.0,0.0,1.0]
	nx = 3
	ny = 3
	nz = 3
	my_motor_params = MotorParams()
	my_motor_params.modelName = "dummy"
	my_motor_dummy = getMotors(my_motor_params)
	my_motor_dummy.connect()
	my_motor_dummy.homeAxis(0)
	my_motor_dummy.homeAxis(1)
	my_motor_dum
	my.homeAxis(2)
	myScanParams = ScanParams()
	myScanParams.p0 = p0
	myScanParams.dirX = dirx
	myScanParams.dirY = diry
	myScanParams.dirZ = dirz
	myScanParams.nx = nx
	myScanParams.ny = ny
	myScanParams.nz = nz
	myScan = Scan(my_motor_dummy,myScanParams)
	gridSize = myScan.grid.gridSize
	seqDimensions =  myScan.sequence.getDimensions()
	print('sequence Dimensions: ', seqDimensions)
	print('gridSize: ', gridSize)
	print('length X: {:.3f}, Y: {:.3f}, Z: {:.3f}'.format(myScan.grid.lengthX,myScan.grid.lengthY,myScan.grid.lengthZ))
	print('gridSize: ', gridSize)
	myScan.moveToStart()
	for i in range(gridSize):
		myScan.moveForward()
		print(my_motor_dummy.getCurrentPosition())

