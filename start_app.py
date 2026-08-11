# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 14:01:43 2026

@author: MathieuGUYOT
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile
from interface_scan import Ui_mainWindow
from function_app import f_app



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
       
     


app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)
window = MainWindow()
window.show()

f_app=f_app(window)
window.ui.button_connect_pico.clicked.connect( f_app.connect_scope_app)
window.ui.button_connect_motor.clicked.connect( f_app.connect_motor_app)
window.ui.button_Start_motor1.clicked.connect(f_app.Goto_starting_pointX_app)
window.ui.button_start_motor2.clicked.connect(f_app.Goto_starting_pointY_app)
window.ui.button_start_motor3.clicked.connect(f_app.Goto_starting_pointZ_app)
window.ui.button_origin_motor1.clicked.connect(f_app.Goto_originX_app)
window.ui.button_origin_motor2.clicked.connect(f_app.Goto_originY_app)
window.ui.button_origin_motor3.clicked.connect(f_app.Goto_originZ_app)
window.ui.button_start_scan.clicked.connect(f_app.Run_scan_app)
window.ui.button_start_sequence.clicked.connect(f_app.run_sequence_scan)
window.ui.pushButton_load_config.clicked.connect(f_app.load_axes)
window.ui.pushButton_move_pX.clicked.connect(f_app.move_pointXp_app)
window.ui.pushButton_move_mX.clicked.connect(f_app.move_pointXm_app)
window.ui.pushButton_move_pY.clicked.connect(f_app.move_pointYp_app)
window.ui.pushButton_move_mY.clicked.connect(f_app.move_pointYm_app)
window.ui.pushButton_move_pZ.clicked.connect(f_app.move_pointZp_app)
window.ui.pushButton_move_mZ.clicked.connect(f_app.move_pointZm_app)
window.ui.button_disconnectmotor.clicked.connect(f_app.disconnect_motor_app)
window.ui.button_disconnectpico.clicked.connect(f_app.disconnect_scope_app)
window.ui.pushButton_save_config.clicked.connect(f_app.change_ini)
f_app.load_axes()
sys.exit(app.exec())

# Fonctions reliées aux boutons
