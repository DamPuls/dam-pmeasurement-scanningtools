# -*- coding: utf-8 -*-
"""
Created on Tue May 20 11:52:35 2025

@author: MathieuGUYOT
"""
import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc
import configparser
import scope_pico as pico


class acquisition_pico:
    def __init__(self, scope):
        self.scope_pico = scope
        self.config = configparser.ConfigParser()
        self.config.read('config/config_scan.ini')
    def reload(self):
        self.config.read('config/config_scan.ini')

    def config_acquisition(self):
        # Setting the number of sample to be collected
        self.preTriggerSamples = int(
            self.config['Samples']['preTriggerSamples'])
        self.postTriggerSamples = int(
            self.config['Samples']['postTriggerSamples'])
        self.maxsamples = self.preTriggerSamples + self.postTriggerSamples

# Handle = chandle
        self.timebase = int(self.config['Samples']['data_base'])
        # Nosample = maxsamples
        # TimeIntervalNanoseconds = ctypes.byref(timeIntervalns)
        # MaxSamples = ctypes.byref(returnedMaxSamples)
        # Segement index = 0
        self.timeIntervalns = ctypes.c_float()
		
        ##ps.ps5000aSetAutoTriggerMicroSeconds(self.scope_pico.chandle,int(self.config['TIMEOUT']['valuemicros']))
  
		
        returnedMaxSamples = ctypes.c_int16()
        self.scope_pico.status["GetTimebase"] = ps.ps5000aGetTimebase2(
            self.scope_pico.chandle, self.timebase, self.maxsamples, ctypes.byref(self.timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
        assert_pico_ok(self.scope_pico.status["GetTimebase"])
        self.time_line = 0
        print(' timeintervals=')
        print(str(self.timeIntervalns.value)+'ns')
		    
        frequency=(1/self.timeIntervalns.value)*1e6
        print('acquisition frequency')
        print(str(frequency)+'MHz')

    def running_block(self):

        self.data = 0
        # Creates a overlow location for data
        overflow = ctypes.c_int16()
        # Creates converted types maxsamples
        cmaxSamples = ctypes.c_int32(self.maxsamples)
        # Handle = Chandle
        # nSegments = 10
        # nMaxSamples = ctypes.byref(cmaxSamples)
        

        self.scope_pico.status["MemorySegments"] = ps.ps5000aMemorySegments(
            self.scope_pico.chandle, 1, ctypes.byref(cmaxSamples))
        assert_pico_ok(self.scope_pico.status["MemorySegments"])

        # sets number of captures
        self.scope_pico.status["SetNoOfCaptures"] = ps.ps5000aSetNoOfCaptures(self.scope_pico.chandle, 1)
        assert_pico_ok(self.scope_pico.status["SetNoOfCaptures"])

        self.scope_pico.status["runblock"] = ps.ps5000aRunBlock(
            self.scope_pico.chandle, self.preTriggerSamples, self.postTriggerSamples, self.timebase, None, 0, None, None)
        assert_pico_ok(self.scope_pico.status["runblock"])

    def get_data(self):
        # Create buffers ready for assigning pointers for data collection

        bufferAMax = (ctypes.c_int16 * self.maxsamples)()
        # used for downsampling which isn't in the scope of this example
        bufferAMin = (ctypes.c_int16 * self.maxsamples)()
        # Setting the data buffer location for data collection from channel A
        # Handle = Chandle
        self.source = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"]
        # Buffer max = ctypes.byref(bufferAMax)
        # Buffer min = ctypes.byref(bufferAMin)
        # Buffer length = maxsamples
        # Segment index = 0
        # Ratio mode = ps5000a_Ratio_Mode_None = 0
        self.scope_pico.status["SetDataBuffers"] = ps.ps5000aSetDataBuffers(self.scope_pico.chandle, self.source, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), self.maxsamples, 0, 0)
        assert_pico_ok(self.scope_pico.status["SetDataBuffers"])
        # Creates a overlow location for data
        overflow = (ctypes.c_int16 * 10)()
        # Creates converted types maxsamples
        cmaxSamples = ctypes.c_int32(self.maxsamples)

        # Checks data collection to finish the capture
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.scope_pico.status["isReady"] = ps.ps5000aIsReady(self.scope_pico.chandle, ctypes.byref(ready))
        self.scope_pico.status["GetValuesBulk"] = ps.ps5000aGetValuesBulk( self.scope_pico.chandle, ctypes.byref(cmaxSamples), 0, 0, 0, 0, ctypes.byref(overflow))
        assert_pico_ok(self.scope_pico.status["GetValuesBulk"])

        self.data = adc2mV(bufferAMax, self.scope_pico.chARange, self.scope_pico.maxADC)
        # Creates the time data
        self.time_line = np.linspace(0, (cmaxSamples.value) * self.timeIntervalns.value, cmaxSamples.value)

      	
    def save_data(self):
        file_name='test.txt'
        np.savetxt(file_name,np.c_[self.time_line,self.data], delimiter=' ')   # x,y,z equal sized 1D arrays
        
