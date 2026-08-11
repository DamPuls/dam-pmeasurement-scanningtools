# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'scan_app_qt.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMenuBar, QPushButton,
    QRadioButton, QSizePolicy, QStatusBar, QTextBrowser,
    QWidget)

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        mainWindow.resize(918, 616)
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEdit_coef_axesY_motor3 = QLineEdit(self.centralwidget)
        self.lineEdit_coef_axesY_motor3.setObjectName(u"lineEdit_coef_axesY_motor3")
        self.lineEdit_coef_axesY_motor3.setEnabled(True)
        self.lineEdit_coef_axesY_motor3.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_coef_axesY_motor3, 10, 8, 1, 1)

        self.button_start_motor3 = QPushButton(self.centralwidget)
        self.button_start_motor3.setObjectName(u"button_start_motor3")

        self.gridLayout.addWidget(self.button_start_motor3, 10, 3, 1, 1)

        self.button_disconnectmotor = QPushButton(self.centralwidget)
        self.button_disconnectmotor.setObjectName(u"button_disconnectmotor")

        self.gridLayout.addWidget(self.button_disconnectmotor, 11, 0, 1, 1)

        self.textBrowser_7 = QTextBrowser(self.centralwidget)
        self.textBrowser_7.setObjectName(u"textBrowser_7")
        self.textBrowser_7.setMaximumSize(QSize(70, 25))

        self.gridLayout.addWidget(self.textBrowser_7, 5, 8, 1, 1)

        self.textBrowser_3 = QTextBrowser(self.centralwidget)
        self.textBrowser_3.setObjectName(u"textBrowser_3")
        self.textBrowser_3.setMaximumSize(QSize(40, 25))

        self.gridLayout.addWidget(self.textBrowser_3, 11, 5, 1, 1)

        self.lineEdit_scan_nbrpoint = QLineEdit(self.centralwidget)
        self.lineEdit_scan_nbrpoint.setObjectName(u"lineEdit_scan_nbrpoint")

        self.gridLayout.addWidget(self.lineEdit_scan_nbrpoint, 1, 10, 1, 1)

        self.lineEdit_coef_axesZ_motor2 = QLineEdit(self.centralwidget)
        self.lineEdit_coef_axesZ_motor2.setObjectName(u"lineEdit_coef_axesZ_motor2")
        self.lineEdit_coef_axesZ_motor2.setEnabled(True)
        self.lineEdit_coef_axesZ_motor2.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_coef_axesZ_motor2, 11, 7, 1, 1)

        self.pushButton_move_mX = QPushButton(self.centralwidget)
        self.pushButton_move_mX.setObjectName(u"pushButton_move_mX")

        self.gridLayout.addWidget(self.pushButton_move_mX, 9, 11, 1, 1)

        self.pushButton_move_mY = QPushButton(self.centralwidget)
        self.pushButton_move_mY.setObjectName(u"pushButton_move_mY")

        self.gridLayout.addWidget(self.pushButton_move_mY, 10, 11, 1, 1)

        self.lineEdit_coef_axesY_motor2 = QLineEdit(self.centralwidget)
        self.lineEdit_coef_axesY_motor2.setObjectName(u"lineEdit_coef_axesY_motor2")
        self.lineEdit_coef_axesY_motor2.setEnabled(True)
        self.lineEdit_coef_axesY_motor2.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_coef_axesY_motor2, 10, 7, 1, 1)

        self.button_connect_motor = QPushButton(self.centralwidget)
        self.button_connect_motor.setObjectName(u"button_connect_motor")

        self.gridLayout.addWidget(self.button_connect_motor, 5, 0, 1, 1)

        self.button_origin_motor1 = QPushButton(self.centralwidget)
        self.button_origin_motor1.setObjectName(u"button_origin_motor1")

        self.gridLayout.addWidget(self.button_origin_motor1, 5, 2, 1, 1)

        self.textBrowser_6 = QTextBrowser(self.centralwidget)
        self.textBrowser_6.setObjectName(u"textBrowser_6")
        self.textBrowser_6.setMaximumSize(QSize(70, 25))

        self.gridLayout.addWidget(self.textBrowser_6, 5, 7, 1, 1)

        self.pushButton_load_config = QPushButton(self.centralwidget)
        self.pushButton_load_config.setObjectName(u"pushButton_load_config")

        self.gridLayout.addWidget(self.pushButton_load_config, 5, 10, 1, 1)

        self.pushButton_move_pY = QPushButton(self.centralwidget)
        self.pushButton_move_pY.setObjectName(u"pushButton_move_pY")

        self.gridLayout.addWidget(self.pushButton_move_pY, 10, 10, 1, 1)

        self.textBrowser_2 = QTextBrowser(self.centralwidget)
        self.textBrowser_2.setObjectName(u"textBrowser_2")
        self.textBrowser_2.setMaximumSize(QSize(40, 25))

        self.gridLayout.addWidget(self.textBrowser_2, 9, 5, 1, 1)

        self.button_Start_motor1 = QPushButton(self.centralwidget)
        self.button_Start_motor1.setObjectName(u"button_Start_motor1")

        self.gridLayout.addWidget(self.button_Start_motor1, 5, 3, 1, 1)

        self.lineEdit_step_axesY = QLineEdit(self.centralwidget)
        self.lineEdit_step_axesY.setObjectName(u"lineEdit_step_axesY")

        self.gridLayout.addWidget(self.lineEdit_step_axesY, 10, 9, 1, 1)

        self.pushButton_move_pZ = QPushButton(self.centralwidget)
        self.pushButton_move_pZ.setObjectName(u"pushButton_move_pZ")

        self.gridLayout.addWidget(self.pushButton_move_pZ, 11, 10, 1, 1)

        self.button_origin_motor2 = QPushButton(self.centralwidget)
        self.button_origin_motor2.setObjectName(u"button_origin_motor2")

        self.gridLayout.addWidget(self.button_origin_motor2, 9, 2, 1, 1)

        self.pushButton_save_config = QPushButton(self.centralwidget)
        self.pushButton_save_config.setObjectName(u"pushButton_save_config")

        self.gridLayout.addWidget(self.pushButton_save_config, 3, 10, 1, 1)

        self.pushButton_move_pX = QPushButton(self.centralwidget)
        self.pushButton_move_pX.setObjectName(u"pushButton_move_pX")

        self.gridLayout.addWidget(self.pushButton_move_pX, 9, 10, 1, 1)

        self.lineEdit_coef_axesX_motor3 = QLineEdit(self.centralwidget)
        self.lineEdit_coef_axesX_motor3.setObjectName(u"lineEdit_coef_axesX_motor3")
        self.lineEdit_coef_axesX_motor3.setEnabled(True)
        self.lineEdit_coef_axesX_motor3.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_coef_axesX_motor3, 9, 8, 1, 1)

        self.lineEdit_step_axesX = QLineEdit(self.centralwidget)
        self.lineEdit_step_axesX.setObjectName(u"lineEdit_step_axesX")

        self.gridLayout.addWidget(self.lineEdit_step_axesX, 9, 9, 1, 1)

        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setMaximumSize(QSize(40, 25))

        self.gridLayout.addWidget(self.textBrowser, 10, 5, 1, 1)

        self.lineEdit_coef_axesX_motor2 = QLineEdit(self.centralwidget)
        self.lineEdit_coef_axesX_motor2.setObjectName(u"lineEdit_coef_axesX_motor2")
        self.lineEdit_coef_axesX_motor2.setEnabled(True)
        self.lineEdit_coef_axesX_motor2.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_coef_axesX_motor2, 9, 7, 1, 1)

        self.button_connect_pico = QPushButton(self.centralwidget)
        self.button_connect_pico.setObjectName(u"button_connect_pico")

        self.gridLayout.addWidget(self.button_connect_pico, 9, 0, 1, 1)

        self.textBrowser_5 = QTextBrowser(self.centralwidget)
        self.textBrowser_5.setObjectName(u"textBrowser_5")
        self.textBrowser_5.setMaximumSize(QSize(70, 25))

        self.gridLayout.addWidget(self.textBrowser_5, 5, 6, 1, 1)

        self.checkBox_axescan_Y = QCheckBox(self.centralwidget)
        self.checkBox_axescan_Y.setObjectName(u"checkBox_axescan_Y")

        self.gridLayout.addWidget(self.checkBox_axescan_Y, 2, 11, 1, 1)

        self.checkBox_axescan_Z = QCheckBox(self.centralwidget)
        self.checkBox_axescan_Z.setObjectName(u"checkBox_axescan_Z")

        self.gridLayout.addWidget(self.checkBox_axescan_Z, 3, 11, 1, 1)

        self.pushButton_move_mZ = QPushButton(self.centralwidget)
        self.pushButton_move_mZ.setObjectName(u"pushButton_move_mZ")

        self.gridLayout.addWidget(self.pushButton_move_mZ, 11, 11, 1, 1)

        self.textBrowser_8 = QTextBrowser(self.centralwidget)
        self.textBrowser_8.setObjectName(u"textBrowser_8")
        self.textBrowser_8.setMaximumSize(QSize(70, 25))

        self.gridLayout.addWidget(self.textBrowser_8, 5, 9, 1, 1)

        self.lineEdit_coef_axesZ_motor1 = QLineEdit(self.centralwidget)
        self.lineEdit_coef_axesZ_motor1.setObjectName(u"lineEdit_coef_axesZ_motor1")
        self.lineEdit_coef_axesZ_motor1.setEnabled(True)
        self.lineEdit_coef_axesZ_motor1.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_coef_axesZ_motor1, 11, 6, 1, 1)

        self.button_origin_motor3 = QPushButton(self.centralwidget)
        self.button_origin_motor3.setObjectName(u"button_origin_motor3")

        self.gridLayout.addWidget(self.button_origin_motor3, 10, 2, 1, 1)

        self.checkBox_axescan_X = QCheckBox(self.centralwidget)
        self.checkBox_axescan_X.setObjectName(u"checkBox_axescan_X")

        self.gridLayout.addWidget(self.checkBox_axescan_X, 1, 11, 1, 1)

        self.lineEdit_coef_axesX_motor1 = QLineEdit(self.centralwidget)
        self.lineEdit_coef_axesX_motor1.setObjectName(u"lineEdit_coef_axesX_motor1")
        self.lineEdit_coef_axesX_motor1.setEnabled(True)
        self.lineEdit_coef_axesX_motor1.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_coef_axesX_motor1, 9, 6, 1, 1)

        self.lineEdit_coef_axesY_motor1 = QLineEdit(self.centralwidget)
        self.lineEdit_coef_axesY_motor1.setObjectName(u"lineEdit_coef_axesY_motor1")
        self.lineEdit_coef_axesY_motor1.setEnabled(True)
        self.lineEdit_coef_axesY_motor1.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_coef_axesY_motor1, 10, 6, 1, 1)

        self.button_start_motor2 = QPushButton(self.centralwidget)
        self.button_start_motor2.setObjectName(u"button_start_motor2")

        self.gridLayout.addWidget(self.button_start_motor2, 9, 3, 1, 1)

        self.lineEdit_step_axesZ = QLineEdit(self.centralwidget)
        self.lineEdit_step_axesZ.setObjectName(u"lineEdit_step_axesZ")

        self.gridLayout.addWidget(self.lineEdit_step_axesZ, 11, 9, 1, 1)

        self.button_start_scan = QPushButton(self.centralwidget)
        self.button_start_scan.setObjectName(u"button_start_scan")

        self.gridLayout.addWidget(self.button_start_scan, 5, 4, 1, 1)

        self.lineEdit_coef_axesZ_motor3 = QLineEdit(self.centralwidget)
        self.lineEdit_coef_axesZ_motor3.setObjectName(u"lineEdit_coef_axesZ_motor3")
        self.lineEdit_coef_axesZ_motor3.setEnabled(True)
        self.lineEdit_coef_axesZ_motor3.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_coef_axesZ_motor3, 11, 8, 1, 1)

        self.button_start_sequence = QPushButton(self.centralwidget)
        self.button_start_sequence.setObjectName(u"button_start_sequence")

        self.gridLayout.addWidget(self.button_start_sequence, 9, 4, 1, 1)

        self.button_disconnectpico = QPushButton(self.centralwidget)
        self.button_disconnectpico.setObjectName(u"button_disconnectpico")

        self.gridLayout.addWidget(self.button_disconnectpico, 10, 0, 1, 1)

        self.listWidget = QListWidget(self.centralwidget)
        self.listWidget.setObjectName(u"listWidget")

        self.gridLayout.addWidget(self.listWidget, 0, 0, 3, 8)

        self.textBrowser_4 = QTextBrowser(self.centralwidget)
        self.textBrowser_4.setObjectName(u"textBrowser_4")
        self.textBrowser_4.setMaximumSize(QSize(16777215, 45))

        self.gridLayout.addWidget(self.textBrowser_4, 1, 9, 1, 1)

        self.textBrowser_9 = QTextBrowser(self.centralwidget)
        self.textBrowser_9.setObjectName(u"textBrowser_9")
        self.textBrowser_9.setMaximumSize(QSize(16777215, 45))

        self.gridLayout.addWidget(self.textBrowser_9, 2, 9, 1, 1)

        self.lineEdit_scan_nbrpointY = QLineEdit(self.centralwidget)
        self.lineEdit_scan_nbrpointY.setObjectName(u"lineEdit_scan_nbrpointY")

        self.gridLayout.addWidget(self.lineEdit_scan_nbrpointY, 2, 10, 1, 1)

        self.textBrowser_10 = QTextBrowser(self.centralwidget)
        self.textBrowser_10.setObjectName(u"textBrowser_10")
        self.textBrowser_10.setMaximumSize(QSize(16777215, 45))

        self.gridLayout.addWidget(self.textBrowser_10, 0, 9, 1, 3)

        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(mainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 918, 33))
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName(u"statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)

        QMetaObject.connectSlotsByName(mainWindow)
    # setupUi

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"MainWindow", None))
        self.lineEdit_coef_axesY_motor3.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.button_start_motor3.setText(QCoreApplication.translate("mainWindow", u"Start axe 3", None))
        self.button_disconnectmotor.setText(QCoreApplication.translate("mainWindow", u"Disconnect motor", None))
        self.textBrowser_7.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">motor3</p></body></html>", None))
        self.textBrowser_3.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Z</p></body></html>", None))
        self.lineEdit_scan_nbrpoint.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.lineEdit_coef_axesZ_motor2.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.pushButton_move_mX.setText(QCoreApplication.translate("mainWindow", u"- X", None))
        self.pushButton_move_mY.setText(QCoreApplication.translate("mainWindow", u"- Y", None))
        self.lineEdit_coef_axesY_motor2.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.button_connect_motor.setText(QCoreApplication.translate("mainWindow", u"Connect Motor", None))
        self.button_origin_motor1.setText(QCoreApplication.translate("mainWindow", u"Origin  motor 1", None))
        self.textBrowser_6.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">motor2</p></body></html>", None))
        self.pushButton_load_config.setText(QCoreApplication.translate("mainWindow", u"load ", None))
        self.pushButton_move_pY.setText(QCoreApplication.translate("mainWindow", u"+ Y", None))
        self.textBrowser_2.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">X</p></body></html>", None))
        self.button_Start_motor1.setText(QCoreApplication.translate("mainWindow", u"Start axe 1", None))
        self.lineEdit_step_axesY.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.pushButton_move_pZ.setText(QCoreApplication.translate("mainWindow", u"+ Z", None))
        self.button_origin_motor2.setText(QCoreApplication.translate("mainWindow", u"Origin  motor 2", None))
        self.pushButton_save_config.setText(QCoreApplication.translate("mainWindow", u"save ini", None))
        self.pushButton_move_pX.setText(QCoreApplication.translate("mainWindow", u"+ X", None))
        self.lineEdit_coef_axesX_motor3.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.lineEdit_step_axesX.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.textBrowser.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Y</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.lineEdit_coef_axesX_motor2.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.button_connect_pico.setText(QCoreApplication.translate("mainWindow", u"Connect Pico", None))
        self.textBrowser_5.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">motor1</p></body></html>", None))
        self.checkBox_axescan_Y.setText(QCoreApplication.translate("mainWindow", u"Y", None))
        self.checkBox_axescan_Z.setText(QCoreApplication.translate("mainWindow", u"Z", None))
        self.pushButton_move_mZ.setText(QCoreApplication.translate("mainWindow", u"- Z", None))
        self.textBrowser_8.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Step</p></body></html>", None))
        self.lineEdit_coef_axesZ_motor1.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.button_origin_motor3.setText(QCoreApplication.translate("mainWindow", u"Origin  motor 3", None))
        self.checkBox_axescan_X.setText(QCoreApplication.translate("mainWindow", u"X", None))
        self.lineEdit_coef_axesX_motor1.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.lineEdit_coef_axesY_motor1.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.button_start_motor2.setText(QCoreApplication.translate("mainWindow", u"Start axe 2", None))
        self.lineEdit_step_axesZ.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.button_start_scan.setText(QCoreApplication.translate("mainWindow", u"Start scan", None))
        self.lineEdit_coef_axesZ_motor3.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.button_start_sequence.setText(QCoreApplication.translate("mainWindow", u"Start sequence ", None))
        self.button_disconnectpico.setText(QCoreApplication.translate("mainWindow", u"Disconnect pico", None))
        self.textBrowser_4.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">nbr point (1st checked axis)</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.textBrowser_9.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">nbr point (2nd checked axis, plane only)</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.lineEdit_scan_nbrpointY.setText(QCoreApplication.translate("mainWindow", u"0", None))
        self.textBrowser_10.setHtml(QCoreApplication.translate("mainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Check 1 axis = line scan. Check 2 = plane scan (e.g. Y+Z).</p></body></html>", None))
    # retranslateUi

