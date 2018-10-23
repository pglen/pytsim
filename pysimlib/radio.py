#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import signal, os, time, string, pickle, re, random

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

class   Radio(object):

    def __init__(self, self2, agv = 0):
        self.self2 = self2
        self.agv = agv
        self.win2 = Gtk.Window()
        self.win2.set_accept_focus(True)
        self.win2.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.sname = "rad%d" % self.agv        
        self.win2.set_transient_for(self.self2.appwin.mywin)
        self.treestore = Gtk.TreeStore(str)
        self.treeview = self.create_tree(self.treestore)
        self.treestore2 = Gtk.TreeStore(str)
        self.treeview2 = self.create_tree(self.treestore2)
        self.str2 = ""; self.str2a = ""
                            
        try:
            self.win2.set_icon_from_file(get_img_path("agvsim.png"))
        except:
            print("Canot load decor icon.", "'" + get_img_path("agvsim.png") + "'")
        
        fdesc  = Pango.FontDescription().from_string("Arial Bold 24px")
        fdescx = Pango.FontDescription().from_string("Sans Bold 20px")
        
        self.sw = Gtk.ScrolledWindow()
        self.sw.add(self.treeview)
        
        self.sw2 = Gtk.ScrolledWindow()
        self.sw2.add(self.treeview2)
        
        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 10)
        frame = Gtk.Frame()
        #frame.set_border_width(10)
        frame.set_label(" Loss Scale ")
        frame.add(self.scale)
        
        hbox = Gtk.HBox()
        hbox.pack_start(self.sw, 1, 1, 0)
        hbox.pack_start(self.sw2, 1, 1, 0)
        
        self.vbox = Gtk.VBox()
        self.vbox.pack_start(hbox, 1, 1, 0)
        self.vbox.pack_start(frame, 0, 0, 0)
        
        self.win2.add(self.vbox)
        
        self.win2.set_size_request(300, 200)
        self.win2.set_title("Radio Sim ")
        
        self.win2.set_can_focus(True)
        self.win2.connect("key-press-event", self.area_key)
        self.win2.connect("key-release-event", self.area_key)
        self.win2.connect("focus-in-event", self.area_focus)
        self.win2.connect("delete-event", self.area_destroy)    
        
        xx = config.conf.sql.get(self.sname + "cx")
        yy = config.conf.sql.get(self.sname + "cy")
        ww = config.conf.sql.get(self.sname + "cw")
        hh = config.conf.sql.get(self.sname + "ch")
    
        #print("load coord", self.sname, xx, yy, ww, hh);
        
        if not xx and not ww:
            xxx, yyy, www, hhh = get_disp_size()
            self.win2.move(www - 900, 10)
        else:    
            #print("xx", xx, "yy", yy)
            self.win2.move(int(xx), int(yy))
            self.win2.set_default_size(int(ww), int(hh))
        
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
        
        #print ("save coord", self.sname, oldxx, oldyy, oldww, oldhh)
        #print ("save coord2", self.win2.get_window().get_geometry())
        
        config.conf.sql.put(self.sname + "cx", oldxx)           
        config.conf.sql.put(self.sname + "cy", oldyy)           
        config.conf.sql.put(self.sname + "cw", oldww)           
        config.conf.sql.put(self.sname + "ch", oldhh)           
                                                   
    # --------------------------------------------------------------------
    def create_tree(self, tstore):

        # create the TreeView using treestore
        tv = Gtk.TreeView(tstore)

        # create a CellRendererText to render the data
        cell = Gtk.CellRendererText()

        # create the TreeViewColumn to display the data
        tvcolumn = Gtk.TreeViewColumn('On AIR Events')

        # add the cell to the tvcolumn and allow it to expand
        tvcolumn.pack_start(cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        tvcolumn.add_attribute(cell, 'text', 0)

        # add tvcolumn to treeview
        tv.append_column(tvcolumn)

        return tv


    def  deltree(self):
    
        # Delete previous contents
        while True:
            root = self.treestore.get_iter_first()
            if not root:
                break
            try:
                self.treestore.remove(root)
            except:
                print("Exception on rm treestore")
                break

        while True:
            root = self.treestore2.get_iter_first()
            if not root:
                break
            try:
                self.treestore2.remove(root)
            except:
                print("Exception on rm treestore")
                break

    # ------------------------------------------------------------------------------
    
    def broadcast(self, agvx, strx = "", stry = ""):
            
        str2 = strx + " " + stry
        
        #print ("bc got ", agvx, strx, stry)
            
        if agvx == 0:
            if self.str2 == str2:
                self.cnt = self.cnt + 1
                str2 = "%s TX repeated: %dx" % (str2, self.cnt + 1)
                self.treestore[self.last] = [str2]
            else:
                self.str2 = str2
                self.cnt = 0
                self.last = self.treestore.append(None, [str2])
        else:
            if self.str2a == str2:
                self.cnta = self.cnta + 1
                str2 = "%s TX repeated: %dx " % (str2, self.cnta + 1)
                self.treestore2[self.lasta] = [str2]
            else:
                self.str2a = str2
                self.cnta = 0
                self.lasta = self.treestore2.append(None, [str2])
    
        # Let the system breathe, so last one is added before scroll
        usleep(10)
        try:
            vadj = self.sw.get_vadjustment()
            vadj.set_value(vadj.get_upper())
            
            vadj2 = self.sw2.get_vadjustment()
            vadj2.set_value(vadj2.get_upper())
        except:
            pass
    
        loss = self.scale.get_value()
        rrr = random.randint(0, 100)
        
        '''if loss > rrr:
            print ("    uh oh")
        else:
            print ("TX OK")'''
        





