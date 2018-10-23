#!/usr/bin/env python

# ------------------------------------------------------------------------

# Python AGV simulator. Requires pyGtk. See pygtk-dependencied for 
# eazy access to depencdencies. 

from __future__ import absolute_import
from __future__ import print_function
import os, sys, getopt, signal

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import pysimlib.config
import pysimlib.sql
import pysimlib.mainwin

mainwin = None
show_timing = 0
show_config = 0
clear_config = 0
use_stdout = 0
  
# ------------------------------------------------------------------------

def main(strarr):

    if(pysimlib.config.conf.verbose):
        print("pytsim running on", "'" + os.name + "'", \
            "GTK", Gtk._version, "PyGtk", \
               "%d.%d.%d" % (Gtk.get_major_version(), \
                    Gtk.get_minor_version(), \
                        Gtk.get_micro_version()))

    signal.signal(signal.SIGTERM, terminate)
    mainwin = pysimlib.mainwin.MainWindow(None, None, strarr)
    
    pysimlib.config.conf.mainwin = mainwin 
    
    '''
    import ctypes
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    SW_HIDE = 0
    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        print ("Console found")
        user32.ShowWindow(hWnd, SW_HIDE)
    '''
        
    Gtk.main()
              
def help():

    print() 
    print("pytsim version: ", pysimlib.config.conf.version)
    print("Usage: " + os.path.basename(sys.argv[0]) + " [options] [[filename] ... [filenameN]]")
    print("Options:")
    print("            -d level  - Debug level 1-10. (Limited implementation)")
    print("            -v        - Verbose (to stdout and log)")
    print("            -f        - Start Full screen")
    print("            -c        - Dump Config")
    print("            -V        - Show version")
    print("            -x        - Clear (eXtinguish) config (will prompt)")
    print("            -h        - Help")
    print()

# ------------------------------------------------------------------------

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
       
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
       
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
       
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

def terminate(arg1, arg2):

    if(pysimlib.config.conf.verbose):
        print("Terminating pytsim.py, saving files to ~/pytsim")
        
    # Save all     
    pysimlib.config.conf.pedwin.activate_quit(None)    
    #return signal.SIG_IGN

# Start of program:

if __name__ == '__main__':

    # Redirect stdout to a fork to real stdout and log. This way messages can 
    # be seen even if pytsim is started without a terminal (from the GUI)
    
    opts = []; args = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h?fvxctVo")
    except getopt.GetoptError as err:
        print("Invalid option(s) on command line:", err)
        sys.exit(1)

    #print "opts", opts, "args", args
    
    pysimlib.config.conf.version = 0.43

    for aa in opts:
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
            except:
                pgdebug = 0

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-?": help();  exit(1)
        if aa[0] == "-V": print("Version", pysimlib.config.conf.version); \
            exit(1)
        if aa[0] == "-f": pysimlib.config.conf.full_screen = True
        if aa[0] == "-v": pysimlib.config.conf.verbose = True            
        if aa[0] == "-x": clear_config = True            
        if aa[0] == "-c": show_config = True            
        if aa[0] == "-t": show_timing = True
        if aa[0] == "-o": use_stdout = True
    
    try:
        if not os.path.isdir(pysimlib.config.conf.config_dir):
            if(pysimlib.config.conf.verbose):
                print("making", pysimlib.config.con.config_dir)
            os.mkdir(pysimlib.config.conf.config_dir)
    except: pass
    
    # Let the user know it needs fixin'
    if not os.path.isdir(pysimlib.config.conf.config_dir):
        print("Cannot access config dir:", pysimlib.config.conf.config_dir)
        sys.exit(1)

    if not os.path.isdir(pysimlib.config.conf.data_dir):
        if(pysimlib.config.conf.verbose):
            print("making", pysimlib.config.con.data_dir)
        os.mkdir(pysimlib.config.conf.data_dir)
         
    if not os.path.isdir(pysimlib.config.conf.log_dir):
        if(pysimlib.config.conf.verbose):
            print("making", pysimlib.config.conf.log_dir)
        os.mkdir(pysimlib.config.conf.log_dir)
    
    if not os.path.isdir(pysimlib.config.conf.macro_dir):
        if(pysimlib.config.conf.verbose):
            print("making", pysimlib.config.conf.macro_dir)
        os.mkdir(pysimlib.config.conf.macro_dir)

    if(pysimlib.config.conf.verbose):
        print("Data stored in ", pysimlib.config.conf.config_dir)
        
    # Initialize sqlite to load / save preferences & other info    
    sql = pysimlib.sql.Sql(pysimlib.config.conf.sql_data)
        
    # Initialize config for use  
    pysimlib.config.conf.sql = sql
    #pysimlib.config.conf.keyh = pysimlib.keyhand.KeyHand()
    pysimlib.config.conf.mydir = os.path.abspath(__file__)

    # To clear all config vars
    if clear_config:    
        print("Are you sure you want to clear config ? (y/n)")
        sys.stdout.flush()
        aa = sys.stdin.readline()
        if aa[0] == "y":
            print("Removing configuration ... ", end=' ')
            sql.rmall()        
            print("OK")
        sys.exit(0)

    # To check all config vars
    if show_config:    
        print("Dumping configuration:")
        ss = sql.getall(); 
        for aa in ss: 
            print(aa)
        sys.exit(0)

    '''
    #Uncomment this for silent stdout
    if use_stdout:
        print "Using stdout"
        sys.stdout = Unbuffered(sys.stdout)
        sys.stderr = Unbuffered(sys.stderr)
    else:
        #sys.stdout = pysimlib.log.fake_stdout()
        #sys.stderr = pysimlib.log.fake_stdout()
        pass
    '''    
    sys.stdout = Unbuffered(sys.stdout)
    sys.stderr = Unbuffered(sys.stderr)
        
    # Uncomment this for buffered output
    if pysimlib.config.conf.verbose:
        print("Started pytsim")
        #pysimlib.log.print("Started pytsim")
     
    main(args[0:])

# EOF




