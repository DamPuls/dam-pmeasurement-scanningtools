# -*- coding: utf-8 -*-
"""
Created on Fri May 23 12:05:39 2025

@author: MathieuGUYOT
"""
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
pr=scanning()
sc=scope_pico()
pr.scope_init()
pr.axes_init()
pr.run_scan()

