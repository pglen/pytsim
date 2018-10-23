# pytsim

Python simulator for the Targ project.
It is a targeting simulator for drones and possibly other moving objects.

It is really just a skeleton for further research. The screen is updated with
a 'heartbeat' every 400 msecs. The objects are modified and present d on screen.

 For instance to present an object, define it as:
   
asset = { 'drone' : agvimg, 'xxx' : 0, 'yyy' : 0, 'go': 1, 'num' : 1, 
                'zone': 20, 'name': 'objname', 'vector' : [1, -2],
        }

 To animate an object, manipulate xxx / yyy in the heartbeat routine.
 
  Example: asset['xxx'] += asset['vector'][0]

 The simulation contains hit testing, basic vector manipulation. 
 (for instance unit vector conversion, vector averaging etc ..)
 
   The two objects on screen are for showing the basic spirit of the project.
 The wheeled object is chasing the moving red dot, adjusting its trajectory
 as circumstances demand.
 
  I am sharing this as a root of a larger project, so others can have access 
 to simple simulation tools. One never knows.
 
 
 Enjoy.
 
 
