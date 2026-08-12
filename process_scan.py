
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
		
	    
	def reload(self,file_ini):
		self.config.read(file_ini)
		self.motor.reload()
		self.sc.reload(file_ini)
		self.acq.reload(file_ini)
		self.config.read(file_ini)

	def axes_init(self):
		self.motor.connect()
		
	def origin_init(self,axis):
		self.motor.homeAxis(axis)
	
	def read_axes(self):
		dir_matrice = [
		[0, 0, 0],
		[0, 0, 0],
		[0, 0, 0]
		]
		dir_matrice[0][0]=round(float(self.config['DirectionX']['dir_axes1']),2)
		dir_matrice[0][1]=round(float(self.config['DirectionX']['dir_axes2']),2)
		dir_matrice[0][2]=round(float(self.config['DirectionX']['dir_axes3']),2)
		
		dir_matrice[1][0]=round(float(self.config['DirectionY']['dir_axes1']),2)
		dir_matrice[1][1]=round(float(self.config['DirectionY']['dir_axes2']),2)
		dir_matrice[1][2]=round(float(self.config['DirectionY']['dir_axes3']),2)
		
		dir_matrice[2][0]=round(float(self.config['DirectionZ']['dir_axes1']),2)
		dir_matrice[2][1]=round(float(self.config['DirectionZ']['dir_axes2']),2)
		dir_matrice[2][2]=round(float(self.config['DirectionZ']['dir_axes3']),2)
		return dir_matrice
		
	def change_ini(self,file_ini,step,scan_axe,nbr_point_scan):
		self.reload(file_ini)
		dir_matrice = [
		[0, 0, 0],
		[0, 0, 0],
		[0, 0, 0]
		]
		dir_matrice[0][0]=float(self.config['DirectionX']['dir_axes1'])
		dir_matrice[0][1]=float(self.config['DirectionX']['dir_axes2'])
		dir_matrice[0][2]=float(self.config['DirectionX']['dir_axes3'])
		
		dir_matrice[1][0]=float(self.config['DirectionY']['dir_axes1'])
		dir_matrice[1][1]=float(self.config['DirectionY']['dir_axes2'])
		dir_matrice[1][2]=float(self.config['DirectionY']['dir_axes3'])
		
		dir_matrice[2][0]=float(self.config['DirectionZ']['dir_axes1'])
		dir_matrice[2][1]=float(self.config['DirectionZ']['dir_axes2'])
		dir_matrice[2][2]=float(self.config['DirectionZ']['dir_axes3'])
		norm = np.sqrt(sum(x**2 for x in dir_matrice[0]))
		
		self.config['DirectionX']['dir_axes1']=str(round(dir_matrice[0][0]*step[0]/norm,2) )
		self.config['DirectionX']['dir_axes2']=str(round(dir_matrice[0][1]*step[0]/norm,2) )
		self.config['DirectionX']['dir_axes3']=str(round(dir_matrice[0][2]*step[0]/norm,2) )
		norm = np.sqrt(sum(x**2 for x in dir_matrice[1]))
		self.config['DirectionY']['dir_axes1']=str(round(dir_matrice[1][0]*step[1]/norm,2) )
		self.config['DirectionY']['dir_axes2']=str(round(dir_matrice[1][1]*step[1]/norm,2) )
		self.config['DirectionY']['dir_axes3']=str(round(dir_matrice[1][2]*step[1],2))
		norm = np.sqrt(sum(x**2 for x in dir_matrice[2]))
		self.config['DirectionZ']['dir_axes1']=str(round(dir_matrice[2][0]*step[2]/norm,2) )
		self.config['DirectionZ']['dir_axes2']=str(round(dir_matrice[2][1]*step[2]/norm,2) )
		self.config['DirectionZ']['dir_axes3']=str(round(dir_matrice[2][2]*step[2]/norm,2) )
		p0=[0,0,0]
		axes_dir=[0,0,0]
		midle_fov=[0,0,0]
		midle_fov[0]=float(self.config['max_point']['cordm_axes1'])
		midle_fov[1]=float(self.config['max_point']['cordm_axes2'])
		midle_fov[2]=float(self.config['max_point']['cordm_axes3'])
		if(scan_axe==0):
			self.config['Number of points']['nx']=str(nbr_point_scan )
			self.config['Number of points']['ny']=str(1)
			self.config['Number of points']['nz']=str(1)
			axes_dir[0]=float(self.config['DirectionX']['dir_axes1'])
			axes_dir[1]=float(self.config['DirectionX']['dir_axes2'])
			axes_dir[2]=float(self.config['DirectionX']['dir_axes3'])
			p0[0]=midle_fov[0]-(axes_dir[0]*((nbr_point_scan-1)/2))
			p0[1]=midle_fov[1]-(axes_dir[1]*((nbr_point_scan-1)/2))
			p0[2]=midle_fov[2]-((axes_dir[2]*(nbr_point_scan-1)/2))
		elif(scan_axe==1):
			self.config['Number of points']['nx']=str(1)
			self.config['Number of points']['ny']=str(nbr_point_scan )
			self.config['Number of points']['nz']=str(1)
			axes_dir[0]=float(self.config['DirectionY']['dir_axes1'])
			axes_dir[1]=float(self.config['DirectionY']['dir_axes2'])
			axes_dir[2]=float(self.config['DirectionY']['dir_axes3'])
			p0[0]=midle_fov[0]-(axes_dir[0]*((nbr_point_scan-1)/2))
			p0[1]=midle_fov[1]-(axes_dir[1]*((nbr_point_scan-1)/2))
			p0[2]=midle_fov[2]-(axes_dir[2]*((nbr_point_scan-1)/2))
		elif(scan_axe==2):
			self.config['Number of points']['nx']=str(1)
			self.config['Number of points']['ny']=str(1)
			self.config['Number of points']['nz']=str(nbr_point_scan )
			axes_dir[0]=float(self.config['DirectionZ']['dir_axes1'])
			axes_dir[1]=float(self.config['DirectionZ']['dir_axes2'])
			axes_dir[2]=float(self.config['DirectionZ']['dir_axes3'])
			p0[0]=midle_fov[0]-(axes_dir[0]*((nbr_point_scan-1)/2))
			p0[1]=midle_fov[1]-(axes_dir[1]*((nbr_point_scan-1)/2))
			p0[2]=midle_fov[2]-(axes_dir[2]*((nbr_point_scan-1)/2))

		self.config['Cord_p0']['cordp0_axes1']=str(p0[0])
		self.config['Cord_p0']['cordp0_axes2']=str(p0[1] )
		self.config['Cord_p0']['cordp0_axes3']=str(p0[2] )
		for key in ('cordm_axes1','cordm_axes2','cordm_axes3'):
			self.config.remove_option('Cord_p0',key)
		with open(file_ini, "w") as fichier:
			self.config.write(fichier)


	def change_ini_plane(self,file_ini,step,axis1,axis2,n1,n2):
		"""axis1/axis2 in {0,1,2} for X/Y/Z, axis1<axis2. Scans the plane spanned
		by those two axes' direction vectors, centered on [max_point]."""
		self.reload(file_ini)
		dir_sections=['DirectionX','DirectionY','DirectionZ']
		npts_keys=['nx','ny','nz']

		for axis in (axis1,axis2):
			section=dir_sections[axis]
			dir_vec=[float(self.config[section]['dir_axes1']),
			         float(self.config[section]['dir_axes2']),
			         float(self.config[section]['dir_axes3'])]
			norm = np.sqrt(sum(x**2 for x in dir_vec))
			self.config[section]['dir_axes1']=str(round(dir_vec[0]*step[axis]/norm,2))
			self.config[section]['dir_axes2']=str(round(dir_vec[1]*step[axis]/norm,2))
			self.config[section]['dir_axes3']=str(round(dir_vec[2]*step[axis]/norm,2))

		for axis in range(3):
			if axis==axis1:
				self.config['Number of points'][npts_keys[axis]]=str(n1)
			elif axis==axis2:
				self.config['Number of points'][npts_keys[axis]]=str(n2)
			else:
				self.config['Number of points'][npts_keys[axis]]=str(1)

		midle_fov=[float(self.config['max_point']['cordm_axes1']),
		           float(self.config['max_point']['cordm_axes2']),
		           float(self.config['max_point']['cordm_axes3'])]

		dir1=[float(self.config[dir_sections[axis1]]['dir_axes1']),
		      float(self.config[dir_sections[axis1]]['dir_axes2']),
		      float(self.config[dir_sections[axis1]]['dir_axes3'])]
		dir2=[float(self.config[dir_sections[axis2]]['dir_axes1']),
		      float(self.config[dir_sections[axis2]]['dir_axes2']),
		      float(self.config[dir_sections[axis2]]['dir_axes3'])]

		p0=[0,0,0]
		for i in range(3):
			p0[i]=midle_fov[i]-(dir1[i]*((n1-1)/2))-(dir2[i]*((n2-1)/2))

		self.config['Cord_p0']['cordp0_axes1']=str(p0[0])
		self.config['Cord_p0']['cordp0_axes2']=str(p0[1])
		self.config['Cord_p0']['cordp0_axes3']=str(p0[2])
		for key in ('cordm_axes1','cordm_axes2','cordm_axes3'):
			self.config.remove_option('Cord_p0',key)
		with open(file_ini, "w") as fichier:
			self.config.write(fichier)


	def move_step(self,axis,file_ini,step):
		self.reload(file_ini)
		dir_s=[0,0,0]
		if(axis==0):
			dir_s[0]=float(self.config['DirectionX']['dir_axes1'])
			dir_s[1]=float(self.config['DirectionX']['dir_axes2'])
			dir_s[2]=float(self.config['DirectionX']['dir_axes3'])
		if(axis==1):
			dir_s[0]=float(self.config['DirectionY']['dir_axes1'])
			dir_s[1]=float(self.config['DirectionY']['dir_axes2'])
			dir_s[2]=float(self.config['DirectionY']['dir_axes3'])
		if(axis==2):
			dir_s[0]=float(self.config['DirectionZ']['dir_axes1'])
			dir_s[1]=float(self.config['DirectionZ']['dir_axes2'])
			dir_s[2]=float(self.config['DirectionZ']['dir_axes3'])
		norm = np.sqrt(sum(x**2 for x in dir_s))
		self.motor.moveAxisRel(0,round(float(step*dir_s[0]/norm),2))
		self.motor.moveAxisRel(1,round(float(step*dir_s[1]/norm),2))
		self.motor.moveAxisRel(2,round(float(step*dir_s[2]/norm),2))
        
	def go_start(self,axis,file_ini):
			self.reload(file_ini)
			if(axis==0):
				pos=float(self.config['Cord_p0']['cordp0_axes1'])
				print(pos)
			elif(axis==1):
				pos=float(self.config['Cord_p0']['cordp0_axes2'])
			elif(axis==2):
				pos=float(self.config['Cord_p0']['cordp0_axes3'])
			
			self.motor.moveAxisTo(axis, pos)
		
	def get_position(self):
		return self.motor.getCurrentPosition()
	
	
	
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
	
	def save_config(self,fichier_ini): 
		src='config'
		dst=self.folder_name+'/config'
		os.mkdir(dst)
		shutil.copy2(fichier_ini,dst)
		
		
	def create_result_folder(self,save_folder,ini_suffix=''):
		suffix = ('_'+ini_suffix) if ini_suffix else ''
		self.folder_name='measure/'+save_folder+'measure'+self.curent_date+suffix
		os.mkdir(self.folder_name)
		self.folder_name_data=self.folder_name+'/'+'data'
		os.mkdir(self.folder_name_data)
		
	def init_scan(self,ini_file):
		myScanParams = {}
		self.myScan = Scan(self.motor,myScanParams)
		self.myScan.reload(ini_file)
		self.myScan.config_scan()
		self.gridSize = self.myScan.grid.gridSize
		seqDimensions =  self.myScan.sequence.getDimensions()
		print('sequence Dimensions: ', seqDimensions)
		print('gridSize: ',self.gridSize)
		print('length X: {:.3f}, Y: {:.3f}, Z: {:.3f}'.format(self.myScan.grid.lengthX,self.myScan.grid.lengthY,self.myScan.grid.lengthZ))
		print('gridSize: ',self.gridSize)
		
	def print_progress(self, ind, total, t_start, position):
		elapsed = time.time() - t_start
		remaining = (elapsed / (ind + 1)) * (total - (ind + 1))
		def fmt(t):
			h, rem = divmod(int(t), 3600)
			m, s = divmod(rem, 60)
			return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
		print("[{}/{}] elapsed {} / remaining ~{} | X={:.4f} Y={:.4f} Z={:.4f}".format(
			ind + 1, total, fmt(elapsed), fmt(remaining), position[0], position[1], position[2]))

	def save_data(self, ind_acqu,position ):
		str_position='_X_'+str(position[0])+'_Y_'+str(position[1])+'_Z_'+str(position[2])+'_'
		file_name=self.folder_name_data+'/'+'ind'+str(ind_acqu)+str_position+'.txt'
		np.savetxt(file_name,np.c_[self.acq.time_line,self.acq.data], delimiter=' ')   # x,y,z equal sized 1D arrays

	def init_plot(self):
		plt.ion()
		self.fig, self.ax = plt.subplots()
		self.lineB, = self.ax.plot([], [], color='red', label='Channel B', zorder=1)
		self.lineA, = self.ax.plot([], [], color='blue', label='Channel A', zorder=2)
		self.ax.set_xlabel('Time (ns)')
		self.ax.set_ylabel('Amplitude (mV)')
		self.ax.legend()
		self.fig.show()

	def update_plot(self):
		self.lineA.set_data(self.acq.time_line, self.acq.data)
		self.lineB.set_data(self.acq.time_line, self.acq.dataB)
		self.ax.relim()
		self.ax.autoscale_view()
		self.fig.canvas.draw()
		self.fig.canvas.flush_events()
		plt.pause(0.001)


	def run_scan(self,ini_file,save_folder,ini_suffix=''):
		t1=time.time()
		self.define_current_date()
		self.create_result_folder(save_folder,ini_suffix)
		self.reload(ini_file)
		self.scope_init()
		self.init_scan(ini_file)
		self.save_config(ini_file)
		delay_mvt_acq=int(self.config['delaymvt_acq']['delayms'])*0.001
		self.init_plot()
		for ind in range(self.gridSize):
			self.myScan.moveForward()
			self.acq.running_block()
			position=self.motor.getCurrentPosition()
			time.sleep(delay_mvt_acq)
			self.trig_shot.gene_trig()
			self.acq.get_data()
			self.update_plot()
			self.save_data(ind,position)
			self.print_progress(ind,self.gridSize,t1,position)
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
		self.init_plot()
		for ind in range(0,Nshot):

			self.trig_shot.gene_trig()
			self.acq.get_data()
			self.update_plot()
			self.save_data(ind,position)
			self.print_progress(ind,Nshot,t1,position)
			time.sleep(delay_shot)
		t2=time.time()

		print(t2-t1)
		
		
	def disconnect_motor(self):
		self.motor.disconnect()
		

	def disconnect_scope(self):
		self.sc.close()
