import logging
import serial
import time
import datetime
import re
import configparser
from numpy import array, sqrt
#from PyQt4.QtCore import QMutex, QMutexLocker
 

logger = logging.getLogger('AE')
##logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)


class MotorModels(object):
	Name = {0:'3Bop',1:"dummy"}
##	Name = {0:'3Bop',1:'Velmex',2:'PI',3:"dummy"}
	Number ={v: k for k, v in Name.items()}

class MotorError    (Exception):
	"""Motor error"""
	def __init__(self,msg):
		Exception.__init__(self,msg)
# end class MotorError

class MotorParams(object):
	"""
	Holds the settings needed to create a Move instance, and saved in the config file.
	Note: only attributes beginning with a lower case letter are saved (no capital, no _)
	"""

	def __init__(self, dic=None):
		if dic is None:
			self.modelName  = "3Bop"
			self.baudRate   = 115200
			self.serialPort = 3        #COM10
			self.maxX       = 100
			self.maxY       = 170
			self.maxZ       = 170
			self.limits     = [[ 0, self.maxX ],[ 0, self.maxY ],[ 0, self.maxZ ]]
			self.speed      = [-1.0,-1.0,-1.0]
		else:
			for k in dic.iterkeys():
				self.__setattr__(k, dic[k])
			if ("limX" in dic) and self.limX is not None:
				self.limits = [self.limX,self.limY,self.limZ]
			if "speed" not in dic or self.speed is None:
				self.speed = [-1.0,-1.0,-1.0]
	# end def __init__
	def copy(self, data = None):
		if (type(data)==type({})):
			self.modelName  = data["modelName"]
			self.baudRate   = data["baudRate"]
			self.serialPort = data["serialPort"]
			self.maxX       = data["maxX"]
			self.maxY       = data["maxY"]
			self.maxZ       = data["maxZ"]
			self.limits     = data["limits"]
			self.speed      = data["speed"]
# end class MotorParams


class Motors(object):
	"""
	Object to connect and communicate with a 3D positioning system
	"""

	def __init__(self, motorParams):
# 		self.mutex = QMutex()
		self.motorParams = motorParams
		self.connected = False
		self.ready = False
		self.firmware_version = ''
		self._current_position = [-1.00,-1.00,-1.00]  # current position of mechanical system
		self._relative_motion = [0.00,0.00,0.00]  # by default all motions are relative = target - current
		self._moving = [ False, False, False ]  # list of bool, one per axis, True when moving
		self._axisLetter = [ 'X','Y', 'Z' ] # list of axes units, unit=hardware identifier (>0)

	# end def __init__

	# CONNECTION FUNCTIONS ________________________________________________

	def connect(self, port = 3, baudRate = 115200):
		pass
	# end def connect

	def disconnect(self):
		pass
	# end def disconnect

	def motorType(self):
		return self.motorParams.modelName
	# end def motorType

	def stopAllOnExit(self):
		if not self.connected:
			return
		# end if
		self.disconnect()
	# end def stopAllOnExit

	# MOVEMENT FUNCTIONS ___________________________________________________
	def homeAxis(self, axis):
		pass

	def moveAxisTo(self, axis, pos):
		pass

	def moveAxisRel(self, axis, offset):
		pass

	def readPosition(self, axis, forceRead=True):
		pass

	# Switch motors on/off __________________________________________________
	def getAxisState(self, axis):
		pass

	def setAxisState(self, axis, state):
		"""Changes the state of the motor, state(bool)."""
		pass
	# end def setAxisState

	def allAxesOn(self):
		pass

	# WAITING FUNCTIONS ____________________________________________________
	def waitOnAxes(self, step=0.1):
		"""step(float): seconds to wait between each command to check if motion is over."""
		while not self.ready:
			time.sleep(step)

	def getAxisVelocity(self, axis):
		pass

	def setAxisVelocity(self, axis, vel):
		"""Change axis velocity, can be done while moving, vel is a float in physical unit/second."""
		pass

	def emergencyStop(self):
		pass

	def isReady(self):
		return self.ready

	def isConnected(self):
		return self.connected

	def getCurrentPosition(self):
		return self._current_position

# end class Motor

class Motor_3Bop(Motors):
	"""
	Object to connect and communicate with 3Bop positioning system
	"""


	ERRORS = {
			0:   ["NO ERROR",                              "No error "],
			1:   ["PARAM SYNTAX",                          "Parameter syntax error"]
	}


	def __init__(self, motorParams):
		Motors.__init__(self, motorParams)
		self._axisLetter = [ 'X','Y', 'Z' ] # list of axes units, unit=hardware identifier (>0)
		self.pattern = "X:([-+]?[0-9]*\.[0-9]*),Y:([-+]?[0-9]*\.[0-9]*),Z:([-+]?[0-9]*\.[0-9]*)"
		self.M114_re = re.compile(self.pattern)
		self.config = configparser.ConfigParser()
		self.config.read('config_scan.ini')
		msg = "3Bop"
		logger.debug(msg)
	# end def __init__
    
	
	def reload(self):
       
		self.config.read('config/config_scan.ini')

	# CONNECTION FUNCTIONS ________________________________________________

	def connect(self, port = 3, baudRate = 115200):
		timeout=5
		self.com = serial.Serial('Com'+str(port), baudRate, timeout=timeout)
		line=self.com.readline().rstrip()
		msg = "port= {} baudRate= {}".format(port,baudRate)
		logger.debug(msg)
		if line ==  'start':
			portOk = True
		finished=False
		isOK = False
		error = False
		version = ''
		start_time=time.time()
		while ( not finished ):
			line=self.com.readline().rstrip()
			if(line!=''):
				line2=line.decode('utf-8')
				token = line2.split()
				if token[0] == 'ok':
					isOK = True
					finished = True
				if token[0] == '//':
					if token[1] == 'BBBop_Meca':
						version = token[2]
				if token[0] == '!!':
					finished = True
				if ((time.time()-start_time)>timeout):
					finished =True
		if (isOK) and (not error):
			self.connected = True
		else:
			self.com.close()
			raise MotorError("Error could not connect to Motors")

		msg = "finished: {} isOK: {} connected: {}".format(finished, isOK, self.connected)
		logger.debug(msg)

	# end def connect

	def disconnect(self):
		self.com.close()
		self.connected = False
		self.ready = False
		self.firmware_version = ''

	# end def disconnect

	def wait_for_ok(self,timeout=30):
		""" function to wait for an ok answer from the mechanical system
		returns the answer as a list of strings corresponding each to a line
		"""
		start_time=time.time()
		finished=False
		lines = []
		while ( not finished ):
			line=self.com.readline().rstrip()
			if(line!=''):
##				print line
				line=line[:2]
				finished = (line == 'ok') or (line == '!!') or ((time.time()-start_time)>timeout)
		return line


	def sendCommand(self,cmd, waitForOK=True,timeout=30):
		"""
		(low-level) Sends a command to the motor unit
		command(str): the command to send
		expectAnswer(bool): True wait for OK and send answer
		return(list): [error(bool), answer(str)], if error is True, answer is a list ["CODE", "MESSAGE"], raise MotorError if not connected
		"""
		self.ready = False
		self.com.write(cmd.encode())
		error = False
		lines = []
		if waitForOK:
			finished=False
			start_time=time.time()
			while ( not finished ):
				line=self.com.readline().rstrip()
				if(line!=''):
					lines.append(line.decode('utf-8'))
					line2=line.decode('utf-8')
					token = line2.split()
					if(len(token)>0):
						if token[0] == 'ok':
							self.ready = True
							finished = True
						if token[0] == '!!':
							self.ready = True
							finished = True
							error = True
				
					if ((time.time()-start_time)>timeout):
						finished = True
						error = True
						raise MotorError("timeout error")
			if error:
				return [True, lines]
			else:
				return [False, lines]
							
							
							
							
# 	def sendCommandvmutex(self,cmd, waitForOK=True,timeout=10):
# 		"""
# 		(low-level) Sends a command to the motor unit
# 		command(str): the command to send
# 		expectAnswer(bool): True wait for OK and send answer
# 		return(list): [error(bool), answer(str)], if error is True, answer is a list ["CODE", "MESSAGE"], raise MotorError if not connected
# 		"""

# 		with QMutexLocker(self.mutex):
# 			self.ready = False
# 			self.com.write(cmd)
# 			error = False
# 			lines = []
# 			if waitForOK:
# 				finished=False
# 				start_time=time.time()
# 				while ( not finished ):
# 					line=self.com.readline().rstrip()
# 					if(line!=''):
# 						lines.append(line)
# 						token = line.split()
# 						if token[0] == 'ok':
# 							self.ready = True
# 							finished = True
# 						if token[0] == '!!':
# 							self.ready = True
# 							finished = True
# 							error = True
# 						if ((time.time()-start_time)>timeout):
# 							finished = True
# 							error = True
# 							raise MotorError("timeout error")

# 		if error:
# 			return [True, lines]
# 		else:
# 			return [False, lines]
# 	# end def sendCommand

	def readAnswer(self,timeout=30):
		"""
		read the answer to a command on the serial port.
		return list of string corresponding to the lines in the answer on success,
		raises a MotorError on error
		"""
		finished=False
		error = False
		lines = []
		start_time=time.time()
		while ( not finished ):
			line=self.com.readline().rstrip()
			if(line!=''):
				lines.append(line)
				token = line.split()
				if token[0] == 'ok':
					ready = True
					finished = True
				if token[0] == '!!':
					ready = True
					finished = True
					error = True
				if ((time.time()-start_time)>timeout):
					finished = True
					error = True
					raise MotorError("timeout error")
		return lines
	# end def readAnswer

	def stopAllOnExit(self):
		if not self.connected:
			return
		# end if
		self.disconnect()
	# end def stopAllOnExit

	# MOVEMENT FUNCTIONS ___________________________________________________
	def homeAxis(self, axis):
		if not self.connected :
			raise MotorError("Motor not connected.")
		cmd_G28="G28 " + self._axisLetter[axis] +"\n"
##		cmd_G28="T5 1 0.0 0.0 0.0\n"
		self.sendCommand(cmd_G28)
		self.readPosition(axis,forceRead = True)
		ax1_init = (self._current_position[0]>=0.0)
		ax2_init = (self._current_position[1]>=0.0)
		ax3_init = (self._current_position[2]>=0.0)
		if(ax1_init and ax2_init and ax3_init):
			self.ready = True
##        T5_cmd = "T5 1 %2.2f %2.2f %2.2f \n" % tuple(self._current_position)
##        self.motor.sendCommand(T5_cmd)
	# end def homeAxis
	def define_current_position(self):
		self._current_position[0]=float(self.config['motor']['current_positionX'])
		self._current_position[1]=float(self.config['motor']['current_positionY'])
		self._current_position[2]=float(self.config['motor']['current_positionZ'])

	def moveAxisTo(self, axis, pos):
		if not self.connected :
			raise MotorError("Motor not connected.")
		if self._current_position[axis] < 0.0 :
			msg = 'Motion on unreferenced axis, axis: {}, current position: {}'.format(axis,self._current_position)
			raise MotorError(msg)
		target = round(pos,4)
		if (target<self.motorParams.limits[axis][0]) or (target>self.motorParams.limits[axis][1]):
			msg = 'Motion out of bounds, axis: {}, pos: {}'.format(axis,pos)
			raise MotorError(msg)
		current = round(self._current_position[axis],4)
		relative_move = target - current
		msg = "axis: {} , target: {}, curent:{}, rel.move: {}".format(axis, target, current, relative_move)
		logger.debug(msg)
		if relative_move != 0.0:
			cmd_format_G1="G1 "+self._axisLetter[axis]+"{:.4f}\n"
			cmd_G1 = cmd_format_G1.format(relative_move)
			status=self.sendCommand(cmd_G1)
			if status[0]:
				msg = "error from motor: {}".format(status[1])
				logger.debug(msg)
				raise MotorError(msg)
			xyz = self.readPosition(axis,forceRead = True)
		# end if
	# end def moveAxisTo

	def moveAxisRel(self, axis, offset):
		self.moveAxisTo(axis, offset + self.readPosition(axis,forceRead=False)[axis])
	# end def shiftAxis

	def readPosition(self, axis, forceRead=True):
		if (forceRead):
			M114_answer=self.sendCommand("M114\n")
			for line in M114_answer[1]:
				split_str=line.split()
				if split_str[0]=='ok':
					match_M114=self.M114_re.match(split_str[1])
					self._current_position = [float(x) for x in match_M114.groups()]
				else:
					if split_str[0]=='!!':
						print("error"+split_str[1])
						self._current_position = [-1.0,-1.0,-1.0]
						self.ready = False
		msg = "current_position: {} ".format(self._current_position)
		logger.debug(msg)
		return self._current_position
	# end def readPosition

	# Switch motors on/off __________________________________________________
	def getAxisState(self, axis):
		"""Returns True if the motor is On, False if Off."""
		return self.connected
	# end def getAxisState

	def setAxisState(self, axis, state):
		"""Changes the state of the motor, state(bool)."""
		pass
	# end def setAxisState

	def allAxesOn(self):
		"""if motors are connected -> axes are ON"""
		return self.connected
	# end def allAxesOn


	# WAITING FUNCTIONS ____________________________________________________
	def waitOnAxes(self, step=0.1):
		"""step(float): seconds to wait between each command to check if motion is over."""
		while not self.ready:
			time.sleep(step)

	def getAxisVelocity(self, axis):
		return float(0.0)
	# end def getAxisVelocity

	def setAxisVelocity(self, axis, vel):
		"""Change axis velocity, can be done while moving, vel is a float in physical unit/second."""
		pass
		# end def setAxisVelocity

	def emergencyStop(self):
		M114_answer=self.sendCommand("&")

class Motor_dummy(Motors):
	"""
	Mock Object for Motor
	"""


	def __init__(self,motorParams):
		Motors.__init__(self, motorParams)
		self.axisState = [True,True,True]
		msg = "dummy"
		logger.debug(msg)

	# CONNECTION FUNCTIONS ________________________________________________

	def connect(self, port = 3, baudRate = 115200):
		self.connected = True

	def disconnect(self):
		self._current_position = [-1.00,-1.00,-1.00]
		self.connected = False
		self.ready = False

	def homeAxis(self, axis):
		if not self.connected :
			raise MotorError("Motor not connected.")
		self._current_position[axis] = 0.0
		ax1_init = (self._current_position[0]>=0.0)
		ax2_init = (self._current_position[1]>=0.0)
		ax3_init = (self._current_position[2]>=0.0)
		if(ax1_init and ax2_init and ax3_init):
			self.ready = True


	def moveAxisTo(self, axis, pos):
		if not self.connected :
			raise MotorError("Motor not connected.")
		if self._current_position[axis] < 0.0 :
			msg = 'Motion on unreferenced axis, axis: {}, current position: {}'.format(axis,self._current_position)
			raise MotorError(msg)
		target = round(pos,4)
		if (target<self.motorParams.limits[axis][0]) or (target>self.motorParams.limits[axis][1]):
			msg = 'Motion out of bounds, axis: {}, pos: {}'.format(axis,pos)
			raise MotorError(msg)
		self._current_position[axis] = target

	def moveAxisRel(self, axis, offset):
		self.moveAxisTo(axis, offset + self._current_position[axis])
	# end def shiftAxis

	def readPosition(self, axis, forceRead=True):
		return self._current_position
	# Switch motors on/off __________________________________________________

	def getAxisVelocity(self, axis):
		return float(0.0)
	# end def getAxisVelocity

	def setAxisVelocity(self, axis, vel):
		"""Change axis velocity, can be done while moving, vel is a float in physical unit/second."""
		pass
		# end def setAxisVelocity

	def getAxisState(self, axis):
		"""Returns True if the motor is On, False if Off."""
		return self.axisState[axis]
	# end def getAxisState

	def setAxisState(self, axis, state):
		"""Changes the state of the motor, state(bool)."""
		self.axisState[axis]=state
	# end def setAxisState

	def allAxesOn(self):
		"""if motors are connected -> axes are ON"""
		return self.axisState[0] and self.axisState[1] and self.axisState[2]
	# end def allAxesOn


def getMotors(motorParams):
	"""
	Returns an instance of the Motors object of requested model.

	:param str modelName: a string.
	:return: an instance of the corresponding Motors object.
	:raise: a motorError if the model is not supported.
	"""
	modelName = str(motorParams.modelName)
	if modelName == "3Bop":
		return Motor_3Bop(motorParams)
	elif modelName.startswith("dummy"):
		return Motor_dummy(motorParams)
	raise MotorError("Unsupported model (%s)." % modelName)

if __name__ == '__main__':
	my_motor_params = MotorParams()
	my_motor_3Bop = Motor_3Bop(my_motor_params)
	my_motor_dummy = Motor_dummy(my_motor_params)
	my_motor_dummy.connect()
	my_motor_dummy.homeAxis(0)
	my_motor_dummy.homeAxis(1)
	my_motor_dummy.homeAxis(2)
	my_motor_dummy.moveAxisTo(0,10.0)
	my_motor_dummy.moveAxisTo(1,15.0)
	my_motor_dummy.moveAxisTo(2,20.0)
	print(my_motor_dummy.getCurrentPosition())