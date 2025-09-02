# -*- coding: utf-8 -*-
"""
Created on Thu May 22 17:27:44 2025

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

class scan_data:
	"""
	Holds the settings needed to create a Move instance, and saved in the config file.
	Note: only attributes beginning with a lower case letter are saved (no capital, no _)
	"""

	def __init__(self,,grid,):
		self.grid=
		self.