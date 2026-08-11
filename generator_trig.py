# -*- coding: utf-8 -*-
"""
Created on Thu May 22 09:44:35 2025

@author: MathieuGUYOT
"""

import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc
import configparser
import scope_pico as pico
import time

class generator_trig:
    
	
	
	def __init__(self, scope):
		self.scope_pico = scope
		self.config = configparser.ConfigParser()
		self.config.read('config/config_scan.ini')

	def config_trig(self):
		# Output a square wave with peak-to-peak voltage of 2 V and frequency of 10 kHz
		# handle = chandle
		# offsetVoltage = -1000000
		# pkToPk = 1500000
		# waveType = ctypes.c_int16(1) = PS5000A_SQUARE
		# startFrequency = 10 kHz
		# stopFrequency = 10 kHz
		# increment = 0
		# dwellTime = 1
		# sweepType = ctypes.c_int16(1) = PS5000A_UP
		# operation = 0
		# shots = 0
		# sweeps = 0
		# triggerType = ctypes.c_int16(3) = PS5000A_SIGGEN_GATE_HIGH 
		# triggerSource = ctypes.c_int16(0) = PS5000A_SIGGEN_SOFT_TRIG 
		# extInThreshold = 0
		wavetype = ctypes.c_int32(1)
		sweepType = ctypes.c_int32(0)
		triggertype = ctypes.c_int32(0)
		triggerSource = ctypes.c_int32(4)
		print('config trig')
		print(triggerSource)
		
		self.scope_pico.status["setSigGenBuiltInV2"] = ps.ps5000aSetSigGenBuiltInV2(self.scope_pico.chandle, 1000000, 2000000, wavetype,12, 12, 0, 0, sweepType, 0,1, 0, triggertype, triggerSource, 0)
		assert_pico_ok(self.scope_pico.status["setSigGenBuiltInV2"])
		# Pauses the script to show signal
		ps.ps5000aSigGenSoftwareControl(self.scope_pico.chandle, 0);
		time.sleep(1)
		
		
	def gene_trig(self):
		ps.ps5000aSigGenSoftwareControl(self.scope_pico.chandle, 1);
		time.sleep(0.1)
		
		