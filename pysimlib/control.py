#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import signal, os, time, string, pickle, re

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from . import keyhand, config, ync, color, utils

from .util import *

class   Control(object):

    def __init__(self, self2):
    
        self.agv = 0
        self.self2 = self2
        
        #self.win2 = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.win2 = Gtk.Window()
        self.win2.set_accept_focus(True)
        #self.win2.set_position(Gtk.WIN_POS_CENTER)
        self.win2.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
                
        self.win2.set_transient_for(self.self2.appwin.mywin)
        
        try:
            self.win2.set_icon_from_file(get_img_path("agvsim.png"))
        except:
            print("Canot load control icon.", "'" + get_img_path("agvsim.png") + "'")
        
        fdesc  = Pango.FontDescription().from_string("Arial Bold 24px")
        fdescx = Pango.FontDescription().from_string("Sans Bold 20px")
        
        self.qcan_1 = Gtk.Label(" IDLE  ");  
        self.qcan_1.override_font(fdesc)
        #self.qcan_1.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 30535, 0))
        
        self.qcan_2 = Gtk.Label(" AGV %d  " % (self.agv + 1)) 
        self.qcan_2.override_font(fdesc)
        #self.qcan_2.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 30535, 0))
        
        frame = Gtk.Frame()
        frame.set_border_width(5)
        frame.set_label(" Buttons ")
        
        frame2 = Gtk.Frame()
        frame2.set_border_width(5)
        frame2.set_label(" AGV ")
        
        but1 = Gtk.Button("    Start Sim   "); but1.connect("clicked", self.but1); 
        but2 = Gtk.Button("    Stop Sim    "); but2.connect("clicked", self.but2)
        but3 = Gtk.Button("    ReStart     "); but3.connect("clicked", self.but3)

        but4 = Gtk.Button("  Start AGV V1   "); but4.connect("clicked", self.but4)
        but5 = Gtk.Button("  Start AGV V2   "); but5.connect("clicked", self.but5)
        but6 = Gtk.Button("  Stop AGV V1    "); but6.connect("clicked", self.but6)
        but7 = Gtk.Button("  Stop AGV V2    "); but7.connect("clicked", self.but7)
        
        but8 = Gtk.Button("    Slower    "); but8.connect("clicked", self.but8)
        but9 = Gtk.Button("    Faster    "); but9.connect("clicked", self.but9)

                #frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN )
        #frame.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 100, 0))
        
        label3 = Gtk.Label("   ");   label4 = Gtk.Label("   ") 
        label3a = Gtk.Label("   ");  label4a = Gtk.Label("   ") 
      
        hbox2 = Gtk.HBox(); hbox2.set_spacing(6);  hbox2.set_border_width(3)
        hbox2.pack_start(but1, 0, 0, 0)  
        hbox2.pack_start(but2, 0, 0, 0)  
        hbox2.pack_start(but3, 0, 1, 0)  
        
        hbox3 = Gtk.HBox();   hbox3.set_spacing(6); hbox3.set_border_width(3)
        hbox3.pack_start(but4, 0, 0, 0)  
        hbox3.pack_start(but5, 0, 0, 0)  
        hbox3.pack_start(but8, 0, 0, 0)  
        
        hbox4 = Gtk.HBox();   hbox4.set_spacing(6); hbox4.set_border_width(3)
        hbox4.pack_start(but6, 0, 0, 0)  
        hbox4.pack_start(but7, 0, 0, 0)  
        hbox4.pack_start(but9, 0, 0, 0)  
        
        #hbox2.pack_start(label3, 0, 0, 0)  
        #hbox2.pack_start(entry, True, True, 0)  
        #hbox2.pack_start(label4, 0, 0, 0)  
        
        vbox3 = Gtk.VBox()
        vbox3.pack_start(hbox2, 0, 0, 0)  
        vbox3.pack_start(hbox3, 0, 0, 0)  
        vbox3.pack_start(hbox4, 0, 0, 0)  
        vbox3.pack_start(label3a, 0, 0, 0)  
        #vbox3.pack_start(self.qcan_1, 0, 0, 0)  
        #vbox3.pack_start(self.qcan_2, 0, 0, 0)  
        vbox3.pack_start(label4a, 0, 0, 0)  
        
        frame.add(vbox3)
        
        # ===============================================================
        
        vbox4 = Gtk.VBox()
        entry = Gtk.Entry(); 
        vbox4.pack_start(entry, 0, 0, 0)  
      
      #vbox4.pack_start(label6, 0, 0, 0)  
        #vbox4.pack_start(self.label7, 0, 0, 0)  
        #vbox4.pack_start(label8, 0, 0, 0)  
      
        #vbox4.pack_start(label9, 0, 0, 0)  
        #vbox4.pack_start(self.label11, 0, 0, 0)  
        #vbox4.pack_start(label10, 0, 0, 0)  
        
        frame2.add(vbox4)
        
        vbox2 = Gtk.VBox()
        vbox2.pack_start(frame2, 0, 0, 0)
        vbox2.pack_start(frame, 0, 0, 0)
        
        self.win2.add(vbox2)
        
        self.win2.set_can_focus(True)
        self.win2.connect("key-press-event", self.area_key)
        self.win2.connect("key-release-event", self.area_key)
        self.win2.connect("focus-in-event", self.area_focus)
        self.win2.connect("delete-event", self.area_destroy)    
        
        xxx, yyy, www, hhh = get_disp_size()
       
        self.win2.set_size_request(250, 180)
        self.win2.set_title("Control Panel")
        
        xx = config.conf.sql.get("csrcx_%d" % self.agv)
        yy = config.conf.sql.get("csrcy_%d" % self.agv)
        ww = config.conf.sql.get("csrcw_%d" % self.agv)
        hh = config.conf.sql.get("csrch_%d" % self.agv)
    
        if not xx and not yy == 0:
            if self.agv:
                self.win2.move(www - 900, 10)
            else:
                self.win2.move(www - 900, 10)
        else:            
            #print("xx", xx, "yy", yy)
            self.win2.move(int(xx), int(yy))
            
        self.win2.show_all()
        self.win2.activate_focus()
        
    def but1(self, but):
        #print ("but1 pressed")
        self.self2.mained.update_statusbar("Starting simlation.")
        self.self2.stop = False
        pass
        
    def but2(self, but):
        #print ("but2 pressed")
        self.self2.mained.update_statusbar("Stopping simlation.")
        self.self2.stop = True
        pass
    
    def but3(self, but):
        #print ("but3 pressed")
        self.self2.restart_sim()
         
    def but4(self, but):
        #print ("but4 pressed")
        self.self2.mained.update_statusbar("Started AGV 1.")
        self.self2.agvs[0]['go'] = 1
     
    def but5(self, but):
        #print ("but5 pressed")
        self.self2.mained.update_statusbar("Started AGV 1.")
        self.self2.agvs[1]['go'] = 1
         
    def but6(self, but):
        #print ("but6 pressed")
        self.self2.mained.update_statusbar("Started AGV 1.")
        self.self2.agvs[0]['go'] = 0
         
    def but7(self, but):
        #print ("but7 pressed")
        self.self2.mained.update_statusbar("Started AGV 1.")
        self.self2.agvs[1]['go'] = 0
 
    def but8(self, but):
        #print ("but8 pressed")
        if self.self2.mained.timeout > 100:
           self.self2.mained.timeout = self.self2.mained.timeout + 100
        elif self.self2.mained.timeout >= 10:
           self.self2.mained.timeout = self.self2.mained.timeout + 10
        self.self2.mained.update_statusbar(
                    "Slower ... (delay=%d)" % self.self2.mained.timeout)
        
    def but9(self, but):
        #print ("but9 pressed")
        self.self2.mained.update_statusbar(
                "Faster ... (delay=%d)" % self.self2.mained.timeout)
        if self.self2.mained.timeout > 100:
           self.self2.mained.timeout = self.self2.mained.timeout - 100
        elif self.self2.mained.timeout > 10:
           self.self2.mained.timeout = self.self2.mained.timeout - 10
     
    def close(self):
        #print("control close", self) 
        self.win2.close()    
        
    # Focus on the current window
    def area_focus(self, area, event):
        #print ("control area_focus")
        pass
        
    # Call key handler
    def area_key(self, area, event):
        #print ("control area_key", event)
        # Do key down:
        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Escape:
                #print "Esc"
                area.destroy()
    
        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Return:
                #print "Ret"
                area.destroy()
    
            if event.keyval == Gdk.KEY_Alt_L or \
                    event.keyval == Gdk.KEY_Alt_R:
                self.alt = True;
        
            if event.keyval >= Gdk.KEY_1 and \
                    event.keyval <= Gdk.KEY_9:
                pass
                print("pedwin Alt num", event.keyval - Gdk.KEY__1)
            
            if event.keyval == Gdk.KEY_x or \
                    event.keyval == Gdk.KEY_X:
                if self.alt:
                    self.self2.appwin.mywin.present()
                    pass
                                      
        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                self.alt = False;
    
    def area_destroy(self, event, arg):
   
        #print("control area destroy", self) 
        
        # Finally, gdk delivers an up to date position    
        oldxx, oldyy = self.win2.get_position() 
        oldww, oldhh = self.win2.get_size()
        
        #print ("save coord", oldxx, oldyy, oldww, oldhh)
        #print ("save coord2", self.win2.get_window().get_geometry())
        
        config.conf.sql.put("csrcx_%d" % self.agv, oldxx)           
        config.conf.sql.put("csrcy_%d" % self.agv, oldyy)           
        config.conf.sql.put("csrcw_%d" % self.agv, oldww)           
        config.conf.sql.put("csrch_%d" % self.agv, oldhh)           
    








