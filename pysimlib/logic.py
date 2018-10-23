#!/usr/bin/env python

# Drawing operations done here
 
from __future__ import absolute_import
from __future__ import print_function
import signal, os, time, sys, random, math

from .definitions import *
from .utils import *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GdkPixbuf

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

QCAN_IDLE         =   0
QCAN_SEEN_RED     =   1
QCAN_SEEN_BLUE    =   2
QCAN_SEEN_GREEN   =   3

QCAN_STATUS_IDLE    =   10
QCAN_STATUS_LISTEN  =   11
QCAN_STATUS_BULLY   =   12
QCAN_STATUS_RELEASE =   13

# Supporting routined for AGV logic

class Logic(object):   

    def __init__(self):
            
        self.agvs = []; self.poks = []
        self.delta = 5                      # Vehicle moves this many pixels
        self.sumw = []
        self.sumw2 = []
        #self.xdelta = self.delta
        #self.ydelta = self.delta
        self.collision = False
        self.oldcoll   = False
        self.pokevent = "";       self.pokevent2 = ""
        self.speedevent = "";     self.speedevent2 = ""
        self.agvs = [] #init_agvs()
        self.oob = 0
        self.count = 0        
        
    def init_targs(self):
        self.targs = []
        rect = self.get_allocation()
        targ['xxx'] = 6 * rect.width / 8; targ['yyy'] =  5 * rect.height / 16
        self.targs.append(targ)
     
    def init_agvs(self, resize = False):
        rect = self.get_allocation()
        if not resize:
            self.agvs = []
        if not len(self.agvs):
            self.agvs.append(dict(agv_ass))
            #self.agvs.append(dict(agv_ass2))
            #self.agvs.append(dict(agv_ass3))
            #self.agvs.append(dict(agv_ass4))
        
        for aa in range(len(self.agvs)):                
            pbuf = self.agvs[aa]['agv'].get_pixbuf()
            ww =  pbuf.get_width() / 2
            hh =  pbuf.get_height() / 2
            self.agvs[aa]['ww'] = ww; self.agvs[aa]['hh'] = hh
            self.agvs[aa]['pbuf'] = \
                pbuf.scale_simple(ww, hh, GdkPixbuf.InterpType.BILINEAR )
            self.agvs[aa]['oob'] = 0
            self.agvs[aa]['qcan'] = dict(qcan_ass)
            
            #print (self.agvs[aa])
            
        # redo xxx yyy for correct path
        self.agvs[0]['yyy'] = rect.height / 2
        #self.agvs[1]['xxx'] = rect.width / 2
        #self.agvs[3]['yyy'] = rect.height
        
        #self.agvs[0]['xxx'] = 0
        #self.agvs[1]['yyy'] = 0
            
    def update_states(self):
        #self.qcan_1.update_state()
        #self.qcan_2.update_state()
        #self.qcan_3.update_state()
        #self.qcan_4.update_state()
        pass
        
    def heartbeat(self):
        #print "heartbeat"
        if self.stop:
            return
                       
        self.count += 1
            
        self.move_agvs()
        
        # Evaluate state machine 
        self.eval_sim()
        
        # Stages of simulation
        self.listener()
        self.broadcaster()
        self.update_states()
        
        # Paint what we got
        self.invalidate()
        
    # Swish back and forth       
    def move_agvs(self):
        rect = self.get_allocation()
        aspect = float(rect.width) / rect.height
        #print ("aspect", aspect)
                
        # move the agvs with vector
        for aa in self.agvs:
            #print (aa)
            if aa['go']:
                fact = 0.; 
                xx = aa['xxx']; yy = aa['yyy']
                if aa['qcan']['speed'] == 2:
                    fact = 2
                if aa['qcan']['speed'] == 1:
                    fact = 1
        
                # if both vectors are set, calc diagonal speed
                if aa['vector'][0] != 0 and aa['vector'][1] != 0:
                    fact = fact * 2
                    
                aa['xxx'] = fact * aspect * aa['vector'][0] + xx
                aa['yyy'] = fact * aa['vector'][1] + yy
        
        # move the targs
        for aa in self.targs:
            #print (aa)
            xx = aa['xxx']; yy = aa['yyy']
            aa['xxx'] = aspect * aa['vector'][0] + xx
            aa['yyy'] = aa['vector'][1] + yy
            
        # See if game over
        for aa in self.agvs:
            xx2 = aa['xxx']
            yy2 = aa['yyy']
            if xx2 > rect.width or yy2 > rect.height: 
                aa['oob'] = 1 
            if xx2 < 0 or yy2 < 0: 
                aa['oob'] = 1 
          
        xx = self.targs[0]['xxx']; yy = self.targs[0]['yyy']
        #self.appwin.log_txt("targx %d targy %d" % (xx, yy))
        
        xxx = aa['xxx']; yyy =  aa['yyy']
        self.appwin.log_txt("xxx %d yyy %d" % (xxx, yyy))
        
        dx = xx-xxx; dy = yy-yyy
        
        dia = math.sqrt(dx * dx + dy * dy)
        rat = float(dx) / dia
        self.appwin.log_txt("dx %d dy %d rat %0.4f" % (dx, dy, rat))
        
        v1 = self.agvs[0]['vector'][0]
        v2 = self.agvs[0]['vector'][1]
        
        rat2 = v1 / math.sqrt(v1*v1+ v2*v2)
        
        uv  = unit_vector(v1, v2); uv2 = unit_vector(dx, dy)
        
        #print("unit vec %0.4f  %0.4f  %0.4f  %0.4f " %  
        #                        (uv[0], uv[1], uv2[0], uv2[1]  ))
            
        uv3 = merge_unit_vectors(uv, uv2)
        
        #print("unit vec3 %0.4f  %0.4f " %  
        #                        ( uv3[0], uv3[1]  ))
        
        self.appwin.log_txt("vecx %d vecy %d rat2 %0.4f" %
                        (v1, v2, rat2) )
        
        if self.count > 10:
            self.agvs[0]['vector'] = uv3
        
        # Count out of bound vehicles
        oobcnt = 0  
        for aa in self.agvs:
            if aa['oob']:
                oobcnt = oobcnt + 1
        if oobcnt > 0:     
            self.restart_sim()
            
        
    # Look all the AGV rectangles, see if collision occured
    def eval_collision(self):
        coll = False
        for aa, cc in self.agvrectarr:
            for bb, dd in self.agvrectarr:
                if aa != bb:
                    if aa.intersect(bb)[0]:
                        coll = True
                        break
        # Commit collision info
        self.collision = coll
        
    # --------------------------------------------------------------------
    # This is where the events end up ...
    
    def eval_sim(self):
    
        #rect = self.get_allocation()
        #print "initial", rect.x, rect.y, rect.width, rect.height
        
        # Build current state of rectangles
        self.agvrectarr = []
        for aa in self.agvs:
            pbuf = aa['agv'].get_pixbuf()
            ww =  aa['ww']; hh =  aa['hh']
            xx = aa['xxx']; yy = aa['yyy'] 
            crect = Gdk.Rectangle()
            crect.x = xx - ww / 2; crect.y = yy - hh / 2
            crect.width = ww / 2; crect.height = hh / 2
            #print (crect.x, crect.y, crect.width, crect.height)
            self.agvrectarr.append((crect, aa))
        
        # Generate pok events
        '''for rr in self.pokrectarr:
            for aa, bb in agvrectarr:
                if aa.intersect(rr[0])[0]:
                    #ev = "AGV %d Color: %s Zone: %d" % (bb['num'], rr[1]['color'], rr[1]['zone'])
                    #print (ev)
                    #if  ev != self.pokevent:
                    #self.pokevent = ev
                    #self.sumw.append(self.pokevent)
                    
                    self.evel_poks(rr, bb)
        '''
        
        # Step through state machine events
        for aa in self.agvs:
            self.eval_states(aa)
                                                                  
        '''                      
        try:        
            self.appwin.update_treestore(self.sumw)
        except:
            # This is normal, ignore it
            print("run_async_time", sys.exc_info())    
            pass
        try:        
            self.appwin.update_treestore2(self.sumw2)
        except:
            # This is normal, ignore it
            print("run_async_time", sys.exc_info())    
            pass
        '''
        
    def restart_sim(self):
        self.mained.update_statusbar("Restarting simlation.")
        
        self.oob = 0
        self.poks = []; self.agvs = []
        self.init_agvs(); 
        self.init_targs()
        
        self.sumw = []; self.pokevent = ""
        self.sumw2 = []; self.pokevent2 = ""
        self.appwin.log_clear()
        # Deliver one heartbeat to display updates
        self.heartbeat()
        #self.xdelta = self.delta + random.randint(0, +3)
        #self.decor_1.qcan_1.set_text("COMS OK")
        #self.decor_1.qcan_2.set_text("AGV #%d" % 1);
        
        #self.decor_2.qcan_1.set_text("COMS OK")
        #self.decor_2.qcan_2.set_text("AGV #%d" % 2);
        #
        #self.decor_3.qcan_1.set_text("COMS OK")
        #self.decor_3.qcan_2.set_text("AGV #%d" % 2);
        #
        #self.decor_4.qcan_1.set_text("COMS OK")
        #self.decor_4.qcan_2.set_text("AGV #%d" % 2);
        #
        #self.qlcd.set_sser(0, "\  %02x  %02x  %02x  %02x  " % (0, 0, 0, 0))
        #self.qlcd.set_sser(1, "\  %02x  %02x  %02x  %02x  " % (0, 0, 0, 0))
        #
        #self.qlcd.set_rser(0, "\  %02x  %02x  %02x  %02x  " % (0, 0, 0, 0))
        #self.qlcd.set_rser(1, "\  %02x  %02x  %02x  %02x  " % (0, 0, 0, 0))

        #self.radio.deltree()
        #self.stop = False
    
    def toggle_sim(self):
        if self.stop:
            self.mained.update_statusbar("Starting simulation.")
            self.stop = False
        else:
            self.mained.update_statusbar("Stopping simulation.")
            self.stop = True
    
    def stop_sim(self):
        self.mained.update_statusbar("Stopping simulation.")
        self.stop = True
    
    def toggle_1(self):
        if self.agvs[0]['go'] == 0:
            self.mained.update_statusbar("Started AGV 1.")
            self.agvs[0]['go'] = 1
        else:
            self.mained.update_statusbar("Stopped AGV 1.")
            self.agvs[0]['go'] = 0
        
    def toggle_2(self):
        if self.agvs[1]['go'] == 0:
            self.mained.update_statusbar("Started AGV 2.")
            self.agvs[1]['go'] = 1
        else:
            self.mained.update_statusbar("Stopped AGV 2.")
            self.agvs[1]['go'] = 0
            
    def toggle_3(self):
        if self.agvs[2]['go'] == 0:
            self.mained.update_statusbar("Started AGV 3.")
            self.agvs[2]['go'] = 1
        else:
            self.mained.update_statusbar("Stopped AGV 3.")
            self.agvs[2]['go'] = 0
    
    def toggle_4(self):
        if self.agvs[3]['go'] == 0:
            self.mained.update_statusbar("Started AGV 4.")
            self.agvs[3]['go'] = 1
        else:
            self.mained.update_statusbar("Stopped AGV 4.")
            self.agvs[3]['go'] = 0
    
    def cont_sim(self):
        self.mained.update_statusbar("Continuing simulation.")
        self.stop = False

        
    # Ideally, this is what the radio will do    
    def evel_poks(self, rr, bb):
        if rr[1]['color'] == 'red':
            bb['qcan']['seen']  = QCAN_SEEN_RED
            bb['qcan']['seenzone'] = rr[1]['zone']
    
        if rr[1]['color'] == 'blue':
            bb['qcan']['seen'] = QCAN_SEEN_BLUE
            bb['qcan']['seenzone'] = rr[1]['zone']
            
        if rr[1]['color'] == 'green':
            bb['qcan']['seen'] = QCAN_SEEN_GREEN
            bb['qcan']['seenzone'] = rr[1]['zone']

    # --------------------------------------------------------------------
    def eval_states(self, bb):
    
        '''logfunc = self.appwin.log_txt2
        event = "none"
        if rr[1]['color'] == 'red':
            event = "Anticipate Intersection"
        if rr[1]['color'] == 'blue':
            event = "Occupy Intersection"
        if rr[1]['color'] == 'green':
            event = "Release Intersection"
        logfunc("AGV_%d Event: %s (%s) Zone %d  Zone: %d Coords: %d:%d" %  
                  (bb['num'], event, rr[1]['color'], rr[1]['zone'],  
                          bb['zone'], rr[0].x, rr[0].y))
        '''
            
        # Examine changes in poks
        if bb['qcan']['seen'] != bb['qcan']['oldseen']:
        
            ttt = "AGV %d - seen event: %d  zone: %d " % \
                            (bb['num'], bb['qcan']['seen'], bb['qcan']['seenzone'])
            self.appwin.log_txt(ttt)
            
            # Event generated!
            bb['qcan']['oldseen'] =  bb['qcan']['seen'] 
            
            # RED POK ----------------------------------------------------
            if bb['qcan']['seen'] == QCAN_SEEN_RED:
            
                # Only change zones if idle
                if bb['qcan']['status'] == QCAN_STATUS_IDLE:
                    bb['qcan']['currzone']  = bb['qcan']['seenzone']
                    bb['qcan']['scancnt'] = 10
                    bb['qcan']['status'] = QCAN_STATUS_LISTEN
                    
                    self.sumw2.append("AGV_%d started listening" % bb['num'])
                    strxx = "INTER Z%d" % bb['qcan']['currzone']
                    strgo = "AGV V%d" % (bb['num'])
                    self.qlcd.set_lcdx(bb['num']-1, "SCAN", strxx, "GO", strgo)
                    
                    self.qlcd.set_sser(bb['num']-1, "\  %02x  %02x  %02x  %02x  " % 
                                        (0x81, bb['qcan']['currzone'], bb['num'], 0))
                                        
                    self.qlcd.set_rser(bb['num']-1, "\  %02x  %02x  %02x  %02x  " % 
                                        (0x01, bb['qcan']['currzone'], bb['num'], 0))
                  
                                    
            # BLUE POK ---------------------------------------------------
            if bb['qcan']['seen'] == QCAN_SEEN_BLUE:
            
                # Anyone broadcastig?
                bcast = 0
                for aa in self.agvs:
                    if aa['qcan']['status'] == 2:  
                        bcast =  aa
                        break
                if bcast:          
                    # Add to list
                    bb['qcan']['contester']  = aa
                    
                else:
                    # no broadcast, start one
                    bb['qcan']['status'] = QCAN_STATUS_BULLY
                    
                    self.sumw.append("AGV_%d started broadcasting" % bb['num'])
                    self.sumw2.append("AGV_%d started broadcasting" % bb['num'])
                
                    self.qlcd.set_sser(bb['num']-1, "\  %02x  %02x  %02x  %02x  " % 
                        (0x81, bb['qcan']['currzone'], bb['num'], 0xff))

                    self.qlcd.set_rser(bb['num']-1, "\  %02x  %02x  %02x  %02x  " % 
                        (0x01, bb['qcan']['currzone'], bb['num'], 0xff))
                        
                    strxx = "INTER Z%d" % bb['qcan']['currzone']
                    strgo = "AGV V%d" % bb['num']
                    self.qlcd.set_lcdx(bb['num']-1, "REQUEST", strxx, "GO", strgo)
        
            
            # GREEN POK ---------------------------------------------------
            if bb['qcan']['seen'] == QCAN_SEEN_GREEN:
                # Release waiting one
                if bb['qcan']['status'] == QCAN_STATUS_BULLY:
                    self.sumw.append("AGV_%d stopped broadcasting" % bb['num'])
                    self.sumw2.append("AGV_%d stopped broadcasting" % bb['num'])
                
                    self.qlcd.set_sser(bb['num']-1, "\  %02x  %02x  %02x  %02x  " % 
                                (0x82, bb['qcan']['currzone'], bb['num'], 0x00))
    
                    self.qlcd.set_rser(bb['num'], "\  %02x  %02x  %02x  %02x  " % 
                                (0x02, bb['qcan']['currzone'], bb['num'], 0x00))
                
                    strxx = "INTER Z%d" % rr[1]['zone']
                    strgo = "AGV V%d" % bb['num']
                    self.qlcd.set_lcdx(bb['num']-1, "LEAVE", strxx, "GO", strgo)
                        
                    #self.radio.broadcast(agv, "AGV %d: " % (agv + 1),\
                    #                        "LEAVE" + " " + strxx)
                    #self.agvs[agv]['qcan']['currzone'] =  -1
                    #self.rm_contester(agv, agv)
                    #self.agvs[agv]['contester'] =  -1
                        
                bb['qcan']['status'] = QCAN_STATUS_RELEASE
                bb['qcan']['relcnt'] = 10
                    
    # --------------------------------------------------------------------
    def listener(self):
        # Execute listen to any bradcasts
        for aa in self.agvs:
            if aa['qcan']['status'] == 1:  
                brgot = 0; cnt2 = 0
                for bb in self.agvs:
                    if aa != bb:  # not self, scanning others
                        if bb['qcan']['status'] == 2:
                            #print "stopping", aa
                            if aa['qcan']['seen'] == 2:
                                str1 = "AGV_%d stopped." % aa['num']
                                if self.speedevent != str1:
                                        if aa['num'] == 1:
                                            self.sumw.append(str1)
                                        else:
                                            self.sumw2.append(str1)
                                        self.speedevent = str1
                                aa['qcan']['speed'] = 0
                                brgot = True
                                self.disp_qcan_wait(aa)
                            else:
                                str2 = "AGV_%d slowed." % aa['num']
                                if aa['num'] == 1:
                                    self.disp_qcan_slow(aa)
                                aa['qcan']['speed'] = 1
                                brgot = True
                                
                    cnt2 = cnt2 + 1        
                    
                # if no collision:
                if not brgot:
                    for cc in self.agvs:
                        cnt = 0
                        if cc['qcan']['speed'] == 0 or cc['qcan']['speed'] == 1:
                            if cc['num'] == 1:
                                self.sumw.append("AGV_%d started."  % cc['num'] )
                            if cc['num'] == 2:
                                self.sumw2.append("AGV_%d started." %  cc['num'] )
                                
                            self.disp_qcan_go(aa, cc)
                            cc['qcan']['speed'] = 2
                            cnt = cnt + 1

    # --------------------------------------------------------------------
    # Imitate the TX side 
    
    def broadcaster(self, what = 0):
    
        #if agv == 0:
        # Tell everyone ... this is what the RADIO will do
        cnt = 0;
        for bb in self.agvs:
            if bb['qcan']['status'] == QCAN_STATUS_RELEASE:  
                strxx = "INTER Z%d" % bb['qcan']['currzone']
                if bb['qcan']['relcnt'] > 0:
                    self.radio.broadcast(cnt, "AGV %d: " % bb['num'],"LEAVE" + " " + strxx)
                    bb['qcan']['relcnt'] = bb['qcan']['relcnt'] - 1
                    
            if bb['qcan']['status'] == QCAN_STATUS_BULLY:  
                strxx = "INTER Z%d" % bb['qcan']['currzone']
                self.radio.broadcast(cnt, "AGV %d: " % bb['num'],"REQUEST" + " " + strxx)
                
            if bb['qcan']['status'] == 1:  
                if bb['qcan']['scancnt'] > 0:
                    strxx = "INTER Z%d" % bb['qcan']['currzone']
                    self.radio.broadcast(cnt, "AGV %d: " % bb['num'],"SCAN" + " " + strxx)
                    bb['qcan']['scancnt'] = bb['qcan']['scancnt'] - 1
                    
            cnt = cnt + 1  
            
    
    # Add if not duplicate
    def add_contester(self, agvx, contx, zone):
        found = 0
        for aa in agvx['contesters']:
            if aa == contx:
                found = 1
        if not found:
            agvx['contesters'].append((contx, zone))
                                
    # Remove contester
    def rm_contester(self, agvx, zone):
        found = 0
        cpcont = []
        for aa in agvx['contesters']:
            if aa[1] == zone:
                found = 1
            else:
                cpcont.append(aa)
       
        # write it back          
        if found:
            agvx['contesters'] = cpcont            
                                













