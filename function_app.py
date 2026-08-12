# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 15:33:34 2026

@author: MathieuGUYOT
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile
from interface_scan import Ui_mainWindow  # import du fichier généré
import sys 
from process_scan import scanning
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
import datetime as date 
import os 
import shutil 
import numpy as np
from pathlib import Path
from tkinter import simpledialog

class f_app :
    
    def __init__(self,main_window):
        self.pr=scanning()
        self.sc=scope_pico()
        self.window=main_window
    
    def connect_motor_app(self):
        self.pr.axes_init()
        self.add_message( " connect motor .\n")
    
    def connect_scope_app(self):
        self.pr.scope_connect()
        self.add_message( "connect scope.\n")
    
    def Goto_originX_app(self):
        self.pr.origin_init(0)
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    
    def Goto_originY_app(self):
        self.pr.origin_init(1)
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    
    def Goto_originZ_app(self):
        self.pr.origin_init(2)
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    	
    def Goto_starting_pointX_app(self):
        self.pr.go_start(0,'config/config_scan.ini')
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    
    def Goto_starting_pointY_app(self):
        self.pr.go_start(1,'config/config_scan.ini')
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    
    def Goto_starting_pointZ_app(self):
        self.pr.go_start(2,'config/config_scan.ini')
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    def move_pointXp_app(self):
        step=float(self.window.ui.lineEdit_step_axesX.text())
        self.pr.move_step(0,'config/config_scan.ini',step)
        self.add_message( " start X.\n")
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    def move_pointXm_app(self):
        step=float(self.window.ui.lineEdit_step_axesX.text())
        self.pr.move_step(0,'config/config_scan.ini',-step)
        
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    
    def move_pointYp_app(self):
        step=float(self.window.ui.lineEdit_step_axesY.text())
        self.pr.move_step(1,'config/config_scan.ini',step)
       
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    def move_pointYm_app(self,orient):
        step=float(self.window.ui.lineEdit_step_axesY.text())
        self.pr.move_step(1,'config/config_scan.ini',-step)
  
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
    	
    def move_pointZp_app(self):
        step=float(self.window.ui.lineEdit_step_axesZ.text())
        self.pr.move_step(2,'config/config_scan.ini',step)
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
        
    def move_pointZm_app(self):
        step=float(self.window.ui.lineEdit_step_axesZ.text())
        self.pr.move_step(2,'config/config_scan.ini',-step)
        pos=self.pr.get_position()
        message = f"motor1 ={pos[0]} motor2 ={pos[1]} motor3= {pos[2]}"
        self.add_message(message)
        
    def load_axes(self):
        self.pr.reload('config/config_scan.ini')
        matice_dir=self.pr.read_axes()
        self.window.ui.lineEdit_coef_axesX_motor1.setText(str(matice_dir[0][0]))
        self.window.ui.lineEdit_coef_axesX_motor2.setText(str(matice_dir[0][1]))
        self.window.ui.lineEdit_coef_axesX_motor3.setText(str(matice_dir[0][2]))
        self. window.ui.lineEdit_coef_axesY_motor1.setText(str(matice_dir[1][0]))
        self.window.ui.lineEdit_coef_axesY_motor2.setText(str(matice_dir[1][1]))
        self.window.ui.lineEdit_coef_axesY_motor3.setText(str(matice_dir[1][2]))
        self.window.ui.lineEdit_coef_axesZ_motor1.setText(str(matice_dir[2][0]))
        self.window.ui.lineEdit_coef_axesZ_motor2.setText(str(matice_dir[2][1]))
        self.window.ui.lineEdit_coef_axesZ_motor3.setText(str(matice_dir[2][2]))
        norm = np.sqrt(sum(x**2 for x in matice_dir[0]))
        self.window.ui.lineEdit_step_axesX.setText(str(round(norm,2)))
        norm = np.sqrt(sum(x**2 for x in matice_dir[1]))
        self. window.ui.lineEdit_step_axesY.setText(str(round(norm,2)))
        norm = np.sqrt(sum(x**2 for x in matice_dir[2]))
        self.window.ui.lineEdit_step_axesZ.setText(str(round(norm,2)))
		
    	
    def change_ini(self):
        step=[0,0,0]
        step[0]=float(self.window.ui.lineEdit_step_axesX.text())
        step[1]=float(self.window.ui.lineEdit_step_axesY.text())
        step[2]=float(self.window.ui.lineEdit_step_axesZ.text())
        checked_axes=[]
        if self.window.ui.checkBox_axescan_X.isChecked(): checked_axes.append(0)
        if self.window.ui.checkBox_axescan_Y.isChecked(): checked_axes.append(1)
        if self.window.ui.checkBox_axescan_Z.isChecked(): checked_axes.append(2)
        if len(checked_axes)==1:
            scan_axe=checked_axes[0]
            nbr_point_scan=int(round(float(self.window.ui.lineEdit_scan_nbrpoint.text())))
            if nbr_point_scan% 2 == 0:nbr_point_scan=nbr_point_scan+1
            self.pr.change_ini('config/config_scan.ini',step,scan_axe,nbr_point_scan)
        elif len(checked_axes)==2:
            axis1,axis2=checked_axes[0],checked_axes[1]
            n1=int(round(float(self.window.ui.lineEdit_scan_nbrpoint.text())))
            n2=int(round(float(self.window.ui.lineEdit_scan_nbrpointY.text())))
            if n1 % 2 == 0: n1=n1+1
            if n2 % 2 == 0: n2=n2+1
            self.pr.change_ini_plane('config/config_scan.ini',step,axis1,axis2,n1,n2)
        else:
            self.add_message("Check exactly 1 axis (line scan) or 2 axes (plane scan).\n")
            return
        self.load_axes()
    	
    def add_message(self,texte):
    
        if texte:
           self.window.ui.listWidget.addItem(texte)
    
           if self.window.ui.listWidget.count() > 10:
                self.window.ui.listWidget.takeItem(0)
    
           

    def Run_scan_app(self):
        self.pr.run_scan('config/config_scan.ini','')
        #text_area.insert(tk.END, "Run Scan.\n")
    
    def run_sequence_scan(self):
        folder_sequence_save =simpledialog.askstring(title=" folder name",prompt="put the name of folder :")
        os.mkdir('measure/'+folder_sequence_save)
        if folder_sequence_save:
          
             print("folder creates :"+folder_sequence_save)
        else:
            print("no names")
        folder_sequence_save=folder_sequence_save+'/'
        #list_scan=list(Path(folder).glob("*.ini"))
        folder='sequence_scan'
        list_files=sorted(Path(folder).glob("*.ini"), key=lambda f: int(f.stem) if f.stem.isdigit() else f.stem)
        for f in list_files:
            
            print(f)
            self.pr.run_scan(f,folder_sequence_save,f.stem)
    
    def disconnect_motor_app(self):
        self.pr.disconnect_motor()
        self.add_message( " disconnect motor .\n")
        #text_area.insert(tk.END, "disconnect.\n")
		
    def disconnect_scope_app(self):
        self.pr.disconnect_scope()
        self.add_message( " disconnect scope .\n")
        #text_area.insert(tk.END, "disconnect.\n")
