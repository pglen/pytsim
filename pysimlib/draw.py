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
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GdkPixbuf

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from . import  config
from    .keywords import *
from    .util import *

BOUNDLINE   = 80            # Boundary line for col 80 (the F12 func)

class Draw(object):   

    def __init__(self):
        return self
       
    def draw_usage(self, gcr):
        gcr.set_source_rgba(0, 0, 0)
        rect = self.get_allocation()
        anx = rect.width  - 340; any = rect.height - 150
        self.draw_text(gcr, anx, any,  "Press 'R' for restart sim");    any += 18
        self.draw_text(gcr, anx, any,  "Press 'S' for start/stop sim"); any += 18
        self.draw_text(gcr, anx, any,  "Press '1  to start/stop AGV1"); any += 18
        self.draw_text(gcr, anx, any,  "Press '2  to start/stop AGV2"); any += 18
        self.draw_text(gcr, anx, any,  "Press '3  to start/stop AGV3"); any += 18
        self.draw_text(gcr, anx, any,  "Press '4  to start/stop AGV4"); any += 18
        self.draw_text(gcr, anx, any,  "Press 'Alt-X' to exit sim");    any += 18
                    
    def draw_status(self, gcr):
        rect = self.get_allocation()
        anyx = rect.width  / 2 - 240;
        anyy = 10
        
        gcr.set_source_rgba(0, 0, 0)
        rect = self.get_allocation()
        self.draw_text(gcr, anyx, anyy,  "AGV1 xx=%d yy=%d" % \
                (self.agvs[0]['xxx'], self.agvs[0]['yyy'])); 
        anyy += 18
        
        '''self.draw_text(gcr, anyx, anyy,  "AGV2 xx=%d yy=%d" % \
                (self.agvs[1]['xxx'], self.agvs[1]['yyy'])); 
        anyy += 18
        self.draw_text(gcr, anyx, anyy,  "AGV3 xx=%d yy=%d" % \
                (self.agvs[2]['xxx'], self.agvs[2]['yyy'])); 
        anyy += 18
        self.draw_text(gcr, anyx, anyy,  "AGV4 xx=%d yy=%d" % \
                (self.agvs[3]['xxx'], self.agvs[3]['yyy'])); 
        anyy += 18
                
        if self.collision:
            colstr = "Collision !!!"
            self.draw_text(gcr, anyx, anyy,  colstr, (255,0,0))
            #self.appwin.append(colstr)
            self.sumw.append("Collision")
            self.sumw2.append("Collision")
            print("Collision")
            self.mained.update_statusbar("Collision detected.")
        
        else:
            colstr     = "No Collision."
            self.draw_text(gcr, anyx, anyy,  colstr)
        '''
        
        #self.draw_text(gcr, 14, 64,  "Latest Event: %s" % self.pokevent)
        #self.draw_text(gcr, anyx, 64,  "Speed (V1/V2): %d/%d" % \
        #                                    (self.xdelta,  self.ydelta))
        
    def draw_roads(self, gcr):
        rw = 35
        rect = self.get_allocation()
        ww = rect.width; hh = rect.height

        # Horizontal        
        '''
        self.draw_line(gcr, 0, hh/2-rw, ww/2-rw, hh/2-rw)
        self.draw_line(gcr, 0, hh/2+rw, ww/2-rw, hh/2+rw)

        self.draw_line(gcr, ww/2+rw, hh/2-rw, ww, hh/2-rw)
        self.draw_line(gcr, ww/2+rw, hh/2+rw, ww, hh/2+rw)
        
        # Vertical
        self.draw_line(gcr, ww/2-rw, 0, ww/2-rw, hh/2-rw)
        self.draw_line(gcr, ww/2+rw, 0, ww/2+rw, hh/2-rw)

        self.draw_line(gcr, ww/2-rw, hh/2+rw, ww/2-rw, hh)
        self.draw_line(gcr, ww/2+rw, hh/2+rw, ww/2+rw, hh)
        '''
        
        # Middle
        gcr.set_dash((3, 2))
        gcr.set_source_rgba(0.5, 0.5, 0.5)
        self.draw_line(gcr, 0, hh/2, ww, hh/2)
        self.draw_line(gcr, ww/2, 0, ww/2, hh)
    
        self.draw_line(gcr, 0, hh, ww, 0)
        self.draw_line(gcr, 0, 0, ww, hh)
    
    def draw_grid(self, gcr):
        rect = self.get_allocation()
        ww = rect.width; hh = rect.height
        for aa in range(100):
            xx = (aa * ww) / 100
            yy = 5; 
            if aa % 10 == 0: yy = 10
            self.draw_line(gcr, xx, 0, xx, yy)
            self.draw_line(gcr, xx, hh-yy, xx, hh)
    
            yy = (aa * hh) / 100
            xx = 5; 
            if aa % 10 == 0: xx = 10
            self.draw_line(gcr, 0, yy, xx, yy)
            self.draw_line(gcr, ww-xx, yy, ww, yy)
    
    
    def draw_agvs(self, gcr):
        if not len(self.agvs):
            # init AGVS
            self.init_agvs()
            
        cnt = 0
        for aa in self.agvs:
            xx = aa['xxx']; yy = aa['yyy']
            ww =  aa['ww']; hh =  aa['hh']
    
            '''        
            # if both vectors are set, calc diagonal len
            if aa['vector'][0] > 0 and aa['vector'][1] > 0:
                ww = ww + ww / 2
                hh = hh + hh / 2
            elif aa['vector'][0] < 0 and aa['vector'][1] < 0:
                ww = ww - ww / 2
                hh = hh - hh / 2
            '''    
            
            Gdk.cairo_set_source_pixbuf(gcr, aa['pbuf'], \
                          xx - ww / 2, yy - hh / 2)
            gcr.paint()
                
            '''if aa['name'] == 'heavy':
                   Gdk.cairo_set_source_pixbuf(gcr, aa['pbuf'], \
                         xx - ww/2 - ww - 5, yy - hh/2)'''
            
            gcr.paint()
            
            # hair cross in the middle
            gcr.set_source_rgba(0, 0, 0)
            self.draw_line(gcr, xx, yy-4, xx, yy+4)
            self.draw_line(gcr, xx+4, yy, xx-4, yy)     
            self.draw_text(gcr, xx - 12, yy + 26, "%s%d" % ("V", cnt+1))
            gcr.set_source_rgba(0, 1, 0)
            self.draw_text(gcr, xx - 12, yy - 48, "%s%d" % 
                                ("S", self.agvs[cnt]['qcan']['speed']))
            cnt = cnt + 1
        pass
    
    def draw_poks(self, gcr):
        if not len(self.poks):
            self.init_poks()
            
        for aa in self.poks:
            #print "pok", aa
            pbuf = aa['pok'].get_pixbuf()
            ww =  pbuf.get_width()
            hh =  pbuf.get_height()
            posx = aa['xxx'] - ww/2; posy = aa['yyy'] - hh/2
            Gdk.cairo_set_source_pixbuf(gcr, pbuf, posx, posy)
            gcr.paint()
            
    def draw_targs(self, gcr):
        if not len(self.targs):
            self.init_targs()
            
        for aa in self.targs:
            #print "pok", aa
            pbuf = aa['targ'].get_pixbuf()
            ww =  pbuf.get_width()
            hh =  pbuf.get_height()
            posx = aa['xxx'] - ww/2; posy = aa['yyy'] - hh/2
            Gdk.cairo_set_source_pixbuf(gcr, pbuf, posx, posy)
            gcr.paint()
        
    # Underline with red wiggle
    def draw_wiggle(self, gcr, xx, yy, xx2, yy2):

        gcr.set_line_width(1)

        # The  wiggle took too much processing power .... just a line
        #self.draw_line(gcr, xx, yy, xx2, yy2)
       
        # Back to Wiggle
        while True:
            xx3 = xx + 4        
            if xx3 >= xx2: break   
            self.draw_line2(gcr, xx, yy, xx3, yy2+2)
            xx = xx3; xx3 = xx3 + 4
            self.draw_line2(gcr, xx, yy+2, xx3, yy2)            
            xx = xx3 
            
        gcr.stroke()
    
    def draw_line2(self, cr, xx, yy, xx2, yy2):
        #print "draw line", xx, yy
        cr.move_to(xx, yy)
        cr.line_to(xx2, yy2)
    
    def draw_line(self, cr, xx, yy, xx2, yy2):
        #print "draw line", xx, yy
        cr.move_to(xx, yy)
        cr.line_to(xx2, yy2)
        cr.stroke()
    
    # --------------------------------------------------------------------
    # Draw caret

    def draw_caret(self, gcx):

        gcx.set_line_width(1)
        gcx.set_source_rgba(0, 0, 5)

        #print "drawing caret", self.caret[0], self.caret[1], \
        #        self.caret[0] * self.cxx, self.caret[1] * self. cyy  
                        
        try:
            line = self.text[self.ypos + self.caret[1]]            
        except:
            line = ""
        
        xxx = calc_tabs2(line[self.xpos:], self.caret[0], self.tabstop)      
        xx = xxx * self.cxx               
        #xx = self.caret[0] * self.cxx       
        yy = self.caret[1] * self.cyy

        ch = 3 * self.cyy / 3; cw = 3 * self.cxx / 4

        # Order: Top, left right, buttom
        if self.focus:    
            # Flash cursor
            if self.bigcaret:
                rxx = xx + self.cxx
                ly = yy + self.cyy; uy = yy
                mmx = xx + cw; mmy = yy + ch
                dist = 80
                self.draw_line(gcx, mmx - dist, uy, mmx + dist, uy)
                self.draw_line(gcx, mmx - dist, ly, mmx + dist, ly)
                self.draw_line(gcx, xx , mmy - dist, xx, mmy + dist)        
                self.draw_line(gcx, rxx , mmy - dist, rxx, mmy + dist)        
            else:
                if self.insert:
                    self.draw_line(gcx, xx, yy, xx + cw, yy)
                    self.draw_line(gcx, xx + 1, yy, xx + 1, yy + self.cyy )
                    self.draw_line(gcx, xx + 3, yy, xx + 3, yy + self.cyy )
                    self.draw_line(gcx, xx , yy + self.cyy, xx + cw, yy + self.cyy )
                else:
                    self.draw_line(gcx, xx, yy, xx + cw, yy)
                    self.draw_line(gcx, xx + 1, yy, xx + 1, yy + self.cyy )
                    self.draw_line(gcx, xx + 2, yy, xx + 2, yy + self.cyy )
                    self.draw_line(gcx, xx + 3, yy, xx + 3, yy + self.cyy )
                    self.draw_line(gcx, xx + 4, yy, xx + 4, yy + self.cyy )
                    self.draw_line(gcx, xx , yy + self.cyy, xx + cw, yy + self.cyy )                
        else:
            #self.window.draw_line(gcx, xx, yy, xx + cw, yy)
            self.draw_line(gcx, xx + 1, yy + 2, xx + 1, yy -2 + self.cyy )
            self.draw_line(gcx, xx + 3, yy + 2, xx + 3, yy -2 + self.cyy )
            #self.draw_line(gcx, xx , yy + self.cyy, xx + cw, yy + self.cyy )

    # --------------------------------------------------------------------       
    # This is a response to the draw event request 
    
    def draw_text(self, gc, x, y, text, fg_col = None, bg_col = None):
        #print "draw_text, ",  self.xpos
        
        if self.hex:
            text2 = ""
            for aa in text:
                tmp = "%02x " % ord(aa)
                text2 += tmp                
            text2 = text2[self.xpos * 3:]
        elif self.stab:
            text2 = "";  cnt = 0;
            for aa in text:
                if aa == " ":  text2 += "_"                
                elif aa == "\t":
                    spaces = self.tabstop - (cnt % self.tabstop)
                    cnt += spaces - 1
                    for bb in range(spaces): 
                        text2 += "o"
                else:
                    text2 += aa                                    
                cnt += 1
            #text2 = text2[self.xpos:]
            #self.layout.set_text(ppp, len(ppp))            
        else:
            #text2 = text[self.xpos:].replace("\r", " ")
            text2 = text.replace("\r", " ")
            
        self.layout.set_text(text2, len(text2))
        xx, yy = self.layout.get_pixel_size()
        
        #offs = self.xpos * self.cxx 
        offs = 0     
        if bg_col:
            gc.set_source_rgba(bg_col[0], bg_col[1], bg_col[2])
            
            # The hard way ....
            #rc = self.layout.get_extents().logical_rect
            #rc = self.layout.get_extents().ink_rect
            #print "rc", rc.x, rc.y, rc.width / Pango.SCALE, \
            #            rc.height   / Pango.SCALE
            #gc.rectangle(x, y, rc.width / Pango.SCALE, \
            #            rc.height / Pango.SCALE)
            gc.rectangle(x - offs, y, xx , yy)
            #print self.xpos, x, y, xx, yy
            gc.fill()
        
        if fg_col:    
            gc.set_source_rgba(fg_col[0], fg_col[1], fg_col[2])
            
        #gc.move_to(x - offs, y)
        gc.move_to(x, y)
        PangoCairo.show_layout(gc, self.layout)
        
        if self.scol:
            gc.set_source_rgba(0, 0, 0)
            pos = BOUNDLINE - self.xpos       
            self.draw_line(gc, pos * self.cxx, \
                     0, pos * self.cxx, self.hhh)            
               
        if fg_col:
            gc.set_source_rgba(0, 0, 0)
            
        return xx, yy
	
# ----------------------------------------------------------------
    # Paint selection        
    def draw_selection(self, gc):
           
        xx = 0; yy = 0; 
        cnt = self.ypos;
    
        # Normalize (Read: [xy]ssel - startsel  [xy]esel - endsel
        xssel = min(self.xsel, self.xsel2)
        xesel = max(self.xsel, self.xsel2)
        yssel = min(self.ysel, self.ysel2)
        yesel = max(self.ysel, self.ysel2)
        
        # Override if column selection not active
        if not self.colsel:  
            if yssel != yesel:
                xssel = self.xsel
                xesel = self.xsel2
       
        draw_start = xssel
        if xssel != -1:
            if self.colsel: bgcol = self.cbgcolor
            else: bgcol = self.rbgcolor
            
            while cnt <  self.xlen:
                if cnt >= yssel and cnt <= yesel:
                    line = self.text[cnt]   #.replace("\r", " ")
                    if self.colsel:
                        frag = line[xssel:xesel]
                    else :   # Startsel - endsel                        
                        if cnt == yssel and cnt == yesel:   # sel on the same line
                            frag = line[xssel:xesel]
                        elif cnt == yssel:                  # start line
                            frag = line[xssel:]
                        elif cnt == yesel:                  # end line
                            draw_start = 0
                            frag = line[:xesel]
                        else:
                            draw_start = 0                  # intermediate line
                            frag = line[:]

                    dss = calc_tabs(line, draw_start, self.tabstop)
                    draw_start -= self.xpos
                    self.draw_text(gc, draw_start * self.cxx, yy, \
                                      frag, self.fgcolor, bgcol)
                    
                cnt = cnt + 1
                yy += self.cyy
                if yy > self.hhh:
                    break

    def draw_comments(self, cr):
        xx = 0; yy = 0; 
        cnt = self.ypos;
        while cnt <  self.xlen:
            #line = self.text[cnt]
            line =  untab_str(self.text[cnt])
           
           # Comments: # or // and "     
           # This gives us
           # PY comments, C comments and C defines
            ccc = line.find("#"); 
            if ccc < 0:
                ccc = line.find("//"); 
                
            # Quotes before?
            cccc = line.find('"')

            # If hash does not preceed quote:
            if ccc >= 0 and (cccc > ccc or cccc == -1):
                ccc2 = calc_tabs(line, ccc, self.tabstop) 
                ccc2 -= self.xpos
                line2 = line[ccc:]                 
                self.draw_text(cr, ccc2 * self.cxx, yy, 
                            line2, self.cocolor, None)
            else:   
                qqq = 0                                 
                while True:
                    quote = '"'
                    sss = qqq
                    qqq = line.find(quote, qqq);                     
                    if qqq < 0:
                        # See if single quote is found
                        qqq = line.find("'", sss); 
                        if qqq >= 0:
                            quote = '\''                    
                    if qqq >= 0:
                        qqq += 1
                        qqqq = line.find(quote, qqq)
                        if qqqq >= 0:
                            qqq -= self.xpos           
                            qqq2 = calc_tabs(line, qqq, self.tabstop)
                            line2 = line[qqq:qqqq]
                            line3 = line2[self.xpos:]
                            self.draw_text(cr, qqq2 * self.cxx,
                                         yy, line3, self.stcolor, None)
                            qqq = qqqq + 1
                        else:
                            break
                    else:
                        break
            cnt = cnt + 1
            yy += self.cyy
            if yy > self.hhh:
                break
           
    # Underline spelling errors
    def draw_spellerr(self, cr):
        cr.set_source_rgba(255, 0, 0)
        yyy = self.ypos + self.get_height() / self.cyy             
        for xaa, ybb, lcc in self.ularr:
            # Draw within visible range
            if ybb >= self.ypos and ybb < yyy:
                ybb -= self.ypos; 
                xaa -= self.xpos; lcc -= self.xpos;
                self.draw.draw_wiggle(cr, 
                     xaa * self.cxx, ybb * self.cyy + self.cyy,
                            lcc * self.cxx, ybb * self.cyy + self.cyy)
    
    # Paint main text        
    def draw_maintext(self, cr):
    
        xx = 0; yy = 0; 
        cnt = self.ypos;
        while cnt <  self.xlen:
            # Got fed up with tabs, generate an untabbed copy for drawing
            if self.hex or self.stab:
               text3 = self.text[cnt]
            else: 
               text3 = untab_str(self.text[cnt], self.tabstop)
               
            #print "'" + text3 + "'"
            text4 = text3[self.xpos:]
            dx, dy = self.draw_text(cr, xx, yy, text4)
            cnt += 1
            yy += dy
            if yy > self.hhh:
                break
     
    def disp_qcan_go(self, aa, cc):
        if aa['num'] == 1:
            self.decor_1.qcan_1.set_text("GO @ Z%d" % aa['qcan']['currzone'])
            self.decor_1.qcan_2.set_text("AGV V%d" % cc['num'])
        if aa['num'] == 2:
            self.decor_2.qcan_1.set_text("GO @ Z%d " % aa['qcan']['currzone'])
            self.decor_2.qcan_2.set_text("AGV V%d" % cc['num'])
        if aa['num'] == 3:
            self.decor_3.qcan_1.set_text("GO @ Z%d " % aa['qcan']['currzone'])
            self.decor_3.qcan_2.set_text("AGV V%d" % cc['num'])
        if aa['num'] == 4:
            self.decor_4.qcan_1.set_text("GO @ Z%d " % aa['qcan']['currzone'])
            self.decor_4.qcan_2.set_text("AGV V%d" % cc['num'])

    def disp_qcan_slow(self, aa):
        if aa['num'] == 1:
            self.decor_1.qcan_1.set_text("SLOW @ Z%d" % aa['qcan']['currzone'])
            #self.decor_1.qcan_2.set_text("FOR V%d" % (aa['contesters'][0]+1))
        if aa['num'] == 2:
            self.decor_2.qcan_1.set_text("SLOW @ Z%d " % aa['qcan']['currzone'])
            #self.decor_2.qcan_2.set_text("FOR V%d" % (aa['contesters'][0] + 1)) 
        if aa['num'] == 3:
               self.decor_3.qcan_1.set_text("SLOW @ Z%d " % aa['qcan']['currzone'])
            #self.decor_3.qcan_2.set_text("FOR V%d" % (aa['contesters'][0] + 1)) 
        if aa['num'] == 4:
            self.decor_4.qcan_1.set_text("SLOW @ Z%d " % aa['qcan']['currzone'])
            #self.decor_4.qcan_2.set_text("FOR V%d" % (aa['contesters'][0] + 1)) 

    def disp_qcan_wait(self, aa):
        if aa['num'] == 1:
            self.decor_1.qcan_1.set_text("WAIT @ Z%d" % aa['qcan']['currzone'])
            #self.decor_1.qcan_2.set_text("FOR V%d" % (aa['contesters'][0]+1))
        if aa['num'] == 2:
            self.decor_2.qcan_1.set_text("WAIT @ Z%d " % aa['qcan']['currzone'])
            #self.decor_2.qcan_2.set_text("FOR V%d" % (aa['contesters'][0] + 1)) 
        if aa['num'] == 3:
               self.decor_3.qcan_1.set_text("WAIT @ Z%d " % aa['qcan']['currzone'])
            #self.decor_3.qcan_2.set_text("FOR V%d" % (aa['contesters'][0] + 1)) 
        if aa['num'] == 4:
            self.decor_4.qcan_1.set_text("WAIT @ Z%d " % aa['qcan']['currzone'])
            #self.decor_4.qcan_2.set_text("FOR V%d" % (aa['contesters'][0] + 1)) 
    
# EOF












