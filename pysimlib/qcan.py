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
from .definitions import *

class   Qcan(object):

    def __init__(self, self2, agv):
        self.self2 = self2
        self.agv = agv
        self.win2 = Gtk.Window()
        self.win2.set_accept_focus(True)
        self.win2.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
                
        self.win2.set_transient_for(self.self2.appwin.mywin)
        
        try:
            self.win2.set_icon_from_file(get_img_path("agvsim.png"))
        except:
            print("Canot load decor icon.", "'" + get_img_path("agvsim.png") + "'")
        
        fdesc  = Pango.FontDescription().from_string("Arial Bold 24px")
        fdescx = Pango.FontDescription().from_string("Sans Bold 18px")
        fdescy = Pango.FontDescription().from_string("Sans Bold 12px")
        
        self.qcan_x = Gtk.Label(" QCAN %d  " % (self.agv + 1)) 
        self.qcan_x.override_font(fdesc)
        
        self.lab1  = Gtk.Label("name: '%s' go: %d ")
        self.lab1.override_font(fdescx)
        
        self.lab1a  = Gtk.Label(" ")
        
        self.lab2  = Gtk.Label("xxx %d yyy %d ");  self.lab2.override_font(fdescy)
        self.lab3  = Gtk.Label("Status %d Speed %d ");  self.lab3.override_font(fdescy)
        self.lab4  = Gtk.Label("Zone %d Seen %d ");  self.lab4.override_font(fdescy)
        self.lab5  = Gtk.Label("Contesters %d ");  self.lab5.override_font(fdescy)
        self.lab6  = Gtk.Label("Last rcvd: ");  self.lab6.override_font(fdescy)
        self.lab7  = Gtk.Label("            ");  self.lab7.override_font(fdescy)
        self.lab8  = Gtk.Label("            ");  self.lab8.override_font(fdescy)
        self.lab9  = Gtk.Label("Scancnt: %d Relcnt: %d "); self.lab9.override_font(fdescy)
        
        self.vbox = Gtk.VBox()
        self.vbox.pack_start(self.qcan_x, 0, 0, 0)
        self.vbox.pack_start(self.lab1, 0, 0, 0)
        self.vbox.pack_start(self.lab1a, 0, 0, 0)
        self.vbox.pack_start(self.lab2, 0, 0, 0)
        self.vbox.pack_start(self.lab3, 0, 0, 0)
        self.vbox.pack_start(self.lab4, 0, 0, 0)
        self.vbox.pack_start(self.lab5, 0, 0, 0)
        self.vbox.pack_start(self.lab6, 0, 0, 0)
        self.vbox.pack_start(self.lab7, 0, 0, 0)
        self.vbox.pack_start(self.lab8, 0, 0, 0)
        self.vbox.pack_start(self.lab9, 0, 0, 0)
          
        self.win2.add(self.vbox)
        
        self.win2.set_can_focus(True)
        self.win2.connect("key-press-event", self.area_key)
        self.win2.connect("key-release-event", self.area_key)
        self.win2.connect("focus-in-event", self.area_focus)
        self.win2.connect("delete-event", self.area_destroy)    
        
        self.win2.set_size_request(250, 180)
        self.win2.set_title("State Machine")
        
        xx = config.conf.sql.get("qsrcx_%d" % self.agv)
        yy = config.conf.sql.get("qsrcy_%d" % self.agv)
        ww = config.conf.sql.get("qsrcw_%d" % self.agv)
        hh = config.conf.sql.get("qsrch_%d" % self.agv)
    
        if not xx and not ww:
            xxx, yyy, www, hhh = get_disp_size()
           
            if agv:
                self.win2.move(www - 300, 10)
            else:
                self.win2.move(www - 600, 10)
        else:    
            #print("xx", xx, "yy", yy)
            self.win2.move(int(xx), int(yy))
            self.win2.set_size_request(int(ww), int(hh))
            
        self.win2.show_all()
        self.win2.activate_focus()
        
    def close(self):
        #print("qcan close", self) 
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
        
        config.conf.sql.put("qsrcx_%d" % self.agv, oldxx)           
        config.conf.sql.put("qsrcy_%d" % self.agv, oldyy)           
        config.conf.sql.put("qsrcw_%d" % self.agv, oldww)           
        config.conf.sql.put("qsrch_%d" % self.agv, oldhh)           
    
    # Get state machine information
    def update_state(self):
    
        #print("in_update")
        ass = None
        try:
            ass = self.self2.agvs[self.agv]
        except:
            pass

        if ass:
            self.lab1.set_text("Name: '%s' Go: %d " % (ass['name'], ass['go']) )
            self.lab2.set_text("X pos %d Y pos %d " % (ass['xxx'], ass['yyy']) )
            self.lab3.set_text("Status: %d Speed: %d " % (ass['qcan']['status'], ass['qcan']['speed']) )
            self.lab4.set_text("Zone: %d Seen: %d " % (ass['zone'], ass['qcan']['seen']) )
            
            ccc = ""
            
            for aa in ass['qcan']['contesters']:
                ccc = ccc + " " + str(aa    )
                
            self.lab5.set_text("Contesters: %s " % ccc)
            
            #self.lab6.set_text("Last rcv:")
            self.lab7.set_text("'%s'" % self.self2.radio.str2)
            self.lab8.set_text("'%s'" % self.self2.radio.str2a)
            self.lab9.set_text("Scancnt: %d Relcnt: %d " % (ass['qcan']['scancnt'], 
                                                                    ass['qcan']['relcnt']) )
            









