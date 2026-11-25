# Pressure_scanning_tools 
## Description 
This code allows you to perform pressure mapping

## Installation instructions
1. PICOSDK installation
- Download the picoSDK at this address:https://www.picotech.com/downloads
- For installation follow the instructions in the README file in the SDK folder
the picoscope use p5442D MSO 
2. Library installation 
install PySide6 numpy scipy matplotlib pyserial picosdk with pip 

## User guide 
- Run the interface 'start_app.py'
- Push le button 'Connect motor' 

- Push le button 'Connect scope' 
- Press the buttons 'OriginX' 'OriginY' 'OriginZ' one after the other (Be careful, the arm may collide with the set-up)
- Put scan paramaters in the file 'config_scan.ini' on the folder ''config' 
- Press the buttons 'Start_X' 'Start_Y' 'Start_Z' one after the other (Be careful, the arm may collide with the set-up)
Be careful, the arm may collide with the set-up, be certain that the end points of the scan can be reached by the arm without colliding!!!!!!!!!!!!!!!!!!!!
- Press the Button Scan_start
- The Result  is saved in the folder 'measure'  with this format  measure%year_%month_%day_%hour_%minute_%second
- Sequence scans read every .ini file in the folder 'sequence_scan'
