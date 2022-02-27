# -*- coding: utf-8 -*-
"""
Created on Tue Oct 01 18:52:29 2013

@author: itbl_orlando
"""

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog, QLabel, QFrame, QVBoxLayout
import os

class StartPage(QDialog):
    def __init__(self,parent=None):
        super(StartPage,self).__init__(parent)
        
        #diocionácio do sistema operativo
        dic = os.environ
        
        cp = dic['COMPUTERNAME']
        pu = dic['USERNAME']
        pc = QLabel("Terminal: %s " % cp, self)
        pc_user = QLabel("Licenciado para: %s " % pu, self)
        self.usuario = QLabel("Usuário: %s ")

        self.bmvindo = QLabel("Bem Vindo, %s.")
        self.bmvindo.setAlignment(Qt.AlignCenter)
        font = QFont("Courier New", 24)
        self.bmvindo.setFont(font)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
    
        lay = QVBoxLayout()
        
        lay.addStretch()
        lay.addWidget(self.bmvindo,Qt.AlignCenter)
        lay.addStretch()
        lay.addWidget(pc)
        lay.addWidget(pc_user)
        lay.addWidget(line)
        lay.addWidget(self.usuario)
        
        self.setLayout(lay)

        self.logo = "./images/luxury_hotel-wallpaper-1680x1260.jpg"

        style2 = """ QDialog{border-image: url(%s);}""" % self.logo

        self.setStyleSheet(style2)
        

