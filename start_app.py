# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 14:01:43 2026

@author: MathieuGUYOT
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidget
from PySide6.QtCore import QFile
from PySide6.QtGui import QKeySequence
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
window.ui.button_start_scan.clicked.connect(lambda: f_app.toggle_scan_app(window.ui.button_start_scan))
window.ui.button_start_sequence.clicked.connect(lambda: f_app.toggle_sequence_scan_app(window.ui.button_start_sequence))
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

# "Find Focus" button hidden (not removed) - the focus-search algorithm
# doesn't work well and is never used; its underlying code/wiring is left
# untouched in case it's revisited later.
button_find_focus = QPushButton("Find Focus", window.ui.centralwidget)
window.ui.gridLayout.addWidget(button_find_focus, 10, 4, 1, 1)
button_find_focus.clicked.connect(f_app.find_focus_app)
button_find_focus.setVisible(False)

# New, additive: "Run shot sequence" / "Stop shot sequence" toggle -
# repeated shots at the current position (no motor movement), saved to
# disk. Already existed in process_scan.py (wired only in the old Tkinter
# Scan_app.py) - just exposing it here. Placed in Find Focus's now-hidden
# grid cell (row 10, col 4).
button_shot_sequence = QPushButton("Run shot sequence", window.ui.centralwidget)
window.ui.gridLayout.addWidget(button_shot_sequence, 10, 4, 1, 1)
button_shot_sequence.clicked.connect(lambda: f_app.toggle_shot_sequence_app(button_shot_sequence))

# New, additive: let the message list's text be selected and copied
# (Ctrl+C) - QListWidget items are selectable by default but don't wire
# up copy-to-clipboard on their own.
def _listWidget_keyPressEvent(event, _base=QListWidget.keyPressEvent):
    if event.matches(QKeySequence.StandardKey.Copy):
        selected = window.ui.listWidget.selectedItems()
        if selected:
            QApplication.clipboard().setText("\n".join(item.text() for item in selected))
    else:
        _base(window.ui.listWidget, event)
window.ui.listWidget.keyPressEvent = _listWidget_keyPressEvent

# New, additive: cleanly disconnect the motors and the PicoScope when the
# window is closed - previously neither happened automatically, relying on
# the OS/driver to reclaim the handles after the process dies. That's fine
# for the motor's plain serial port but the PicoScope needs an explicit
# ps5000aCloseUnit() to release cleanly, so closing the app without first
# clicking Disconnect could leave the scope busy on the next reconnect.
def _mainWindow_closeEvent(event, _base=QMainWindow.closeEvent):
    if f_app.pr.motor.isConnected():
        try:
            f_app.disconnect_motor_app()
        except Exception as e:
            print("error disconnecting motor on close: {}".format(e))
    try:
        f_app.disconnect_scope_app()
    except Exception as e:
        print("error disconnecting scope on close: {}".format(e))
    _base(window, event)
window.closeEvent = _mainWindow_closeEvent

f_app.load_axes()
sys.exit(app.exec())

# Fonctions reliées aux boutons
