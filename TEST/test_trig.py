# -*- coding: utf-8 -*-
"""
Created on Wed May 28 08:48:51 2025

@author: MathieuGUYOT
"""

import time
from scope_pico import scope_pico 
from acquisition import acquisition_pico 
from generator_trig import generator_trig  
import matplotlib.pyplot as plt
text="toto"
sc=scope_pico()
sc.connect()

acq=acquisition_pico(sc)
trig_shot=generator_trig(sc)
trig_shot.config_trig()
sc.config_channel()
acq.config_acquisition()
sc.config_trigger()
time.sleep(2)
for ind in range(1,4):
	trig_shot.gene_trig()
	time.sleep(0.2)


sc.close()


