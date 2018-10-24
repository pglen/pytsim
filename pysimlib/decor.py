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

class   Decor(object):

    def __init__(self, self2, agv):
    
        self.agv = agv
        self.self2 = self2
        
        #self.win2 = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.win2 = Gtk.Window()
        self.win2.set_accept_focus(True)
        #self.win2.set_position(Gtk.WIN_POS_CENTER)
        self.win2.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
                
        #self.win2.set_transient_for(self.self2.appwin.mywin)
        
        try:
            self.win2.set_icon_from_file(get_img_path("agvsim.png"))
        except:
            print("Canot load decor icon.", "'" + get_img_path("agvsim.png") + "'")
        
        fdesc  = Pango.FontDescription().from_string("Arial Bold 24px")
        fdescx = Pango.FontDescription().from_string("Sans Bold 20px")
        
        self.qcan_1 = Gtk.Label(" IDLE  ");  
        self.qcan_1.override_font(fdesc)
        #self.qcan_1.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 30535, 0))
        
        self.qcan_2 = Gtk.Label(" AGV %d  " % (self.agv + 1)) 
        self.qcan_2.override_font(fdesc)
        #self.qcan_2.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 30535, 0))
        
        frame = Gtk.Frame()
        frame.set_border_width(10)
        frame.set_label(" Q-CAN ")
        
        frame2 = Gtk.Frame()
        frame2.set_border_width(10)
        frame2.set_label(" AGV ")
        
        #frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN )
        #frame.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 100, 0))
        
        label3 = Gtk.Label("   ");   label4 = Gtk.Label("   ") 
        label3a = Gtk.Label("   ");  label4a = Gtk.Label("   ") 
        
        mmm = "     Com       Z#       Arg1       Arg2 "
        #ddd = " \  ##  ##  ##  ##  "
        ddd = " \  00  00  00  00  "
        
        label5 = Gtk.Label("   ");  label6 = Gtk.Label(" AGV Send to QCAN2 Radio ") 
        label6a = Gtk.Label(mmm)
        
        self.sserial = Gtk.Label(ddd);  label8 = Gtk.Label("   ") 
        self.sserial.override_font(fdescx)
      
        label9 = Gtk.Label(" AGV Receive from QCAN2 Radio ");  label10 = Gtk.Label("   ") 
        label9a = Gtk.Label(mmm)
        self.rserial = Gtk.Label(ddd); 
        self.rserial.override_font(fdescx)
      
        entry = Gtk.Entry(); 
        hbox2 = Gtk.HBox()
        hbox2.pack_start(label3, 0, 0, 0)  
        hbox2.pack_start(entry, True, True, 0)  
        hbox2.pack_start(label4, 0, 0, 0)  
        
        vbox3 = Gtk.VBox()
        vbox3.pack_start(label3a, 0, 0, 0)  
        vbox3.pack_start(self.qcan_1, 0, 0, 0)  
        vbox3.pack_start(self.qcan_2, 0, 0, 0)  
        vbox3.pack_start(label4a, 0, 0, 0)  
        frame.add(vbox3)
        
        # ===============================================================
        
        vbox4 = Gtk.VBox()
        vbox4.pack_start(label6, 0, 0, 0)  
        vbox4.pack_start(label6a, 0, 0, 0)  
        vbox4.pack_start(self.sserial, 0, 0, 0)  
        vbox4.pack_start(label8, 0, 0, 0)  
      
        vbox4.pack_start(label9, 0, 0, 0)  
        vbox4.pack_start(label9a, 0, 0, 0)  
        vbox4.pack_start(self.rserial, 0, 0, 0)  
        vbox4.pack_start(label10, 0, 0, 0)  
        
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
        
        self.win2.set_size_request(250, 180)
        self.win2.set_title("AGV %d" % (self.agv + 1))
        
        #self.win2.set_focus_visible(True)
        
        xx = config.conf.sql.get("wsrcx_%d" % self.agv)
        yy = config.conf.sql.get("wsrcy_%d" % self.agv)
        ww = config.conf.sql.get("wsrcw_%d" % self.agv)
        hh = config.conf.sql.get("wsrch_%d" % self.agv)
    
        if not xx and not ww:
            xxx, yyy, www, hhh = get_disp_size()
           
            if agv:
                self.win2.move(www - 300, 10)
            else:
                self.win2.move(www - 600, 10)
        else:    
            #print("xx", xx, "yy", yy)
            self.win2.move(int(xx), int(yy))
            
        self.win2.show_all()
        self.win2.activate_focus()
        
    def close(self):
        #print("decor close", self) 
        self.win2.close()    
        
    # Focus on the current window
    def area_focus(self, area, event):
        #print ("decor area_focus")
        pass
        
    # Call key handler
    def area_key(self, area, event):
        #print ("decor area_key", event)
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
                    #area.destroy()
                                      
        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                self.alt = False;
    
    def area_destroy(self, event, arg):
   
        #print("decor area destroy", self) 
        
        # Finally, gdk delivers an up to date position    
        oldxx, oldyy = self.win2.get_position() 
        oldww, oldhh = self.win2.get_size()
        
        #print ("save coord", oldxx, oldyy, oldww, oldhh)
        #print ("save coord2", self.win2.get_window().get_geometry())
        
        config.conf.sql.put("wsrcx_%d" % self.agv, oldxx)           
        config.conf.sql.put("wsrcy_%d" % self.agv, oldyy)           
        config.conf.sql.put("wsrcw_%d" % self.agv, oldww)           
        config.conf.sql.put("wsrch_%d" % self.agv, oldhh)           
    










