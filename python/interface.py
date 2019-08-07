#!/usr/bin/env python
# coding: UTF-8
#
## @package interface
#
#  Plot polar equations.
#
#  @author Flavia Roma
#  @date 06/07/2019
#
#  @see https://en.wikipedia.org/wiki/Polar_coordinate_system
#  @see http://jwilson.coe.uga.edu/emt668/emat6680.2003.fall/shiver/assignment11/polargraphs.htm
#  @see http://wwwp.fc.unesp.br/~mauri/Down/Polares.pdf
#  @see http://jwilson.coe.uga.edu/emat6680fa08/kimh/assignment11hjk/assignment11.html
#  @see https://elepa.files.wordpress.com/2013/11/fifty-famous-curves.pdf
#
try:
  from Tkinter import*
  import tkFont
  import tkFileDialog as tk_FileDialog
except:
  from tkinter import*
  import tkinter.font as tkFont
  import tkinter.filedialog as tk_FileDialog

import turtle, sys, os
from math import*
import polar
from polar import *

## Default scale.
scale_default = "80"

## Point list file name.
LFNAME = "turtle.txt"

## Sets a new scale.
def newScale(e, tk):
    scale = e.get()
	
    if (float(scale)>=0.1):
       polar.radius = float(scale)
       polar.LW = polar.LH = polar.radius * 8.5
       polar.Xc = polar.Yc = 0
       polar.joe.reset()
       turtle.setworldcoordinates(polar.Xc-polar.LW/2.0,polar.Yc-polar.LH/2.0,polar.Xc+polar.LW/2.0,polar.Yc+polar.LH/2.0)
       Label(tk, text="CURRENT SCALE: "+str(polar.radius), font="Arial 12", width=20).pack()
    else:
       polar.radius=float(scale_default)
       Label(tk, text="INVALID VALUE!\n ENTERED: "+scale+"\nDEFAULT USED ("+scale_default+")", font="Arial 12", width=20).pack()

## Treats the mouse click event.
#  Update the entry widget with the values from the scale widget.
def click(event):

    entry.delete(0, END)
    entry.insert(0,scale.get())

## Pop up window for changing scale.
def setScale():
    global scale, entry

    popup = Tk()
    popup.title("CHANGE SCALE")
    popup.geometry("220x200")
    Label(popup, text="ENTER A NEW SCALE", font="Noto 14").pack()

    scale = Scale(popup, from_=1, to=1000, orient=HORIZONTAL, bd=0, length=150, sliderlength=10, width=5, showvalue=1, resolution=0.1)
    scale.set(polar.radius)
    scale.pack()

    popup.bind('<B1-Motion>', click)

    Label(popup, text="NEW SCALE: ", font="Arial 12", width=20).pack()
    entry=Entry(popup, font="Arial 12")
    entry.pack()	
    #entry.insert(0,str(polar.radius))
    entry.insert(0,scale.get())
    Button(popup, text="CHANGE", font="Arial 12", width=20, command= lambda: newScale(entry, popup)).pack()
    Button(popup, text="EXIT", font="Arial 12", width=20, command=popup.destroy).pack()

## FileDialog window for getting file name.
def getFile():
    global LFNAME

    files = tk_FileDialog.askopenfilenames (
           filetypes=[("all files","*"),("txt","*.txt"),("TXT","*.TXT")],
           initialdir=os.getcwd())
    # python 2.6 bug: http://bugs.python.org/issue5712
    files = root.splitlist(files)
    for file in files:
        LFNAME=file
 
## Draw the c-th curve.
def drawCurve(c):
    polar.drawCurve(c,LFNAME,120)

## Toggle debugging mode.
def toggleDebug():
    polar.__toDebug__ = not polar.__toDebug__

## Create tk window to render the canvas.
def main():

    global scale_default, root

    root = Tk()

    offsetx = 0
    offsety = 0
    root.title("POLAR - TURTLE GRAPHICS")
    root.geometry('+%d+%d' % (offsetx,offsety))
    #root.geometry(str(root.winfo_screenwidth())+"x"+str(root.winfo_screenheight()))
    Label(root, text="Polar Equations", font="Noto 40").grid(row=0, columnspan=2)
    Label(root, text="FLAVIA ROMA's FLAIL DRIVER", font="Noto").grid(row=1, columnspan=2) 
    # width of the buttons
    widthButton = 20

    canvas0=Canvas(master = root)
    canvas0.grid(row=2, column=0)
    Label(canvas0, text="SELECT A CURVE", font="Noto 20").grid(row=0, columnspan=2)

    #canvas1=Canvas(master = root, width=680, height= 680)
    #canvas1.grid(row=2, column=1)
    #joe=turtle.RawTurtle(canvas1)

    # Set the size and position of the main window.
    polar.setup (startx=(offsetx+2*(12*widthButton)), starty=offsety)

    scale_default = str(polar.radius)

    print ("Scale = %.1f " % polar.radius)
    print ("Number of segments = %d " % polar.num_sides)

    bfont = tkFont.Font(family='Helvetica', size=12, weight='normal')
    ncurves = polar.ncurves()
    b = [None]*ncurves
    for i in range(0,ncurves):
        b[i] = Button(canvas0, text=curveList[i][3], font=bfont, width = widthButton, 
               command=lambda i=i:drawCurve(i)).grid(row=(i%(ncurves//2))+1, 
               column=i>=(ncurves//2), sticky=W+E+N+S, padx=15, pady=2)

    canvas2=Canvas(master = root)
    canvas2.grid(row=4, columnspan=2)
    Button(canvas2, text="POINT LIST FILE", font="Arial", width=30, command=getFile).grid(row=1, column=0, sticky=W+E+N+S, padx=2, pady=5)
    Button(canvas2, text="CHANGE SCALE", font="Arial", width=30, command=setScale).grid(row=2, column=0, sticky=W+E+N+S, padx=2, pady=5)
    Button(canvas2, text="TOGGLE DEBUGGING", font="Arial", width=30, command=toggleDebug).grid(row=3, column=0, sticky=W+E+N+S, padx=2, pady=5)
    Button(canvas2, text="EXIT", font="Arial", width=30, command=root.quit).grid(row=4, column=0, sticky=W+E+N+S, padx=2, pady=5)

    root.mainloop()
	
## Start the program.
if __name__=="__main__":
    sys.exit(main())
