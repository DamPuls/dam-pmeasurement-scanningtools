
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
		dir_matrice[0][0]=round(float(self.config['DirectionX']['dir_axes1']),4)
		dir_matrice[0][1]=round(float(self.config['DirectionX']['dir_axes2']),4)
		dir_matrice[0][2]=round(float(self.config['DirectionX']['dir_axes3']),4)

		dir_matrice[1][0]=round(float(self.config['DirectionY']['dir_axes1']),4)
		dir_matrice[1][1]=round(float(self.config['DirectionY']['dir_axes2']),4)
		dir_matrice[1][2]=round(float(self.config['DirectionY']['dir_axes3']),4)

		dir_matrice[2][0]=round(float(self.config['DirectionZ']['dir_axes1']),4)
		dir_matrice[2][1]=round(float(self.config['DirectionZ']['dir_axes2']),4)
		dir_matrice[2][2]=round(float(self.config['DirectionZ']['dir_axes3']),4)
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
		
		self.config['DirectionX']['dir_axes1']=str(round(dir_matrice[0][0]*step[0]/norm,4) )
		self.config['DirectionX']['dir_axes2']=str(round(dir_matrice[0][1]*step[0]/norm,4) )
		self.config['DirectionX']['dir_axes3']=str(round(dir_matrice[0][2]*step[0]/norm,4) )
		norm = np.sqrt(sum(x**2 for x in dir_matrice[1]))
		self.config['DirectionY']['dir_axes1']=str(round(dir_matrice[1][0]*step[1]/norm,4) )
		self.config['DirectionY']['dir_axes2']=str(round(dir_matrice[1][1]*step[1]/norm,4) )
		self.config['DirectionY']['dir_axes3']=str(round(dir_matrice[1][2]*step[1]/norm,4))
		norm = np.sqrt(sum(x**2 for x in dir_matrice[2]))
		self.config['DirectionZ']['dir_axes1']=str(round(dir_matrice[2][0]*step[2]/norm,4) )
		self.config['DirectionZ']['dir_axes2']=str(round(dir_matrice[2][1]*step[2]/norm,4) )
		self.config['DirectionZ']['dir_axes3']=str(round(dir_matrice[2][2]*step[2]/norm,4) )
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
			self.config[section]['dir_axes1']=str(round(dir_vec[0]*step[axis]/norm,4))
			self.config[section]['dir_axes2']=str(round(dir_vec[1]*step[axis]/norm,4))
			self.config[section]['dir_axes3']=str(round(dir_vec[2]*step[axis]/norm,4))

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
		self.folder_name_data_raw=self.folder_name+'/'+'data_raw'
		
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
		np.savetxt(file_name,np.c_[self.acq.time_line,self.acq.data], delimiter=' ')

	def save_raw_shots(self, ind_acqu, position, raw_list):
		"""Saves every individual (pre-averaging) acquisition for this point,
		in addition to the averaged signal save_data() already writes under
		data/ - so averaging for noise reduction never discards the
		underlying shots. Written to a separate data_raw/ folder (not
		data/), so the existing MATLAB and Python post-processing - which
		globs data/ind*.txt expecting exactly one file per point - is
		completely unaffected."""
		os.makedirs(self.folder_name_data_raw, exist_ok=True)
		str_position='_X_'+str(position[0])+'_Y_'+str(position[1])+'_Z_'+str(position[2])+'_'
		for shot_i, raw in enumerate(raw_list):
			file_name=self.folder_name_data_raw+'/'+'ind'+str(ind_acqu)+str_position+'shot'+str(shot_i)+'.txt'
			np.savetxt(file_name,np.c_[self.acq.time_line,raw], delimiter=' ')

	def acquire_averaged_with_display(self, delay_mvt_acq, ind, total, position, running_attr='scan_running'):
		"""Triggers and acquires config['averaging']['n_acq'] shots (default
		1 - no averaging) at the current point. Each individual shot is
		immediately drawn as a semi-transparent 'ghost' trace held on the
		plot alongside the others from this same point, and the running
		mean (of every shot acquired so far at this point) is shown as the
		usual bold Mean (raw)/Mean (windowed) trace - updated after every
		single shot, not just once per point, so the average visibly builds
		up live. Caller must call clear_shot_lines() first to start from a
		clean display for this point. delay_mvt_acq is applied before every
		single acquisition - both between points (motor-movement settle) and
		between repeated shots at the same point (averaging).

		running_attr names the instance flag (self.scan_running or
		self.shot_sequence_running) checked before every single shot, not
		just once per point - a large n_acq (e.g. 100) at 1.5s/shot can take
		minutes, and checking only between points meant a Stop click could
		take that long to actually register.

		Returns the list of individual raw shots acquired before any stop
		(for save_raw_shots()) - may be shorter than n_acq, even empty, if
		interrupted."""
		n_acq = self.config.getint('averaging', 'n_acq', fallback=1)
		krf = float(self.config['hydro']['krf'])
		temp = float(self.config['hydro']['temp'])
		raw_list = []
		for shot in range(n_acq):
			if not getattr(self, running_attr):
				break
			self.acq.running_block()
			time.sleep(delay_mvt_acq)
			self.trig_shot.gene_trig()
			self.acq.get_data()
			raw_list.append(self.acq.data.copy())

			dt_s = (self.acq.time_line[1] - self.acq.time_line[0]) * 1e-9
			_, shot_pressure_pa = pressure_convert.voltage_to_pressure(raw_list[-1], dt_s, krf, temp)
			time_us = self.acq.time_line / 1000.0
			line, = self.ax.plot(time_us, shot_pressure_pa/1e6, color='gray',
				alpha=0.35, linewidth=0.8, zorder=1)
			self.shot_lines.append(line)

			self.acq.data = np.mean(raw_list, axis=0)
			self.update_plot(ind, total, position)
		return raw_list

	def init_plot(self, scan_dims=None):
		"""scan_dims, when given, is (NX, NY, NZ) for the scan about to run -
		used to add a live-updating profile panel below the raw trace: a 1D
		line (MAX vs position) if exactly one axis has more than one point,
		a 2D colormap (MAX per grid cell) if exactly two do. Three or zero
		varying axes get no profile panel (a true 3D live view and the
		non-scan acquisition loops aren't in scope)."""
		# Close any leftover plot windows (e.g. a previous scan's result
		# window from scan_postprocess.plot_scan_result, which opens its own
		# figure) whenever a new acquisition task starts, instead of letting
		# them pile up on screen.
		plt.close('all')
		plt.ion()

		self.scan_profile_mode = None
		if scan_dims is not None:
			active = [i for i, n in enumerate(scan_dims) if n > 1]
			if len(active) == 1:
				self.scan_profile_mode = '1d'
				self._scan_axis_index = active[0]
				# The active grid axis (X/Y/Z "direction slot" in the ini)
				# doesn't necessarily correspond to the same-numbered
				# physical motor axis - DirectionX/Y/Z can point along any
				# combination of the 3 motors. Resolve which physical axis
				# actually moves, matching scan_postprocess.py's plot -
				# indexing straight into position[] by the grid axis was
				# reading a constant (non-moving) motor coordinate whenever
				# the ini's direction vectors aren't the plain identity.
				direction = np.array([float(self.config['Direction' + 'XYZ'[self._scan_axis_index]]
					['dir_axes{}'.format(i)]) for i in (1, 2, 3)])
				moving = np.where(direction != 0)[0]
				if len(moving) == 1:
					self._scan_physical_axis = int(moving[0])
					axis_label = '{} position (mm)'.format('XYZ'[self._scan_physical_axis])
				else:
					self._scan_physical_axis = None
					axis_label = 'Distance from start (mm)'
				self._scan_profile_origin = None
				self._scan_profile_positions = []
				self._scan_profile_values = []
			elif len(active) == 2:
				self.scan_profile_mode = '2d'
				self._scan_axes_2d = active
				n1, n2 = scan_dims[active[0]], scan_dims[active[1]]
				self._scan_grid_values = np.full((n2, n1), np.nan)
				increments = [self.myScan.grid.getIncrementX(),
					self.myScan.grid.getIncrementY(), self.myScan.grid.getIncrementZ()]
				self._scan_extent = [
					-0.5 * increments[active[0]], (n1 - 0.5) * increments[active[0]],
					-0.5 * increments[active[1]], (n2 - 0.5) * increments[active[1]]]

		with_profile = self.scan_profile_mode is not None
		self.fig = plt.figure(1, figsize=(11, 8.5) if with_profile else (11, 6.5))
		self.fig.clf()
		if with_profile:
			gs = self.fig.add_gridspec(3, 1, height_ratios=[0.6, 5.2, 4.2], hspace=0.32)
		else:
			gs = self.fig.add_gridspec(2, 1, height_ratios=[0.6, 6.9], hspace=0.1)
		self.ax_info = self.fig.add_subplot(gs[0])
		self.ax_info.axis('off')
		self.text_info = self.ax_info.text(0.0, 0.5, '', transform=self.ax_info.transAxes,
			va='center', ha='left', fontsize=11)

		self.ax = self.fig.add_subplot(gs[1])
		self.shot_lines = []
		self.ax.plot([], [], color='gray', alpha=0.35, linewidth=0.8, zorder=1, label='Individual shots')
		self.lineA, = self.ax.plot([], [], color='blue', label='Mean (raw)', zorder=2, alpha=0.5)
		self.line_sw, = self.ax.plot([], [], color='orange', label='Mean (windowed)', zorder=3)
		self.ax.set_xlabel('Time (µs)', fontsize=12)
		self.ax.set_ylabel('Pressure (MPa)', fontsize=12)
		self.ax.tick_params(axis='both', labelsize=11)
		self.ax.grid(True, which='major', axis='both', linewidth=0.5, alpha=0.6)
		self.ax.legend(fontsize=8, loc='upper right')

		self.ax_profile = None
		if self.scan_profile_mode == '1d':
			self.ax_profile = self.fig.add_subplot(gs[2])
			self.line_profile, = self.ax_profile.plot([], [], color='green', marker='o', markersize=4)
			self.ax_profile.set_xlabel(axis_label, fontsize=12)
			self.ax_profile.set_ylabel('MAX pressure (MPa)', fontsize=12)
			self.ax_profile.tick_params(axis='both', labelsize=11)
			self.ax_profile.grid(True, which='major', axis='both', linewidth=0.5, alpha=0.6)
		elif self.scan_profile_mode == '2d':
			self.ax_profile = self.fig.add_subplot(gs[2])
			self.im_profile = self.ax_profile.imshow(
				self._scan_grid_values, origin='lower', aspect='auto',
				extent=self._scan_extent, cmap='viridis')
			self.fig.colorbar(self.im_profile, ax=self.ax_profile, label='MAX pressure (MPa)')
			ax1_letter, ax2_letter = (['X', 'Y', 'Z'][i] for i in self._scan_axes_2d)
			self.ax_profile.set_xlabel('{} position (mm)'.format(ax1_letter), fontsize=12)
			self.ax_profile.set_ylabel('{} position (mm)'.format(ax2_letter), fontsize=12)
			self.ax_profile.tick_params(axis='both', labelsize=11)

		# matplotlib reserves a fixed top/bottom margin by default,
		# regardless of the gridspec height_ratios above - that margin grows
		# in absolute size as the figure gets taller, wasting the space just
		# freed up there. Reclaim it explicitly instead.
		self.fig.subplots_adjust(top=0.95, bottom=0.08, left=0.08, right=0.97)

		self.fig.show()
		self.fig.canvas.draw()
		self.plot_background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

	def clear_shot_lines(self):
		"""Removes the held 'ghost' traces (individual averaging shots) left
		over from the previous point. Forces a full redraw immediately,
		since blitting only ever draws artists on top of a saved background
		bitmap - it can't erase something that bitmap already has baked in,
		so a removed line would otherwise stay visible as stale pixels."""
		for line in self.shot_lines:
			line.remove()
		self.shot_lines = []
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
		suffix = '' if detected else ' (no SW detected - showing raw max)'
		info_parts.append('MAX (windowed): {:.2f} MPa{}'.format(peak_mpa, suffix))
		if position is not None:
			info_parts.append('X={:.2f}  Y={:.2f}  Z={:.2f}'.format(*position))
		if ind is not None and total is not None:
			info_parts.append('Shot {}/{}'.format(ind + 1, total))
		elif ind is not None:
			info_parts.append('Acquisition #{}'.format(ind + 1))
		self.text_info.set_text('   |   '.join(info_parts))

		old_xlim = self.ax.get_xlim()
		old_ylim = self.ax.get_ylim()
		self.ax.relim()
		self.ax.autoscale_view()

		profile_changed = False
		if self.scan_profile_mode == '1d' and position is not None:
			if self._scan_physical_axis is not None:
				x_value = position[self._scan_physical_axis]
			else:
				# Direction vector isn't a single physical axis (a diagonal
				# scan) - fall back to straight-line distance from the first
				# point, matching scan_postprocess.py's own fallback.
				# Motor_3Bop.getCurrentPosition() returns its internal
				# _current_position object directly (not a copy) - storing
				# that reference here would mean this "origin" silently
				# mutates right along with every later position, making
				# every point plot at the same X (always ~0 distance from
				# "itself"). Store a real copy instead.
				if self._scan_profile_origin is None:
					self._scan_profile_origin = list(position)
				x_value = float(np.sqrt(sum(
					(position[k] - self._scan_profile_origin[k]) ** 2 for k in range(3))))
			self._scan_profile_positions.append(x_value)
			self._scan_profile_values.append(peak_mpa)
			self.line_profile.set_data(self._scan_profile_positions, self._scan_profile_values)
			old_pxlim = self.ax_profile.get_xlim()
			old_pylim = self.ax_profile.get_ylim()
			self.ax_profile.relim()
			self.ax_profile.autoscale_view()
			profile_changed = (self.ax_profile.get_xlim() != old_pxlim) or (self.ax_profile.get_ylim() != old_pylim)
		elif self.scan_profile_mode == '2d':
			grid_index = self.myScan.getPositionIndex()
			i1 = grid_index[self._scan_axes_2d[0]]
			i2 = grid_index[self._scan_axes_2d[1]]
			self._scan_grid_values[i2, i1] = peak_mpa
			self.im_profile.set_data(self._scan_grid_values)
			finite_vals = self._scan_grid_values[np.isfinite(self._scan_grid_values)]
			if finite_vals.size:
				# Percentile clip instead of plain min/max - cheap (one
				# np.percentile call over at most a few thousand points) and
				# stops a single spurious/glitched value from blowing out
				# the whole color scale. Falls back to plain min/max with
				# too few points for percentiles to mean anything.
				if finite_vals.size >= 10:
					vmin, vmax = np.percentile(finite_vals, [1, 99])
				else:
					vmin, vmax = np.min(finite_vals), np.max(finite_vals)
				if vmax <= vmin:
					vmax = vmin + 1e-9
				self.im_profile.set_clim(vmin=float(vmin), vmax=float(vmax))
			# imshow's colorbar ticks only refresh on a full canvas draw, not
			# a blit of the image artist alone - just always redraw fully
			# here rather than tracking that separately.
			profile_changed = True

		if self.ax.get_xlim() != old_xlim or self.ax.get_ylim() != old_ylim or profile_changed:
			# axis limits changed - needs a full redraw to refresh ticks/background
			self.fig.canvas.draw()
			self.plot_background = self.fig.canvas.copy_from_bbox(self.fig.bbox)
		else:
			# steady state - just blit the artists instead of redrawing everything
			self.fig.canvas.restore_region(self.plot_background)
			for line in self.shot_lines:
				self.ax.draw_artist(line)
			self.ax.draw_artist(self.lineA)
			self.ax.draw_artist(self.line_sw)
			self.ax_info.draw_artist(self.text_info)
			if self.scan_profile_mode == '1d':
				self.ax_profile.draw_artist(self.line_profile)
			self.fig.canvas.blit(self.fig.bbox)
		# flush_events() alone pumps the Qt event loop (redraw + button
		# clicks) without re-raising/re-focusing the plot window the way
		# plt.pause() does internally (it calls show(block=False) every
		# time) - that repeated re-focus was stealing focus from the main
		# app window on every refresh, blocking clicks on it mid-scan.
		self.fig.canvas.flush_events()


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
		self.init_plot(scan_dims=(self.myScan.grid.NX, self.myScan.grid.NY, self.myScan.grid.NZ))
		self.scan_running = True
		for ind in range(self.gridSize):
			if not self.scan_running:
				break
			loop_t0 = time.time()
			self.myScan.moveForward()
			position=self.motor.getCurrentPosition()
			self.clear_shot_lines()
			raw_list = self.acquire_averaged_with_display(delay_mvt_acq, ind, self.gridSize, position, 'scan_running')
			if not raw_list:
				break
			self.save_data(ind,position)
			if len(raw_list) > 1:
				self.save_raw_shots(ind, position, raw_list)
			self.print_progress(ind,self.gridSize,t1,position)
			print('  loop time: {:.2f}s'.format(time.time() - loop_t0))
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
		delay_mvt_acq=int(self.config['delaymvt_acq']['delayms'])*0.001
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

			self.clear_shot_lines()
			raw_list = self.acquire_averaged_with_display(delay_mvt_acq, ind, Nshot, position, 'shot_sequence_running')
			if not raw_list:
				break
			self.save_data(ind,position)
			if len(raw_list) > 1:
				self.save_raw_shots(ind, position, raw_list)
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
