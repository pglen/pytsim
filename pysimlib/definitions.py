#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
from . import config

from .util import *

# Define the AGVS and behaviours

def load_agv_image(fname):
    nnn = get_img_path(fname)        
    agvx = None
    try:
        agvx = Gtk.Image.new_from_file(nnn)
    except:
        print("Canot load image", sys.exc_info())
        print("'" + nnn + "'")
        
    # Test if we really have an image
    try:      
        ww = agvx.get_pixbuf().get_width()
    except:
        print("Canot load image", sys.exc_info())
        raise
    return agvx
        
#agvimg = load_agv_image("vehicle.png")
agvimg = load_agv_image("ufo.png")
agvimg2 = load_agv_image("vehicle2.png")
agvimg3 = load_agv_image("vehicle3.png")
agvimg4 = load_agv_image("vehicle4.png")

qcan_ass =  {
                'status': 0,  'speed': 2, 'seen' : 0, 'oldseen': 0,
                'scan': 0,  'scancnt' : 0, 'relcnt': 0, 'seenzone': 0,
                 'currzone': -1, 'contester' : None, 'contesters': []
            }

agv_ass = { 'agv' : agvimg, 'xxx' : 0, 'yyy' : 0, 'go': 1, 'num' : 1, 
                'zone': 20, 'name': 'heavy', 'vector' : [1, -2],
                'qcan': dict(qcan_ass)
            }

agv_ass2 = { 'agv' : agvimg2, 'xxx' : 0, 'yyy' : 0, 'go': 1, 'num' : 2, 
                    'zone' : 22, 'name': 'feather', 'vector' : [0, 4],
                    'qcan': dict(qcan_ass)
            }

agv_ass3 = { 'agv' : agvimg3, 'xxx' : 0, 'yyy' : 0, 'go': 1, 'num' : 3, 
                    'zone' : 23, 'name': 'feather', 'vector' : [2, 2],
                    'qcan': dict(qcan_ass)
            }

agv_ass4 = { 'agv' : agvimg4, 'xxx' : 0, 'yyy' : 0, 'go': 1, 'num' : 4, 
                    'zone' : 24, 'name': 'feather', 'vector' : [2, -2],
                    'qcan': dict(qcan_ass)
            }

# Define the Poks and behaviours

pok =  load_agv_image("hokypok.png")
pok2 = load_agv_image("hokypok2.png")
pok3 = load_agv_image("hokypok3.png")

# Note that we delayed to set the position of the coordinates. (xxx, yyy)
# The real values are filled in on intialization after the screen size settled

ass = { 'pok' : pok,  'xxx' : 0, 'yyy': 0,'color' : 'red', 'zone': 3
      }
        
ass2 = { 'pok' : pok, 'xxx' : 0, 'yyy': 0,'color' : 'red', 'zone': 3
       }

ass3 = { 'pok' : pok2,'xxx' : 0, 'yyy': 0, 'color' : 'blue', 'zone': 3
       }

ass4 =  { 'pok' : pok2, 'xxx' : 0, 'yyy': 0,'color' : 'blue', 'zone': 3
        }
      
ass5 =  { 'pok' : pok3, 'xxx' : 0, 'yyy': 0,'color' : 'green', 'zone': 3
        }
        
ass6 = { 'pok' : pok3,  'xxx' : 0, 'yyy': 0,'color' : 'green', 'zone': 3
       }
       
# ------------------------------------------------------------------------        
# cross paths        

ass7 = { 'pok' : pok, 'color' : 'red', 'zone': 3
       }

ass8 = { 'pok' : pok,  'color' : 'red', 'zone': 3
       }
   
     
ass9 = { 'pok' : pok2,  'color' : 'blue', 'zone': 3
       }

ass10 = { 'pok' : pok2,  'color' : 'blue', 'zone': 3
       }
   
     
ass11 = { 'pok' : pok3,  'color' : 'green', 'zone': 3
       }

ass12 = { 'pok' : pok3,  'color' : 'green', 'zone': 3
       }
   
       
targ = { 'targ' : pok,  'xxx' : 0, 'yyy': 0,'color' : 'red', 'zone': 3,
        'vector': [-2,  2]
      }

              
# EOF
















