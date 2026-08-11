# -*- coding: utf-8 -*-
"""
Created on Tue May 20 09:16:19 2025

@author: MathieuGUYOT
"""
import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc
import configparser


class scope_pico:

    def __init__(self):
        self.status = {}
        self.chandle = ctypes.c_int16()
        self.config = configparser.ConfigParser()
        self.config.read('config/config_scan.ini')
  
    def reload(self,file_ini):
        self.config.read(file_ini)
		
    def connect(self):
        self.resolution = ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"]
        # Returns handle to chandle for use in future API functions
        self.status["openunit"] = ps.ps5000aOpenUnit(
            ctypes.byref(self.chandle), None, self.resolution)
        try:
            assert_pico_ok(self.status["openunit"])
        except:  # PicoNotOkError:

            powerStatus = self.status["openunit"]

            if powerStatus == 286:
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(
                    self.chandle, powerStatus)
            elif powerStatus == 282:
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(
                    self.chandle, powerStatus)
            else:
                raise

            assert_pico_ok(self.status["changePowerSource"])

    def config_channel(self):
        # Set up channel A
        # handle = chandle
        channel = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"]
        enabled = 1
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        cr = float(self.config['Channel']['ChannelA_range'])
        print(cr)
        print("PS5000A_" + str(int(cr)) + "V")
        if(cr < 1):
            self.chARange = ps.PS5000A_RANGE["PS5000A_" +
                                             str(int(cr*1000)) + "MV"]
        else:
            self.chARange = ps.PS5000A_RANGE["PS5000A_" + str(int(cr)) + "V"]
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        ##print(ps.PS5000A_RANGE["PS5000A_" + str(int(cr)) + "V"] )
        self. status["setChA"] = ps.ps5000aSetChannel(
            self.chandle, channel, 1, coupling_type, self.chARange, 0)
        assert_pico_ok(self.status["setChA"])
        print('channel A config ')

        # Set up channel B
        # handle = chandle
        channel = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"]
        enabled = 1
        # coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        cr = float(self.config['Channel']['ChannelB_range'])
        if cr < 1.0:
            self.chBRange = ps.PS5000A_RANGE["PS5000A_" +
                                             str(int(cr*1000)) + "MV"]
        else:
            self.chBRange = ps.PS5000A_RANGE["PS5000A_" + str(int(cr)) + "V"]
        print(self.chBRange)
        # analogue offset = 0 V
        self.status["setChB"] = ps.ps5000aSetChannel(
            self.chandle, channel,  enabled, coupling_type, self.chBRange, 0)
        assert_pico_ok(self.status["setChB"])

        #
        self.maxADC = ctypes.c_int16()
        self.status["maximumValue"] = ps.ps5000aMaximumValue(
            self.chandle, ctypes.byref(self.maxADC))
        assert_pico_ok(self.status["maximumValue"])
        print('channel config ')

    def config_trigger(self):
        type_trig = int(self.config['Trigger']['bool_trig_detection'])
        print(type_trig)
        if(type_trig == 1):
            # Set up simple trigger
            # handle = chandle
            # enabled = 1
            source = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"]
            threshold = int(mV2adc(
                float(self.config['Trigger']['ChannelA_threshold']), self.chARange, self.maxADC))
            print('seuil')
            print(float(self.config['Trigger']['ChannelA_threshold']))
            # direction = PS5000A_RISING = 2
            # delay = 0 s
            # auto Trigger = 1000 ms
            v_auto_trig=float(self.config['TIMEOUT']['valuemicros'])*0.001
            print('auto_trig')
            print(v_auto_trig)
            print(float(self.config['Trigger']['ChannelA_threshold']))
            self. status["trigger"] = ps.ps5000aSetSimpleTrigger(
                self.chandle, 1, source, threshold, int(self.config['Trigger']['ChannelA_direction']), 0,int(v_auto_trig))
            assert_pico_ok(self.status["trigger"])
        elif(type_trig == 2):

            adcTriggerLevelA = int(mV2adc(
                float(self.config['Trigger']['ChannelA_threshold']), self.chARange, self.maxADC))
            adcTriggerLevelB = int(mV2adc(
                float(self.config['Trigger']['ChannelB_threshold']), self.chBRange, self.maxADC))

            triggerProperties = (
                ps.PS5000A_TRIGGER_CHANNEL_PROPERTIES_V2 * 2)()
            triggerProperties[0] = ps.PS5000A_TRIGGER_CHANNEL_PROPERTIES_V2(adcTriggerLevelA,
                                                                            10,
                                                                            0,
                                                                            10,
                                                                            ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"])

            triggerProperties[1] = ps.PS5000A_TRIGGER_CHANNEL_PROPERTIES_V2(adcTriggerLevelB,
                                                                            10,
                                                                            0,
                                                                            10,
                                                                            ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"])

            self.status["setTriggerChannelPropertiesV2"] = ps.ps5000aSetTriggerChannelPropertiesV2(
                self.chandle, ctypes.byref(triggerProperties), 2, 0)
            assert_pico_ok(self.status["setTriggerChannelPropertiesV2"])

            ps.ps5000aSetAutoTriggerMicroSeconds(self.chandle,int(self.config['TIMEOUT']['valuemicros']))
            ##
            # LOGICAL OPERATION

            triggerConditionsA = ps.PS5000A_CONDITION(ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
                                                      ps.PS5000A_TRIGGER_STATE["PS5000A_CONDITION_TRUE"])
            triggerConditionsB = ps.PS5000A_CONDITION(ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"],
                                                      ps.PS5000A_TRIGGER_STATE["PS5000A_CONDITION_TRUE"])
            clear = 1
            add = 2

            self.status["setTriggerChannelConditionsV2_A"] = ps.ps5000aSetTriggerChannelConditionsV2(
                self.chandle, ctypes.byref(triggerConditionsA), 1, (add))
            assert_pico_ok(self.status["setTriggerChannelConditionsV2_A"])
            self.status["setTriggerChannelConditionsV2_B"] = ps.ps5000aSetTriggerChannelConditionsV2(
                self.chandle, ctypes.byref(triggerConditionsB), 1, (add))
            assert_pico_ok(self.status["setTriggerChannelConditionsV2_B"])
            ##
            # DIRECTION

            triggerDirections = (ps.PS5000A_DIRECTION * 2)()

            triggerDirections[0] = ps.PS5000A_DIRECTION(ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
                                                        int(self.config['Trigger']
                                                            ['ChannelA_direction']),
                                                        ps.PS5000A_THRESHOLD_MODE["PS5000A_LEVEL"])
            triggerDirections[1] = ps.PS5000A_DIRECTION(ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"],
                                                        int(self.config['Trigger']
                                                            ['ChannelB_direction']),
                                                        ps.PS5000A_THRESHOLD_MODE["PS5000A_LEVEL"])

            self.status["setTriggerChannelDirections"] = ps.ps5000aSetTriggerChannelDirectionsV2(
                self.chandle, ctypes.byref(triggerDirections), 2)
            assert_pico_ok(self.status["setTriggerChannelDirections"])
        elif(type_trig == 3):
            # Set up simple trigger on Channel B only, Channel A is left unarmed
            source = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"]
            threshold = int(mV2adc(
                float(self.config['Trigger']['ChannelB_threshold']), self.chBRange, self.maxADC))
            print('seuil')
            print(float(self.config['Trigger']['ChannelB_threshold']))
            v_auto_trig=float(self.config['TIMEOUT']['valuemicros'])*0.001
            print('auto_trig')
            print(v_auto_trig)
            self. status["trigger"] = ps.ps5000aSetSimpleTrigger(
                self.chandle, 1, source, threshold, int(self.config['Trigger']['ChannelB_direction']), 0,int(v_auto_trig))
            assert_pico_ok(self.status["trigger"])

    def close(self):
        # Stop the scope
        # handle = chandle
        self.status["stop"] = ps.ps5000aStop(self.chandle)
        assert_pico_ok(self.status["stop"])

        # Close unit Disconnect the scope
        # handle = chandle
        self.status["close"] = ps.ps5000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])
