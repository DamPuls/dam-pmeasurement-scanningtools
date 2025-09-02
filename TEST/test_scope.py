# -*- coding: utf-8 -*-
"""
Created on Tue May 20 10:47:18 2025

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

sc.config_channel()
sc.config_trigger()
trig_shot.config_trig()
acq.config_acquisition()

t1=time.time()
acq.running_block()
for ind in range(1,2):
	time.sleep(0.2)
	trig_shot.gene_trig()
	time.sleep(1)
	acq.get_data()
	plt.plot(acq.time_line,acq.data)
	plt.show()
	acq.save_data()
t2=time.time()

print(t2-t1)
sc.close()
# =============================================================================
