#!/usr/bin/env python
# coding: UTF-8
#
## @package drawSpline
#
#  Catmull-Rom spline testing.
#
#  @date 14/06/2019
#
#  In computer graphics, centripetal Catmull–Rom spline is a variant form of Catmull-Rom spline
#  formulated by Edwin Catmull and Raphael Rom according to the work of Barry and Goldman.
#
#  It is a type of interpolating spline (a curve that goes through its control points) defined by
#  four control points @f$P_0, P_1, P_2, P_3@f$ with the curve drawn only from @f$P_1\ to\ P_2@f$.
#
#  @see https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline
#
try:
   from Tkinter import *
except:
   from tkinter import *
import sys
from CatmullRom import CatmullRomSpline, CatmullRomChain

## Tk object.
master = Tk()
## Canvas size in pixels.
size = 1024
## Minimum length for a segment.
minseg = 100**2
## Canvas.
c = Canvas(master, width=size, height=size)
c.pack()

def newLine(e):
    """Starts a new polyline."""

    x,y = c.canvasx(e.x), c.canvasy(e.y)
    c.create_line(x,y,x,y,tags="current",width=3) 

def extendLine(e):
    """Enlarges the current polyline."""

    x,y = c.canvasx(e.x), c.canvasy(e.y) 
    # get the last point entered
    lastx = c.coords("current")[-2]
    lasty = c.coords("current")[-1]
    # filter points too close
    if ((lastx-x)**2 + (lasty-y)**2) < minseg:
         return
    coords = c.coords("current") + [x,y] 
    c.coords("current",*coords)

def closeLine(e): 
    """Closes the current polyline, and draws a smooth spline, based on its points."""

    Points = c.coords("current")
    if closeLine.toDebug:
       print ("Points = %s" % Points)
    Points = [(Points[i],Points[i+1],0) for i in range(2,len(Points)-1,2)]
    if len(Points) > 4:
       cr = CatmullRomChain(Points,80)
       coords = []
       for p in cr: 
           coords += [p[0],p[1]]
       if closeLine.toDebug:
          print ("Coords = %s" % coords)
       if False:
          c.coords("current",*coords)
       else:
          c.create_line(coords,fill='red',width=2) 
    c.itemconfig("current",tags=()) 

closeLine.toDebug = False

def selectLine(e):
    """"Picks a polyline with the right mouse button."""

    global x0,y0
    x0,y0 = c.canvasx(e.x), c.canvasy(e.y) 
    c.itemconfig(CURRENT, tags="sel")

def moveLine (e):
    """Moves the selected polyline."""

    global x0,y0
    x1,y1 = c.canvasx(e.x), c.canvasy(e.y) 
    c.move("sel",x1-x0,y1-y0)
    x0,y0=x1,y1

def deselectLine(e): 
    """Deselects the polyline."""

    c.itemconfig("sel", tags=())

def main(argv=None):
    if argv is None:
       argv = sys.argv

    # Turn debuggin ON.
    if len(argv) > 1:
       closeLine.toDebug = True
    c.bind("<Button-1>", newLine) 
    c.bind("<B1-Motion>", extendLine) 
    c.bind("<ButtonRelease-1>", closeLine)
    c.bind("<Button-3>", selectLine) 
    c.bind("<B3-Motion>", moveLine) 
    c.bind("<ButtonRelease-3>", deselectLine)
    c.pack()
    mainloop()

if __name__=="__main__":
    sys.exit(main())
