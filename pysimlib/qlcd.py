#!/usr/bin/env python

# Drawing operations done here
 
from __future__ import absolute_import
from __future__ import print_function
import signal, os, time, sys, random

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

# --------------------------------------------------------------------
# Set serial displays

class QcanLCD(object):

    def __init__(self, decor_1, decor_2, decor_3, decor_4):
    
        self.decor_1 = decor_1
        self.decor_2 = decor_2
        self.decor_3 = decor_3
        self.decor_4 = decor_4
     
    def  set_rser(self, agv, str_1):
        if agv == 0:
            self.decor_1.rserial.set_text(str_1)
        if agv == 1:
            self.decor_2.rserial.set_text(str_1)
        if agv == 2:
            self.decor_3.rserial.set_text(str_1)
        if agv == 3:
            self.decor_4.rserial.set_text(str_1)
        
    def  set_sser(self, agv, str_1):
        if agv == 0:
            self.decor_1.sserial.set_text(str_1)
        if agv == 1:
            self.decor_2.sserial.set_text(str_1)
        if agv == 2:
            self.decor_3.sserial.set_text(str_1)
        if agv == 3:
            self.decor_4.sserial.set_text(str_1)
    
    def set_lcdx(self, agvx, str_1, str_2, str_3 = None, str_4 = None):
        if agvx == 0:
            self.set_lcd1(str_1, str_2, str_3, str_4)
        if agvx == 1:
            self.set_lcd2(str_1, str_2, str_3, str_4)
        if agvx == 2:
            self.set_lcd3(str_1, str_2, str_3, str_4)
        if agvx == 3:
            self.set_lcd4(str_1, str_2, str_3, str_4)
    
    # --------------------------------------------------------------------
    # Timeout displays
    def  set_lcd1(self, str_1, str_2, str_3 = None, str_4 = None):
        self.decor_1.qcan_1.set_text(str_1)
        self.decor_1.qcan_2.set_text(str_2)
        if(str_3 or str_4):
            self.str3 = str_3
            self.str4 = str_4
            GLib.timeout_add(3000, self.handler_tick1)
    
    
    def  set_lcd2 (self, str_1, str_2, str_3 = None, str_4 = None):
        self.decor_2.qcan_1.set_text(str_1)
        self.decor_2.qcan_2.set_text(str_2)
        if(str_3 or str_4):
            self.str5 = str_3
            self.str6 = str_4
            GLib.timeout_add(3000, self.handler_tick2)
       
    def  set_lcd3 (self, str_1, str_2, str_3 = None, str_4 = None):
        self.decor_3.qcan_1.set_text(str_1)
        self.decor_3.qcan_2.set_text(str_2)
        if(str_3 or str_4):
            self.str7 = str_3
            self.str8 = str_4
            GLib.timeout_add(3000, self.handler_tick3)
    
    def  set_lcd4 (self, str_1, str_2, str_3 = None, str_4 = None):
        self.decor_3.qcan_1.set_text(str_1)
        self.decor_3.qcan_2.set_text(str_2)
        if(str_3 or str_4):
            self.str9 = str_3
            self.str10 = str_4
            GLib.timeout_add(3000, self.handler_tick4)
    
    def handler_tick1(self):
        if self.str3:
            self.decor_1.qcan_1.set_text(self.str3)
            self.str3 = None
        if self.str4:
            self.decor_1.qcan_2.set_text(self.str4)
            self.str4 = None
            
    def handler_tick2(self):
        if self.str5:
            self.decor_2.qcan_1.set_text(self.str5)
            self.str5 = None
        if self.str6:
            self.decor_2.qcan_2.set_text(self.str6)
            self.str6 = None

    def handler_tick3(self):
        if self.str7:
            self.decor_3.qcan_1.set_text(self.str7)
            self.str7 = None
        if self.str8:
            self.decor_3.qcan_2.set_text(self.str8)
            self.str8 = None

    def handler_tick4(self):
        if self.str9:
            self.decor_2.qcan_1.set_text(self.str9)
            self.str9 = None
        if self.str10:
            self.decor_2.qcan_2.set_text(self.str10)
            self.str10 = None


