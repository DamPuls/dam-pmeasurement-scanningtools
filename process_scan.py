
# -*- coding: utf-8 -*-
"""
Created on Fri May 23 09:40:44 2025

@author: MathieuGUYOT
"""
import sys

import Sequence
import scope_pico 
from Scan import ScanParams,Scan
from scope_pico import scope_pico 
from acquisition import acquisition_pico 
from Motors_3Bop import MotorParams, Motor_3Bop
from acquisition import acquisition_pico
from  generator_trig import generator_trig  
import matplotlib.pyplot as plt
import time 
from datetime import datetime 
import os 
import shutil 
import numpy as np
import configparser

class scanning :
	def __init__(self):
		self.my_motor_params = MotorParams()
		self.motor = Motor_3Bop(self.my_motor_params)
		self.sc=scope_pico()
		self.acq=acquisition_pico(self.sc)
		self.trig_shot=generator_trig(self.sc)
		self.config = configparser.ConfigParser()
		self.config.read('config/config_scan.ini')
		
	    
	def reload(self):
		self.config.read('config/config_scan.ini')
		self.motor.reload()
		self.sc.reload()
		self.acq.reload()

	def axes_init(self):
		self.motor.connect()
		
	def origin_init(self,axis):
		self.motor.homeAxis(axis)
		
	def go_start(self,axis):
		self.reload()
		if(axis==0):
			pos=float(self.config['Cord_p0']['cordp0_axes1'])
			print(pos)
		elif(axis==1):
			pos=float(self.config['Cord_p0']['cordp0_axes2'])
		elif(axis==2):
			pos=float(self.config['Cord_p0']['cordp0_axes3'])
		
		self.motor.moveAxisTo(axis, pos)
		
	def scope_connect(self):
		self.sc.connect()
	
	def scope_init(self):
		self.sc.config_channel()
		self.sc.config_trigger()
		self.acq.config_acquisition()
		self.trig_shot.config_trig()
		
	def define_current_date(self):
		tmp_current_date=datetime .now()
		self.curent_date=str(tmp_current_date.year)+'_'+str(tmp_current_date.month)+'_'+str(tmp_current_date.day)+'_'+str(tmp_current_date.hour)+'_'+str(tmp_current_date.minute)+'_'+str(tmp_current_date.second)
		#+'_'tmp_current_date.day+'_'+tmp_current_date.hour+'_'+tmp_current_date.minute+'_'+tmp_current_date.seconde
	
	def save_config(self): 
		src='config'
		dst=self.folder_name+'/config'
		shutil.copytree(src, dst)
		
	def create_result_folder(self):
		self.folder_name='measure/'+'measure'+self.curent_date
		os.mkdir(self.folder_name)
		self.folder_name_data='measure/'+'measure'+self.curent_date+'/'+'data'
		os.mkdir(self.folder_name_data)
		
	def init_scan(self):
		myScanParams = {}
		self.myScan = Scan(self.motor,myScanParams)
		self.myScan.config_scan()
		self.gridSize = self.myScan.grid.gridSize
		seqDimensions =  self.myScan.sequence.getDimensions()
		print('sequence Dimensions: ', seqDimensions)
		print('gridSize: ',self.gridSize)
		print('length X: {:.3f}, Y: {:.3f}, Z: {:.3f}'.format(self.myScan.grid.lengthX,self.myScan.grid.lengthY,self.myScan.grid.lengthZ))
		print('gridSize: ',self.gridSize)
		
	def save_data(self, ind_acqu,position ):
		str_position='_X_'+str(position[0])+'_Y_'+str(position[1])+'_Z_'+str(position[2])+'_'
		file_name=self.folder_name_data+'/'+'ind'+str(ind_acqu)+str_position+'.txt'
		np.savetxt(file_name,np.c_[self.acq.time_line,self.acq.data], delimiter=' ')   # x,y,z equal sized 1D arrays
	
	def run_scan(self):
		t1=time.time()
		self.define_current_date()
		self.create_result_folder()
		self.reload()
		self.scope_init()
		self.init_scan()
		self.save_config()
		delay_mvt_acq=int(self.config['delaymvt_acq']['delayms'])*0.001
		for ind in range(self.gridSize):
			self.myScan.moveForward()
			self.acq.running_block()
			position=self.motor.getCurrentPosition()
			time.sleep(delay_mvt_acq)
			self.trig_shot.gene_trig()
			self.acq.get_data()
			plt.plot(self.acq.time_line,self.acq.data)
			plt.show()
			self.save_data(ind,position)
		t2=time.time()
		print('duration acquisition ')
		print (t2-t1)
	def run_shot_sequence(self):
		self.scope_init()
		self.define_current_date()
		self.create_result_folder()
		self.reload()
		delay_shot=int(self.config['sequence_shot']['delayshot'])*0.001
		Nshot=int(self.config['sequence_shot']['number_shot'])
		t1=time.time()
		self.acq.running_block()
		position=self.motor.getCurrentPosition()
		for ind in range(0,Nshot):
			
			self.trig_shot.gene_trig()
			self.acq.get_data()
			plt.plot(self.acq.time_line,self.acq.data)
			plt.show()
			self.save_data(ind,position)
			time.sleep(delay_shot)
		t2=time.time()

		print(t2-t1)
		
		
	def disconnect(self):
		self.motor.disconnect()
		self.sc.close()
