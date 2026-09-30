
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
import pressure_convert
from sw_detect_py import detect_sw
import scan_postprocess
import matplotlib.pyplot as plt

# Same defaults as the MATLAB pipeline (f_process_scan_2D.m) and focus_search.py
SW_F_SIGNAL = 2e5      # expected SW signal main frequency (Hz)
SW_THRESHOLD_PA = 3e6  # detection threshold (Pa) = 3 MPa
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
		self.acquisition_running = False
		self.scan_running = False
		self.shot_sequence_running = False

	    
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

		if getattr(self, 'seq_index', None) is not None and getattr(self, 'seq_total', None) is not None:
			points_done_seq = (self.seq_points_before or 0) + (ind + 1)
			elapsed_seq = time.time() - self.seq_start_time
			remaining_seq = (elapsed_seq / points_done_seq) * (self.seq_total_points - points_done_seq)
			print("[{}/{}] [{}/{}] remaining(file)~{} remaining(seq)~{} | X={:.4f} Y={:.4f} Z={:.4f}".format(
				self.seq_index, self.seq_total, ind + 1, total, fmt(remaining), fmt(remaining_seq),
				position[0], position[1], position[2]))
		else:
			print("[{}/{}] elapsed {} / remaining ~{} | X={:.4f} Y={:.4f} Z={:.4f}".format(
				ind + 1, total, fmt(elapsed), fmt(remaining), position[0], position[1], position[2]))

	def save_data(self, ind_acqu,position ):
		str_position='_X_'+str(position[0])+'_Y_'+str(position[1])+'_Z_'+str(position[2])+'_'
		file_name=self.folder_name_data+'/'+'ind'+str(ind_acqu)+str_position+'.txt'
		np.savetxt(file_name,np.c_[self.acq.time_line,self.acq.data], delimiter=' ')   # x,y,z equal sized 1D arrays

	def init_plot(self):
		plt.ion()
		self.fig = plt.figure(1, figsize=(11, 6))
		self.fig.clf()
		gs = self.fig.add_gridspec(2, 1, height_ratios=[1, 6], hspace=0.08)
		self.ax_info = self.fig.add_subplot(gs[0])
		self.ax_info.axis('off')
		self.text_info = self.ax_info.text(0.0, 0.5, '', transform=self.ax_info.transAxes,
			va='center', ha='left', fontsize=11)

		self.ax = self.fig.add_subplot(gs[1])
		self.lineA, = self.ax.plot([], [], color='blue', label='Raw', zorder=2, alpha=0.5)
		self.line_sw, = self.ax.plot([], [], color='orange', label='Windowed', zorder=3)
		self.ax.set_xlabel('Time (µs)', fontsize=12)
		self.ax.set_ylabel('Pressure (MPa)', fontsize=12)
		self.ax.tick_params(axis='both', labelsize=11)
		self.ax.grid(True, which='major', axis='both', linewidth=0.5, alpha=0.6)
		self.ax.legend(fontsize=8, loc='upper right')
		self.fig.show()
		self.fig.canvas.draw()
		self.plot_background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

	def update_plot(self, ind=None, total=None, position=None):
		dt_s = (self.acq.time_line[1] - self.acq.time_line[0]) * 1e-9
		krf = float(self.config['hydro']['krf'])
		temp = float(self.config['hydro']['temp'])
		_, pressure_pa = pressure_convert.voltage_to_pressure(self.acq.data, dt_s, krf, temp)

		sw_pa, detected = detect_sw(pressure_pa, dt_s, SW_F_SIGNAL, SW_THRESHOLD_PA)
		peak_mpa = (np.max(sw_pa) if detected else np.max(pressure_pa)) / 1e6

		time_us = self.acq.time_line / 1000.0
		self.lineA.set_data(time_us, pressure_pa / 1e6)
		self.line_sw.set_data(time_us, sw_pa / 1e6)

		info_parts = []
		if ind is not None and total is not None:
			info_parts.append('Shot {}/{}'.format(ind + 1, total))
		elif ind is not None:
			info_parts.append('Acquisition #{}'.format(ind + 1))
		if position is not None:
			info_parts.append('X={:.2f}  Y={:.2f}  Z={:.2f}'.format(*position))
		suffix = '' if detected else ' (no SW detected - showing raw max)'
		info_parts.append('MAX (windowed): {:.2f} MPa{}'.format(peak_mpa, suffix))
		self.text_info.set_text('   |   '.join(info_parts))

		old_xlim = self.ax.get_xlim()
		old_ylim = self.ax.get_ylim()
		self.ax.relim()
		self.ax.autoscale_view()
		if self.ax.get_xlim() != old_xlim or self.ax.get_ylim() != old_ylim:
			# axis limits changed - needs a full redraw to refresh ticks/background
			self.fig.canvas.draw()
			self.plot_background = self.fig.canvas.copy_from_bbox(self.fig.bbox)
		else:
			# steady state - just blit the artists instead of redrawing everything
			self.fig.canvas.restore_region(self.plot_background)
			self.ax.draw_artist(self.lineA)
			self.ax.draw_artist(self.line_sw)
			self.ax_info.draw_artist(self.text_info)
			self.fig.canvas.blit(self.fig.bbox)
		self.fig.canvas.flush_events()
		plt.pause(0.001)


	def run_scan(self,ini_file,save_folder,ini_suffix='',close_plot_after=False,seq_index=None,seq_total=None,seq_total_points=None,seq_points_before=None,seq_start_time=None):
		t1=time.time()
		self.seq_index = seq_index
		self.seq_total = seq_total
		self.seq_total_points = seq_total_points
		self.seq_points_before = seq_points_before
		self.seq_start_time = seq_start_time
		self.define_current_date()
		self.create_result_folder(save_folder,ini_suffix)
		self.reload(ini_file)
		self.scope_init()
		self.init_scan(ini_file)
		self.save_config(ini_file)
		delay_mvt_acq=int(self.config['delaymvt_acq']['delayms'])*0.001
		self.init_plot()
		throttle_plot = self.gridSize > 100
		self.scan_running = True
		for ind in range(self.gridSize):
			if not self.scan_running:
				break
			self.myScan.moveForward()
			self.acq.running_block()
			position=self.motor.getCurrentPosition()
			time.sleep(delay_mvt_acq)
			self.trig_shot.gene_trig()
			self.acq.get_data()
			if (not throttle_plot) or (ind % 5 == 0) or (ind == self.gridSize - 1):
				self.update_plot(ind, self.gridSize, position)
			self.save_data(ind,position)
			self.print_progress(ind,self.gridSize,t1,position)
		t2=time.time()
		print('duration acquisition ')
		print (t2-t1)
		try:
			scan_result = scan_postprocess.process_1d_scan(self.folder_name)
			if scan_result is not None:
				scan_postprocess.plot_scan_result(
					scan_result, save_path=self.folder_name+'/scan_result.png')
		except Exception as e:
			print('scan post-processing failed (raw scan data is unaffected): {}'.format(e))
		if close_plot_after:
			plt.close(self.fig)
	def run_shot_sequence(self):
		self.reload('config/config_scan.ini')
		self.scope_init()
		self.define_current_date()
		self.create_result_folder('')
		delay_shot=int(self.config['sequence_shot']['delayshot'])*0.001
		# Driven by the Start/Stop toggle rather than the ini's number_shot -
		# runs up to this many shots and stops early on a Stop click.
		Nshot=100
		t1=time.time()
		position=self.motor.getCurrentPosition()
		self.init_plot()
		self.shot_sequence_running = True
		for ind in range(0,Nshot):
			if not self.shot_sequence_running:
				break

			self.acq.running_block()
			self.trig_shot.gene_trig()
			self.acq.get_data()
			self.update_plot(ind, Nshot, position)
			self.save_data(ind,position)
			self.print_progress(ind,Nshot,t1,position)
			time.sleep(delay_shot)
		t2=time.time()

		print(t2-t1)

	def run_acquisition_loop(self):
		"""Free-running acquisition with no motor movement - for live
		viewing/alignment, not a recorded measurement (no folder/save_data).
		Runs until self.acquisition_running is set False (the Start/Stop
		toggle button in the UI flips it via a re-entrant call, the same
		way the scan loop already stays responsive: update_plot()'s
		flush_events() lets Qt process that button's next click mid-loop)."""
		self.reload('config/config_scan.ini')
		self.scope_init()
		self.acq.running_block()
		self.init_plot()
		ind = 0
		while self.acquisition_running:
			self.trig_shot.gene_trig()
			self.acq.get_data()
			position = self.motor.getCurrentPosition()
			self.update_plot(ind, None, position)
			ind += 1

	def disconnect_motor(self):
		self.motor.disconnect()
		

	def disconnect_scope(self):
		self.sc.close()
