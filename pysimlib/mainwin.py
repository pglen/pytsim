#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import signal, os, time, sys, subprocess, platform
import warnings

import gi
#from six.moves import range
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

from . import ync, config, doc, ui, menu

# Into our name space
from     .util import *

STATUSCOUNT = 9             # Length of the status bar timeout (in sec)

treestore   = None
treestore2  = None
notebook    = None

#main_timeout = 300

# -----------------------------------------------------------------------
# Create document

class edPane(Gtk.VPaned):

    def __init__(self, buff = [], focus = False):

        global notebook, mained

        pos = config.conf.sql.get_int("vpaned")
        if pos == 0: pos = 10

        Gtk.VPaned.__init__(self)
        self.set_border_width(5)
        self.set_position(pos)
        self.vbox = edWin(buff);
        self.add2(self.vbox)
        
        self.tv = Gtk.TextView() 
        self.tv.set_size_request(50, 50)
        self.tbuff = self.tv.get_buffer()
        
        self.tvs = Gtk.ScrolledWindow()
        self.tvs.add(self.tv)
        
        self.tv2 = Gtk.TextView()
        self.tv2.set_size_request(50, 50)
        self.tbuff2 = self.tv2.get_buffer()
        
        self.tvs2 = Gtk.ScrolledWindow()
        self.tvs2.add(self.tv2)
        
        self.paned2 = Gtk.HPaned()
        self.paned2.set_border_width(5)
        self.paned2.set_size_request(50, 50)
        self.paned2.add1(self.tvs)
        self.paned2.add2(self.tvs2)
        self.paned2.set_position(500)
        
        self.add1(self.paned2)
        self.set_size_request(100, 100)
        
        # Shortcuts to access the editor windows
        self.area  = self.vbox.area
        #self.area2 = self.vbox2.area
        
    def append_tv(self, txt):   
        iii = self.tbuff.get_end_iter()
        self.tbuff.insert(iii, txt + "\n")
        usleep(10)
        vadj = self.tv.get_vadjustment()
        vadj.set_value(vadj.get_upper())

    def append_tv2(self, txt):   
        iii = self.tbuff2.get_end_iter()
        self.tbuff2.insert(iii, txt + "\n")
        usleep(10)
        #self.tv2.scroll_to_iter(iii, .1, True, 1, 1)
        vadj = self.tv2.get_vadjustment()
        vadj.set_value(vadj.get_upper())


    def clear_tvs(self):   
        self.tbuff.set_text("")
        self.tbuff2.set_text("")
        
# -----------------------------------------------------------------------
# Create main document widget with scroll bars

class edWin(Gtk.VBox):

    def __init__(self, buff, readonly = False):

        global notebook, mained

        Gtk.VBox.__init__(self)
        
        # Make it acessable:
        self.area  = doc.Doc(buff, mained, readonly)
        #print "created", self.area, mained
        
        # Give access to notebook and main editor window
        self.area.notebook = notebook
        self.area.mained = mained
        self.area.fname = ""
        self.area.container = self

        frame = Gtk.Frame(); frame.add(self.area)
        self.area.frame = frame

        #frame.
        hbox = Gtk.HBox()
        hbox.pack_start(frame, True, True, 0)
        hbox.pack_end(self.area.vscroll, False, False, 0)

        self.pack_start(hbox, True, True, 0)
        self.pack_end(self.area.hscroll, False, False, 0)

# ------------------------------------------------------------------------
#  Define Application Main Window claass

class  MainWindow():

    def __init__(self, fname, parent, names):

        self.full = False
        self.fcount = 0
        self.statuscount = 0
        self.alt = False
        
        self.timeout = 300
        
        register_stock_icons()

        global mained
        mained = self

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print disp
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)   
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y
        
        # Resort to old means of getting screen w / h
        if www == 0 or hhh == 0:
            www = Gdk.screen_width(); hhh = Gdk.screen_height();
       
        # Create the toplevel window
        #window = Gtk.Window(Gtk.WINDOW_TOPLEVEL)
        self.mywin = Gtk.Window()
        #www = Gdk.screen_width(); hhh = Gdk.screen_height();

        if config.conf.full_screen:
            self.mywin.set_default_size(www, hhh)
        else:
            xx = config.conf.sql.get_int("xx")
            yy = config.conf.sql.get_int("yy")
            ww = config.conf.sql.get_int("ww")
            hh = config.conf.sql.get_int("hh")

            if ww == 0 or hh == 0:
                self.mywin.set_position(Gtk.WindowPosition.CENTER)
                self.mywin.set_default_size(7*www/8, 5*hhh/8)
                self.mywin.move(www / 32, hhh / 10)
            else:
                self.mywin.set_default_size(ww, hh)
                self.mywin.move(xx, yy)
                
            #self.mywin.set_default_size(7*www/8, 7*hhh/8)
            #self.mywin.set_position(Gtk.WindowPosition.CENTER)
            #self.mywin.move(xxx + www / 16, yyy / hhh / 16)          
        try:
            self.mywin.set_icon_from_file(get_img_path("tsim.png"))
        except:
            print("Canot load icon.", "'" + get_img_path("tsim.png") + "'")

        merge = Gtk.UIManager()
        #self.mywin.set_data("ui-manager", merge)

        aa = menu.create_action_group(self)
        merge.insert_action_group(aa, 0)
        self.mywin.add_accel_group(merge.get_accel_group())
        
        try:
            mergeid = merge.add_ui_from_string(ui.ui_info)
        except GLib.GError as msg:
            print("Building menus failed: %s" % msg)
        
        # Add MRU
        for cnt in range(6):
            ss = "/sess_%d" % cnt
            fname = config.conf.sql.get(ss)
            if fname != "":
                self.add_mru(merge, aa, fname, ss)
        merge_id = merge.new_merge_id()
        #merge.add_ui(merge_id, "ui/MenuBar/FileMenu/SaveAs", "", \
        #        None, Gtk.UI_MANAGER_SEPARATOR, False)

        mbar = merge.get_widget("/MenuBar")
        mbar.show()
       
        self.mywin.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        
        global notebook

        # Create note for the main window, give access to it for all
        notebook = Gtk.Notebook(); self.notebook = notebook
        notebook.popup_enable()
        notebook.set_scrollable(True)
        
        # Create the default window
        notebook.append_page(edPane([]))
            
        #notebook.add_events(Gdk.FOCUS_CHANGE_MASK)
        #notebook.add_events(Gdk.ALL_EVENTS_MASK)

        notebook.connect("switch-page", self.note_swpage_cb)
        notebook.connect("focus-in-event", self.note_focus_in)

        # Futile attempts
        #notebook.connect("change-current-page", self.note_page_cb)
        #notebook.connect("grab-focus", self.note_grab_focus_cb)
        #notebook.connect("focus", self.note_focus_cb)
        #notebook.connect("create-window", self.note_create_cb)
        #notebook.connect("enter-notify-event", self.note_enter_notify)

        self.mywin.connect("window_state_event", self.update_resize_grip)
        #self.mywin.connect("destroy", OnExit)
        self.mywin.connect("unmap", OnExit)

        #self.mywin.connect("key-press-event", self.area_key)
        #self.mywin.connect("key-release-event", self.area_key)

        #self.mywin.connect("set-focus", self.area_focus)
        self.mywin.connect("focus-in-event", self.area_focus_in)
        self.mywin.connect("focus-out-event", self.area_focus_out)
        self.mywin.connect("window-state-event", self.area_winstate)
        self.mywin.connect("size_allocate", self.area_size)
        self.mywin.connect("configure_event", self.area_resize)

        #self.mywin.connect("area-focus-event", self.area_focus_in)
        #self.mywin.connect("event", self.area_event)
        #self.mywin.connect("enter-notify-event", self.area_enter)
        #self.mywin.connect("leave-notify-event", self.area_leave)
        #self.mywin.connect("event", self.unmap)

        #tbar = merge.get_widget("/ToolBar"); 
        #tbar.set_tooltips(True)
        #tbar.show()
        
        hpaned = Gtk.HPaned(); hpaned.set_border_width(5)

        scroll = Gtk.ScrolledWindow()

        treeview = self.create_tree()
        treeview.connect("row-activated",  self.tree_sel)
        treeview.connect("cursor-changed",  self.tree_sel_row)
        self.treeview = treeview

        treeview2 = self.create_vartree()
        treeview2.connect("row-activated",  self.tree_sel2)
        treeview2.connect("cursor-changed",  self.tree_sel_row2)
        self.treeview2 = treeview2

        vpaned = Gtk.VPaned(); vpaned.set_border_width(5)

        scroll.add(treeview)
        frame2 = Gtk.Frame(); frame2.add(scroll)
        vpaned.add(frame2)
        
        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(treeview2)
        frame3 = Gtk.Frame(); frame3.add(scroll2)
        vpaned.set_focus_chain((frame2,))
        vpaned.add(frame3)
        
        vpaned.set_position(self.get_height() - 340)
        hpaned.add(vpaned)
        
        self.hpanepos = config.conf.sql.get_int("hpaned")
        if self.hpanepos == 0: self.hpanepos = 200
        hpaned.set_position(self.hpanepos)
        
        hpaned.pack2(notebook)
        
        self.hpaned = hpaned
        
        slabs = Gtk.Label("   ")
        self.slab = Gtk.Label(" status  ")
        self.slab.set_xalign(Gtk.Align.START)
        self.slab.set_yalign(Gtk.Align.START)
        
        shbox = Gtk.HBox()
        shbox.pack_start(slabs, 0, 0, 0)
        shbox.pack_start(self.slab, 0, 0, 0)
        
        self.slab2 = Gtk.Label("  idle   ")
        self.slab2.set_xalign(Gtk.Align.START)
        self.slab2.set_yalign(Gtk.Align.START)
        
        self.hpane2 = Gtk.HPaned()
        
        self.hpane2.pack1(shbox, 1, 1)
        self.hpane2.set_position(self.get_width() - 320)
        self.hpane2.pack2(self.slab2, 1, 1)

        bbox = Gtk.VBox()
        bbox.pack_start(mbar, 0,0, 0)
        bbox.pack_start(hpaned, 1,1, 0)
        bbox.pack_start(self.hpane2, 0,0, 0)
        
        self.mywin.add(bbox)
        self.mywin.show_all()

        # ----------------------------------------------------------------
        # Read in buffers
        
        cnt = 0
        '''for aa in names:
            aaa = os.path.realpath(aa)
            #print "loading file: ", aaa
            vpaned = edPane()
            ret = vpaned.area.loadfile(aaa)
            if not ret:
                self.update_statusbar("Cannot read file '{0:s}', creating ...". format(aaa))
                ret = self.newfile(aaa)
                if not ret:
                    self.update_statusbar("Cannot create fle '{0:s}'". format(aaa))
                    continue
                
            ret = vpaned.area2.loadfile(aaa)

            cnt += 1
            notebook.append_page(vpaned)
            vpaned.area.set_tablabel()'''

        '''if cnt == 0:
            if(config.conf.verbose):
                print "Loading session in", os.getcwd()
            fcnt = config.conf.sql.get_int("cnt")

            # Load old session
            for nnn in range(fcnt):
                ss = "/sess_%d" % nnn
                fff = config.conf.sql.get_str(ss)

                if(config.conf.verbose):
                    print "Loading file:", fff

                vpaned = edPane()
                ret = vpaned.area.loadfile(fff)
                if not ret:
                    self.update_statusbar("Cannot read file '{0:s}'".format(fff))
                    continue
                    #vpaned.area2.loadfile(fff)

                notebook.append_page(vpaned)
                vpaned.area.set_tablabel()
        '''
        # Show newly created buffers:
        self.mywin.show_all()

        # Set last file
        fff = config.conf.sql.get_str("curr")

        #print "curr file", fff
        cc = notebook.get_n_pages()
        for mm in range(cc):
            vcurr = notebook.get_nth_page(mm)
            if vcurr.area.fname == fff:
                #print "found buff", fff
                notebook.set_current_page(mm)
                self.mywin.set_focus(vcurr.vbox.area)
                break

        # Set the signal handler for 1s tick
        #signal.signal(signal.SIGALRM, handler_tick)
        #signal.alarm(1)
        
        # We use gobj instead of SIGALRM, so it is more multi platform
        GLib.timeout_add(self.timeout, self.handler_tick)

        self.update_statusbar("Initial")
        
        # Add to accounting:
        self.start_time = time.time()
        #timesheet("Started pyagvsim", self.start_time, 0)

    # --------------------------------------------------------------------

    def add_mru(self, merge, action_group, fname, mru):

        if not fname:
            return

        sname = os.path.basename(fname)

        #Gtk.Action(name, label, tooltip, stock_id)
        ac = Gtk.Action(mru, sname, fname, None)
        ac.connect('activate', self.activate_action)
        action_group.add_action(ac)
        merge_id = merge.new_merge_id()
        #add_ui(merge_id, path, name, action, type, top)
        #merge.add_ui(merge_id, "/MenuBar/FileMenu/SaveAs", \
        #            mru, mru, Gtk.UI_MANAGER_MENUITEM, False)

    def area_winstate(self, arg1, arg2):
        pass
        #print "area_winstate", arg1, arg2
        #print "state", self.mywin.get_state()

    def unmap(self, arg1, arg2):
        #print "unmap", arg1, arg2
        pass

    def tree_sel_row(self, xtree):
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            xstr = xmodel.get_value(xiter, 0)
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        #vcurr.area.locate(xstr)

    def tree_sel_row2(self, xtree):
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        xstr = xmodel.get_value(xiter, 0)
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        vcurr.area.locate(xstr)

    def tree_sel(self, xtree, xiter, xpath):
        pass
        print("tree_sel", xtree, xiter, xpath)
        # Focus on main doc
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        self.mywin.activate_focus()
        self.mywin.set_focus(vcurr.vbox.area)

    def tree_sel2(self, xtree, xiter, xpath):
        pass
        print("tree_sel2", xtree, xiter, xpath)
        # Focus on main doc
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        self.mywin.activate_focus()
        self.mywin.set_focus(vcurr.vbox.area)

    # Call key handler
    def area_key(self, area, event):
        print("edWin key", event)
        # Inspect key press before treeview gets it
        if self.mywin.get_focus() == self.treeview:
            # Do key down:
            if  event.type == Gdk.EventType.KEY_PRESS:
                if event.keyval == Gtk.keysyms.Alt_L or \
                        event.keyval == Gtk.keysyms.Alt_R:
                    self.alt = True;

                if event.keyval >= Gtk.keysyms._1 and event.keyval <= Gtk.keysyms._9:
                    #print "edWin Alt num", event.keyval - Gtk.keysyms._1
                     # Focus on main doc
                    vcurr = notebook.get_nth_page(notebook.get_current_page())
                    self.mywin.set_focus(vcurr.vbox.area)

            elif  event.type == Gdk.EventType.KEY_RELEASE:
                if event.keyval == Gtk.keysyms.Alt_L or \
                      event.keyval == Gtk.keysyms.Alt_R:
                    self.alt = False;
                    

    def get_height(self):
        xx, yy = self.mywin.get_size()
        return yy

    def get_width(self):
        xx, yy = self.mywin.get_size()
        return xx

    def start_tree(self):

        global treestore
        if not treestore:
            treestore = Gtk.TreeStore(str)

    def start_tree2(self):

        global treestore2
        if not treestore2:
            treestore2 = Gtk.TreeStore(str)

        # Delete previous contents
        try:
            while True:
                root = treestore.get_iter_first()
                if not root:
                    break
                try:
                    treestore.remove(root)
                except:
                    print("Exception on rm treestore")
        except:
            print("strt_tree", sys.exc_info())
            pass

        piter = treestore.append(None, ["Extracting .."])
        treestore.append(piter, ["None .."])

    # --------------------------------------------------------------------
    def create_tree(self, text = None):

        global treestore
        self.start_tree()

        # create the TreeView using treestore
        tv = Gtk.TreeView(treestore)

        # create a CellRendererText to render the data
        cell = Gtk.CellRendererText()

        # create the TreeViewColumn to display the data
        tvcolumn = Gtk.TreeViewColumn('Virtual Events')

        # add the cell to the tvcolumn and allow it to expand
        tvcolumn.pack_start(cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        tvcolumn.add_attribute(cell, 'text', 0)

        # add tvcolumn to treeview
        tv.append_column(tvcolumn)

        return tv

    # --------------------------------------------------------------------
    def create_vartree(self, text = None):

        global treestore2
        self.start_tree2()

        # create the TreeView using treestore
        tv = Gtk.TreeView(treestore2)

        # create a CellRendererText to render the data
        cell = Gtk.CellRendererText()

        # create the TreeViewColumn to display the data
        tvcolumn = Gtk.TreeViewColumn('Events')

        # add the cell to the tvcolumn and allow it to expand
        tvcolumn.pack_start(cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        tvcolumn.add_attribute(cell, 'text', 0)

        # add tvcolumn to treeview
        tv.append_column(tvcolumn)

        return tv

    # --------------------------------------------------------------------
    def update_treestore(self, text):

        global treestore

        if not treestore: return
        # Delete previous contents
        try:
            while True:
                root = treestore.get_iter_first()
                if not root:
                    break
                try:
                    treestore.remove(root)
                except:
                    print("except: treestore remove")
        except:
            print("update_tree", sys.exc_info())
            pass

        if not text:
            return

        try:
            for line in text:
                piter = treestore.append(None, [cut_lead_space(line)])
        except:
            print("Exception in append treestore", sys.exc_info())
    
        usleep(10)
        vadj = config.conf.mainwin.treeview.get_vadjustment()
        vadj.set_value(vadj.get_upper())
            
    # --------------------------------------------------------------------
    def update_treestore2(self, text):

        global treestore2

        if not treestore2: return
        # Delete previous contents
        try:
            while True:
                root = treestore2.get_iter_first()
                if not root:
                    break
                try:
                    treestore2.remove(root)
                except:
                    print("except: treestore remove")
        except:
            print("update_tree2", sys.exc_info())
            pass

        if not text:
            return

        try:
            for line in text:
                piter = treestore2.append(None, [cut_lead_space(line)])
        except:
            print("Exception in append treestore2", sys.exc_info())

        usleep(10)
        vadj = config.conf.mainwin.treeview2.get_vadjustment()
        vadj.set_value(vadj.get_upper())


    # --------------------------------------------------------------------
    # Handlers: (deactivated)

    def area_event(self, win, act):
        pass
        #print  "edWin area event", win, act

    def area_leave(self, win, act):
        pass
        #print  "edWin area leave", win, act

    def area_enter(self, win, act):
        pass
        #print  "edWin area enter", win, act

    def area_focus(self, win, act):
        pass
        #print  "edWin area focus", win, act

    def area_focus_in(self, win, act):
        #print  "area focus in", win, act
        # This was needed as pygtk leaves the alt key hanging
        #config.conf.keyh.reset()
        # Focus on main doc
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        if vcurr:
            self.mywin.set_focus(vcurr.vbox.area)

    def area_focus_out(self, win, act):
        pass
        #print  "area focus out", win, act

    def area_resize(self, win, rect):
        #print  "area resize", rect
        pass

    def area_size(self, win, rect):
        #print  "area size", rect
        self.hpane2.set_position(self.get_width() - 280)

    def  note_focus_in(self, win, act):
        pass
        #print "note_focus_in", win, act
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        if vcurr:
            self.mywin.set_focus(vcurr.vbox.area)

    def note_enter_notify(self, win):
        pass
        #print "note_enter_notify", win

    def  note_grab_focus_cb(self, win):
        #print "note_grab_focus_cb", win
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        if vcurr:
            self.mywin.set_focus(vcurr.vbox.area)

    def  note_swpage_cb(self, tabx, page, num):
        #print "note_swpage", num
        vcurr = tabx.get_nth_page(num)
        self.mywin.set_title("pyagvsim: " + vcurr.area.fname);
        self.mywin.set_focus(vcurr.vbox.area)
        fname = os.path.basename(vcurr.area.fname)
        self.update_statusbar("Switched to '{1:s}'".format(num, fname))

    def  note_page_cb(self, tabx, child, num):
        pass
        #print "note_page"

    def note_focus_cb(self, tabx, foc):
        #print "note_focus_cb"
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        if vcurr:
            self.mywin.set_focus(vcurr.vbox.area)

    def note_create_cb(self, tabx, page, xx, yy):
        pass
        #print "note_create"

    # Devhelp Message handler
    def activate_dhelp(self, action):
        self.update_statusbar("Showing DevHelp")
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        if vcurr2:
            config.conf.keyh.act.f2(vcurr2.area)

    # Devhelp Message handler
    def activate_khelp(self, action):
        self.update_statusbar("Showing Keyboard Help")
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        if vcurr2:
            config.conf.keyh.act.f3(vcurr2.area)

    def activate_qhelp(self, action):
        self.update_statusbar("Showing quick help")
        rr = get_exec_path("QHELP")
        try:
            if platform.system().find("Win") >= 0:
                xxx = get_exec_path(".." + os.sep + "pangview.py")
                print(xxx, rr)
                ret = subprocess.Popen(["python", xxx,  rr])
            else:            
                ret = subprocess.Popen(["pangview.py",  rr])
        except:
            pedync.message("\n   Cannot launch the pangview.py utility.   \n\n"
                           "              (Please install)")
                           
    def activate_about(self, action):
        self.update_statusbar("Showing About Dialog")
        pedync.about(self)

    def newfile(self, newname = ""):
    
        if newname == "":
            # Find non existing file
            cnt = self.fcount + 1; fff = ""
            base, ext = os.path.splitext(config.conf.UNTITLED)
            while True:
                fff =  "%s_%d.txt" % (base, cnt)
                #print fff
                if not os.path.isfile(fff):
                    break;
                cnt += 1
    
            self.fcount = cnt
        else: 
            fff = newname
            # Touch
            try:
                open(fff, "w").close()
            except:
                sss = "Cannot create file %s" % newname
                self.update_statusbar(sss)
                print(sss,  sys.exc_info()) 
                pedync.message("\n" + sss + "\n")
                return
        
        vpaned = edPane([])
        vpaned.area.fname = os.path.realpath(fff) + ""
        global notebook
        notebook.append_page(vpaned)
        vpaned.area.set_tablabel()

        #label = Gtk.Label(" " + os.path.basename(aa) + " ")
        #notebook.set_tab_label(vpaned, label)
        self.mywin.show_all()

        # Make it current
        nn = notebook.get_n_pages();
        if nn:
            vcurr = notebook.set_current_page(nn-1)
            vcurr = notebook.get_nth_page(nn-1)
            self.mywin.set_focus(vcurr.vbox.area)

    # Traditional open file
    def open(self):
        return
        but =   "Cancel", Gtk.ButtonsType.CANCEL,\
         "Open File", Gtk.ButtonsType.OK
        fc = Gtk.FileChooserDialog("Open file", self.mywin, \
             Gtk.FileChooserAction.OPEN  \
            #Gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
            , but)
        fc.set_default_response(Gtk.ButtonsType.OK)
        fc.set_current_folder(os.getcwd())
        fc.connect("response", self.done_open_fc)
        fc.connect("current-folder-changed", self.folder_ch )

        #fc.set_current_name(self.fname)
        fc.run()

    def save(self, flag = False):
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        if flag:
            vcurr.area.saveas()
        else:
            vcurr.area.save()

    def copy(self):
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        if vcurr2:
            config.conf.keyh.act.ctrl_c(vcurr2.area)

    def cut(self):
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        if vcurr2:
             config.conf.keyh.act.ctrl_x(vcurr2.area)

    def paste(self):
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        if vcurr2:
            config.conf.keyh.act.ctrl_v(vcurr2.area)

    def log_txt(self, txt):
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        if vcurr:
            vcurr.append_tv(txt)
                    
    def log_txt2(self, txt):
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        if vcurr:
            vcurr.append_tv2(txt)
            
    def log_clear(self):
        vcurr = notebook.get_nth_page(notebook.get_current_page())
        if vcurr:
            vcurr.clear_tvs()
    # -------------------------------------------------------------------
    # Menu callback

    def activate_action(self, action):

        #dialog = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT,
        #    Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE,
        #    'Action: "%s" of type "%s"' % (action.get_name(), type(action)))
        # Close dialog on user response
        #dialog.connect ("response", lambda d, r: d.destroy())
        #dialog.show()

        #warnings.simplefilter("ignore")
        strx = action.get_name()
        #warnings.simplefilter("default")
        #print "activate_action", strx

        if strx == "New":
            self.newfile();

        if strx == "Open":
            self.open()

        if strx == "Save":
            self.save()

        if strx == "SaveAs":
            self.save(True)

        if strx == "Close":
            self.closedoc()

        if strx == "Copy":
            self.copy()

        if strx == "Cut":
            self.cut()

        if strx == "Paste":
            self.paste()

        if strx == "Goto":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.alt_g(vcurr2.area)

        if strx == "Find":
            #print "find"
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.ctrl_f(vcurr2.area)

        if strx == "Record":
            #print "record"
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.f7(vcurr2.area)

        if strx == "Play":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.f8(vcurr2.area)

        if strx == "Spell":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.f9(vcurr2.area)

        if strx == "Spell2":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.f9(vcurr2.area, True)

        if strx == "Animate":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.f8(vcurr2.area, True)

        if strx == "Undo":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.ctrl_z(vcurr2.area)

        if strx == "Redo":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.ctrl_y(vcurr2.area)

        if strx == "SaveAll":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.alt_a(vcurr2.area)

        if strx == "Discard Undo":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                vcurr2.area.delundo()

        if strx == "Savemacro":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                vcurr2.area.savemacro()

        if strx == "Loadmacro":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                vcurr2.area.loadmacro()

        if strx == "NextWin":
            self.nextwin()

        if strx == "PrevWin":
            self.prevwin()

        if strx == "ShowLog":
            log.show_log()

        if strx.find("/sess_") >= 0:
            fname = config.conf.sql.get_str(strx)
            self.openfile(fname)

        if strx == "Colors":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                pedcolor.colors(self, vcurr2.area)

        if strx == "Fonts":
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                pedfont.selfont(self, vcurr2.area)

        if strx == "Settings":
            pedync.message("\n    Settings: Work in progress    \n")

        if strx == "Help":
            #pedync.message("\n    Help: Work in progress    \n")
            nn2 = notebook.get_current_page()
            vcurr2 = notebook.get_nth_page(nn2)
            if vcurr2:
                config.conf.keyh.act.f1(vcurr2.area)

        if strx == "KeyDoc":
            self.update_statusbar("Showing Keyboard Help")
            fname = get_exec_path("KEYS.TXT")
            self.openfile(fname)
        
    def closedoc(self, other = None):
        #print("closedoc")
        cc = notebook.get_n_pages()
        if other:
            for aa in range(cc):
                vcurr = notebook.get_nth_page(aa)
                if vcurr.area == other:
                    notebook.set_current_page(aa)
                    break
        nn = notebook.get_current_page()
        vcurr = notebook.get_nth_page(nn)
        
        # Disable close
        if vcurr.area.closedoc():
            return

        # Wrap around if closed first
        if nn == 0: mm = cc - 1
        else:       mm = nn - 1

        notebook.set_current_page(mm)
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        self.mywin.set_focus(vcurr2.vbox.area)
        #vcurr2.area.destroy()
        #usleep(10)
        notebook.remove_page(nn)
        #usleep(10)
        
        self.mywin.show_all()
        

    def  firstwin(self):
        cc = notebook.get_n_pages()
        if cc == 0:
            return
        notebook.set_current_page(0)
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        self.mywin.set_focus(vcurr2.vbox.area)
        self.mywin.show_all()

    def  lastwin(self):
        cc = notebook.get_n_pages()
        if cc == 0:
            return
        notebook.set_current_page(cc-1)
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        self.mywin.set_focus(vcurr2.vbox.area)
        self.mywin.show_all()

    def  nextwin(self):
        cc = notebook.get_n_pages()
        nn = notebook.get_current_page()
        vcurr = notebook.get_nth_page(nn)

        # Wrap around if needed
        if nn == cc - 1: mm = 0
        else:       mm = nn + 1
        notebook.set_current_page(mm)
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        self.mywin.set_focus(vcurr2.vbox.area)
        self.mywin.show_all()

    def  prevwin(self):
        cc = notebook.get_n_pages()
        nn = notebook.get_current_page()
        vcurr = notebook.get_nth_page(nn)

        # Wrap around if needed
        if nn == 0: mm = cc - 1
        else:       mm = nn - 1
        notebook.set_current_page(mm)
        nn2 = notebook.get_current_page()
        vcurr2 = notebook.get_nth_page(nn2)
        self.mywin.set_focus(vcurr2.vbox.area)
        self.mywin.show_all()

    def folder_ch(self, win):
        #print "folder_ch"
        pass
        #return True

    def done_open_fc(self, win, resp):
        #print "done_open_fc", win, resp
        if resp == Gtk.ButtonsType.OK:
            fname = win.get_filename()
            if not fname:
                #print "Must have filename"
                self.update_statusbar("No filename specified")
                pass
            elif os.path.isdir(fname):
                self.update_statusbar("Changed to %s" % fname)
                os.chdir(fname)
                win.set_current_folder(fname)
                return
            else:
                self.openfile(fname)
        win.destroy()

    def saveall(self):
        #print "saveall"
        # Save all files
        nn = notebook.get_n_pages(); cnt = 0; cnt2 = 0
        while True:
            if cnt >= nn: break
            ppp = notebook.get_nth_page(cnt)
            if ppp.area.changed:
                ppp.area.writefile()
                cnt2 += 1
            cnt += 1

        self.update_statusbar("%d of %d buffers saved." % (cnt2, nn))

    # -------------------------------------------------------------------
    def openfile(self, fname):
        return
        # Is it already loaded? ... activate
        nn = notebook.get_n_pages();
        for aa in range(nn):
            vcurr = notebook.get_nth_page(aa)
            if vcurr.area.fname == fname:
                self.update_statusbar("Already open, activating '{0:s}'".format(fname))
                vcurr = notebook.set_current_page(aa)
                vcurr = notebook.get_nth_page(aa)
                self.mywin.set_focus(vcurr.vbox.area)
                return

        if(config.conf.verbose):
            print("Opening '"+ fname + "'")
            
        self.update_statusbar("Opening file '{0:s}'".format(fname))
        vpaned = edPane()
        ret = vpaned.area.loadfile(os.path.realpath(fname))
        if not ret:
            self.update_statusbar("Cannot read file '{0:s}'".format(fname))
            return
        #vpaned.area2.loadfile(os.path.realpath(fname))
        self.update_statusbar("Opened file '{0:s}'".format(fname))
        
        # Add to the list of buffers
        notebook.append_page(vpaned)
        vpaned.area.set_tablabel()
        self.mywin.show_all()
        # Make it current
        nn = notebook.get_n_pages();
        if nn:
            vcurr = notebook.set_current_page(nn-1)
            vcurr = notebook.get_nth_page(nn-1)
            self.mywin.set_focus(vcurr.vbox.area)

    def activate_exit(self, action = None):
        #print "activate_exit called"
        OnExit(self.mywin)

    def activate_quit(self, action):
        #print "activate_quit called"
        OnExit(self.mywin, False)

    def activate_radio_action(self, action, current):
        active = current.get_active()
        value = current.get_current_value()

        if active:
            dialog = Gtk.MessageDialog(self, Gtk.DIALOG_DESTROY_WITH_PARENT,
                Gtk.MESSAGE_INFO, Gtk.ButtonsType.CLOSE,
                "You activated radio action: \"%s\" of type \"%s\".\nCurrent value: %d" %
                (current.get_name(), type(current), value))

            # Close dialog on user response
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.show()

    # This is the line count / pos status bar
    def update_statusbar2(self, xx = 0, yy = 0, ins = 0, tlen = 0, clip = 0):
        # Always update line / col
        if ins: str2 = "INS"
        else: str2 ="OVR"
        strx2 = "Ln {0:d} Col {1:d} Tot {3:d}  {2:s} Clip {4:d}".\
                                format(yy+1, xx+1, str2, tlen, clip)

        self.slab2.set_text(strx2)
        #self.statusbar2.pop(0)
        #self.statusbar2.push(0, strx2)

    def update_statusbar(self, strx):
        # Clear any previous message, underflow is allowed
        #self.statusbar.pop(0)
        if not strx:
            self.update_statusbar("Idle")
            return

        self.slab.set_text(strx)
        
        #self.statusbar.push(0, strx)
        self.statuscount = STATUSCOUNT
        pass

    def update_resize_grip(self, widget, event):
        #print "update state", event, event.changed_mask
        #self.mywin.set_focus(notebook)

        mask = Gdk.WindowState.MAXIMIZED
        # | Gdk.FULLSCREEN
        if (event.changed_mask & mask):
            self.statusbar.set_has_resize_grip(not (event.new_window_state & mask))


    def handler_tick(self):
    
        global notebook
    
        #mained.append("testing2\n")
        #print "handler_tick"
        
        try:
            vcurr = notebook.get_nth_page(notebook.get_current_page())
                    
            #print 'Signal handler called with signal'
            #print config.conf.idle, config.conf.syncidle
            
            if config.conf.idle:
                config.conf.idle -= 1
                if config.conf.idle == 0:
                    vcurr = notebook.get_nth_page(notebook.get_current_page())
                    # Rescue to save:
                    if vcurr:
                        vcurr.area.source_id = \
                            GLib.idle_add(vcurr.area.idle_callback)
    
            if config.conf.syncidle:
                config.conf.syncidle -= 1
                if config.conf.syncidle == 0:
                    vcurr = notebook.get_nth_page(notebook.get_current_page())
                    if vcurr:
                        #pedspell.spell(vcurr.area)
                        vcurr.area.source_id2 = \
                        GLib.idle_add(vcurr.area.idle_callback2)
                        '''if len(vcurr.area2.text) == 0:
                            vcurr.area2.text = vcurr.area.text
                            vcurr.area2.fname = vcurr.area.fname
                            vcurr.area2.set_maxlines()
                            vcurr.area2.set_maxlinelen()'''
    
                        if vcurr.area.changed:
                            '''vcurr.area2.text = vcurr.area.text
                            vcurr.area2.set_maxlines(0)
                            vcurr.area2.invalidate()'''
                            pass
    
            if config.conf.mainwin.statuscount:
                config.conf.mainwin.statuscount -= 1
                #print config.conf.mainwin.statuscount 
            else:
               config.conf.mainwin.update_statusbar("")
            
            if vcurr:           
                #print  vcurr.area.agvs[0]
                vcurr.area.heartbeat()
                #move_agvs()
            
        except:
            #print "Exception in timer handler", sys.exc_info()
            print(exc_str("In timer handler: "))
            pass
    
        try:
            GLib.timeout_add(self.timeout, self.handler_tick)
        except:
            print("Exception in setting timer handler", sys.exc_info())
 
# ------------------------------------------------------------------------

def OnExit(arg, prompt = True):

    arg.set_title("Exiting ...")

    # Save UI related data
    pos = mained.hpaned.get_position()
    pos = max(pos, 1)

    config.conf.sql.put("hpaned", pos)

    vcurr = notebook.get_nth_page(notebook.get_current_page())
    if vcurr:
        pos = vcurr .get_position()
        pos = max(pos, 1)

        config.conf.sql.put("vpaned", pos)

    # Do not save full screen coordinates (when used F11)
    #print mained.full

    if not mained.full:
        xx, yy = mained.mywin.get_position()

        config.conf.sql.put("xx", xx)
        config.conf.sql.put("yy", yy)

        ww, hh = mained.mywin.get_size()

        config.conf.sql.put("ww", ww)
        config.conf.sql.put("hh", hh)

    # Save current doc:
    vcurr = notebook.get_nth_page(notebook.get_current_page())
    if vcurr:
        config.conf.sql.put("curr", vcurr.area.fname)

    # Prompt for save files
    nn = notebook.get_n_pages(); cnt = 0
    while True:
        if cnt >= nn: break
        ppp = notebook.get_nth_page(cnt)
        #print "page:", ppp.area
        ppp.area.saveparms()

        ss = "/sess_%d" % cnt
        if cnt < 30:
            config.conf.sql.put(ss, ppp.area.fname)

        if prompt:
            if ppp.area.changed:
                msg = "\nWould you like to save:\n\n  \"%s\" \n" % ppp.area.fname
                rp = pedync.yes_no_cancel("pyagvsim: Save File ?", msg)

                if rp == Gtk.ResponseType.YES:
                    ppp.area.save()

                if rp == Gtk.ResponseType.NO:
                    #print "Gtk.RESPONSE_NO"
                    pass
                if  rp == Gtk.ResponseType.CANCEL or \
                    rp == Gtk.ResponseType.REJECT or \
                    rp == Gtk.ResponseType.CLOSE  or \
                    rp == Gtk.ResponseType.DELETE_EVENT:
                    return
        else:
            # Rescue to temporary:
            if ppp.area.changed:
                hhh = hash_name(ppp.area.fname) + ".rescue"
                xfile = config.conf.config_dir + "/" + hhh
                if(config.conf.verbose):
                    print("Rescuing", xfile)
                writefile(xfile, ppp.area.text)
                
                              
        # This way all the closing doc function gets called
        ppp.area.closedoc()
        cnt += 1
        
    config.conf.sql.put("cnt", cnt)

    if(config.conf.verbose):
        print("Exiting")

    # Add to accounting:
    #timesheet("Ended pyagvsim", mained.start_time, time.time())

    # Kill areas
    nn = notebook.get_n_pages(); cnt = 0
    while True:
        if cnt >= nn: break
        ppp = notebook.get_nth_page(cnt)
        #print "page:", ppp.area
        ppp.area.close_subwins()
        cnt = cnt + 1
        usleep(10)
        
    # Exit here
    Gtk.main_quit()

    #print "OnExit called \"" + arg.get_title() + "\""
                  
# ------------------------------------------------------------------------

   
# EOF




















