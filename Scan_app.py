# -*- coding: utf-8 -*-
"""
Created on Mon May 26 12:13:06 2025

@author: MathieuGUYOT
"""
import sys 
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
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
pr=scanning()
sc=scope_pico()
# Création de la fenêtre principale
root = tk.Tk()
root.title("Scanning interface ")
root.geometry("900x600")

# Zone de texte
text_area = tk.Text(root, height=10, width=70)
file_name_area = tk.Text(root, height=1, width=20)

text_area.pack(pady=10)

# Fonctions reliées aux boutons
def connect_motor_app():
    pr.axes_init()
    text_area.insert(tk.END, " connect motor .\n")

def connect_scope_app():
    pr.scope_connect()
    text_area.insert(tk.END, "connect scope.\n")

def Goto_originX_app():
    pr.origin_init(0)
    text_area.insert(tk.END, " origine X.\n")

def Goto_originY_app():
    pr.origin_init(1)
    text_area.insert(tk.END, " origine Y.\n")

def Goto_originZ_app():
    pr.origin_init(2)
    text_area.insert(tk.END, "origine Z.\n")
	
def Goto_starting_pointX_app():
    pr.go_start(0,'config/config_scan.ini')
    text_area.insert(tk.END, " start X.\n")

def Goto_starting_pointY_app():
    pr.go_start(1,'config/config_scan.ini')
    text_area.insert(tk.END, " start Y.\n")

def Goto_starting_pointZ_app():
    pr.go_start(2,'config/config_scan.ini')
    text_area.insert(tk.END, "start Z.\n")

def Run_scan_app():
    pr.run_scan('config/config_scan.ini','')
    text_area.insert(tk.END, "Run Scan.\n")

def Run_sequence_shot_app():
    pr.run_shot_sequence()
    text_area.insert(tk.END, "Run Scan.\n")

def disconnect_app():
    pr.disconnect()
    text_area.insert(tk.END, "disconnect.\n")


def run_sequence_scan():
    folder_sequence_save =simpledialog.askstring(title=" folder name",prompt="put the name of folder :")
    os.mkdir('measure/'+folder_sequence_save)
    if folder_sequence_save:
      
         print("folder creates :"+folder_sequence_save)
    else:
        print("no names")
    folder_sequence_save=folder_sequence_save+'/'
    #list_scan=list(Path(folder).glob("*.ini"))
    folder='sequence_scan'
    list_files=list(Path(folder).glob("*.ini"))
    for f in list_files:
        
        print(f)
        pr.run_scan(f,folder_sequence_save)

# Création des boutons
Connect_motor = tk.Button(root, text="Connect motor", command=connect_motor_app)
Connect_scope = tk.Button(root, text=" Connect scope", command=connect_scope_app)


Origin_X = tk.Button(root, text="Origin_X ", command=Goto_originX_app)
Origin_Y = tk.Button(root, text="Origin_Y", command=Goto_originY_app)
Origin_Z = tk.Button(root, text="Origin_Z", command=Goto_originZ_app)
start_X = tk.Button(root, text="Start_X", command=Goto_starting_pointX_app)
start_Y = tk.Button(root, text="Start_Y", command=Goto_starting_pointY_app)
start_Z = tk.Button(root, text="Start_Z", command=Goto_starting_pointZ_app)

Start_Scan = tk.Button(root, text="Start Scan", command=Run_scan_app)
disconnect= tk.Button(root, text="disconnect", command=disconnect_app)
sequence_scan= tk.Button(root, text="sequence_scan", command=run_sequence_scan)

# Placement des boutons



Connect_motor.pack(padx=1,pady=1)
Connect_scope.pack(padx=1,pady=1)

Origin_X.pack(padx=2,pady=1)
Origin_Y.pack(padx=2,pady=1)
Origin_Z.pack(padx=2,pady=1)

start_X.pack(padx=3,pady=1)
start_Y.pack(padx=3,pady=1)
start_Z.pack(padx=3,pady=1)

Start_Scan.pack(padx=1,pady=1)
disconnect.pack(padx=1,pady=1)

sequence_scan.pack(padx=1,pady=1)
file_name_area.pack(padx=1,pady=1)
# Lancement de l'application
root.mainloop()

