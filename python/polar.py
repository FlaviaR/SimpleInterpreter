#!/usr/bin/env python
# coding: UTF-8
#
## \mainpage Python <A HREF="https://docs.python.org/3/library/turtle.html">Turtle Graphics</a> - A set of simple python programs for practicing CG concepts.
#
#  The set is made up of 12 small programs in increasing order of difficulty.
#  <br>
#  The most challenging script aims at drawing some parametric curves, defined in 
#  <A HREF="https://www.khanacademy.org/math/multivariable-calculus/integrating-multivariable-functions/double-integrals-a/v/polar-coordinates-1">polar coordinates</a>,
#  using the turtle intrinsic coordinate system.
#
#  Only the <b>forward, left</b> and <b>right</b> commands should be used (no setposition). This way, one may imagine controlling
#  an airplane or a drone, as if a remote control were being used.
#
#  In 3D, this would resemble the ubiquitous <b>yaw, pitch</b> and <b>roll</b> rotation paradigm.
#
# @section notes release.notes
# These programs run either in python 2.7 or python 3.6
# -# <A HREF="../../LEIAME">README</A>
# -# <A HREF="../../refman.pdf">refman.pdf</A>
#
# To run any program:
# - python prog_name.py or
# - python3 prog_name.py
#
# where the prog_name is the name of a file,
# with a python 2 or 3 source code, such as:
# - python <a href="../../doc/html/polar_8py.html">turtle/polar.py</a>
#
## @package polar
#
#  Plot polar equations.
#
#  @date 01/01/2019
#
#  @see https://en.wikipedia.org/wiki/Polar_coordinate_system
#  @see http://jwilson.coe.uga.edu/emt668/emat6680.2003.fall/shiver/assignment11/polargraphs.htm
#  @see http://wwwp.fc.unesp.br/~mauri/Down/Polares.pdf
#  @see http://jwilson.coe.uga.edu/emat6680fa08/kimh/assignment11hjk/assignment11.html
#  @see https://elepa.files.wordpress.com/2013/11/fifty-famous-curves.pdf
#
import sys, os
import numpy
import turtle
import bam
import getopt
from bam import *
try:
    from turtle import FlailDriver as Turtle
## Whether using the flail driver for writing a file, instead of turtle for drawing on screen.
    usingFlail = True
except ImportError as e:
    from turtle import Turtle
    usingFlail = False
from math import sin, cos, sqrt, degrees, pi, acos, atan2
from distutils.spawn import find_executable
print( "usingFlail = %r" % usingFlail )
bam.usingFlail = usingFlail

## Canvas width.
WIDTH = 800
## Canvas height.
HEIGHT = 800

## World Coordinate width.
LW = 680
## World Coordinate height.
LH = 680
## World Coordinate center.
Xc = 0
## World Coordinate center.
Yc = 0

## Toggle debugging mode.
__toDebug__ = False

# File handle for saving the current curve.
tfile = None

## Scale factor applied on curves.
radius = None

## Number of segments for approximating a curve.
num_sides = None

## Should diagonal lines be treated as a slope?
staircase = False
## Trajectory points - will only be initialized in main if usingPointList is set to true.
pointList = []

## Draw and put labels onto an axis, which is aligned with the coordinate system.
#  The origin is at the middle of the axis and there will be the same number of ticks on each side of the axis.
#
#  @param length axis length.
#  @param c axis center.
#  @param ticks number of divisions.
#
def drawAxis(length, c=0, ticks=10):
    x = -length/2.0
    dx = -x/ticks
    x += c
    digits = 1 if radius > 3 else 3
    for i in range(-ticks, ticks+1):
        d = str(round(x,digits)).rstrip('0').rstrip('.')
        joe.write(d)
        joe.dot()

        x += dx
        joe.forward(dx)

## Plot a pair of perpendicular axes.
def axes(w,h,xc=0,yc=0):
    move(xc-w/2.0, yc, False) 
    drawAxis(w,xc)
    move(xc, yc-h/2.0, False) 
    joe.left(90)
    drawAxis(h,yc)

## Number of curves.
ncurves = lambda: len(curveList)

## Return a valid curve number.
clampCurve = lambda c: min(max(c,0),ncurves()-1)

## Length of vector from point p = (x1,y1) to q = (x,y).
veclen = lambda p,q: sqrt(sum([(u-v)**2 for u,v in zip(p,q)]))

## Return vector p1-p0.
subvec = lambda p0,p1: [(i-j) for i,j in zip(p1,p0)]

## Dot product of vectors from point p0=(x0,y0) to p1=(x1,y1) and from p1=(x1,y1) to p=(x,y). 
dotprod = lambda p0,p1,p: sum([u*v for u,v in zip(subvec(p0,p1),subvec(p1,p))])

## Cross product of vectors from point p0=(x0,y0) to p1=(x1,y1) and from p1=(x1,y1) to p0=(x,y). 
def crossprod (p0,p1,p): u=subvec(p0,p1); v=subvec(p1,p); return u[0]*v[1]-v[0]*u[1]

## 3D cross product of vectors from point p0=(x0,y0,z0) to p1=(x1,y1,z1) and from p1=(x1,y1,z1) to p0=(x,y,z).
def crossprod3 (p0,p1,p): u=subvec(p0,p1); v=subvec(p1,p); return (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])

## Clamp a value to range [-1,1].
clamp = lambda a: min(max(-1,a),1)

## Get cartesian coordinates from polar coordinates.
#   
#  @param r radius.
#  @param a angle.
#  @return p = (x,y)
def polar2Cartesian (r,a): 
    if len(pointList)>0:
       p = f25(polar2Cartesian.listIndex)
       polar2Cartesian.listIndex += 1
    else:
       p = (r*cos(a),r*sin(a))
       if tfile:
          tfile.write ("%f, %f, %f\n" % (p[0],p[1],a))
    return p
polar2Cartesian.listIndex = 0

## Get the polar coordinates from cartesian coordinates.
cartesian2Polar = lambda x,y: (sqrt(x*x+y*y), atan2(-y,-x)+pi)

## Update a curve bounding box, by adding a new point to it.
#  - [xmin, xmax, ymin, ymax, zmin, zmax]
#
#  @param p a point.
#  @param BBOX bounding box (list of point coordinates).
#  @return a new bounding box, or the given bounding box, with p in it.
#
def updateBBOX(p,BBOX=None): 
    if BBOX is None:
       box = []
       for i in  p:
           box += [i,i] 
       return box

    i = 0
    for c in p:
        BBOX[i]   = min(BBOX[i],c)
        BBOX[i+1] = max(BBOX[i+1],c)
        i += 2
    return BBOX

## Set the color of the curve. 
setColor = lambda v: joe.color("red" if v < 0 else "blue")

## Archimedean spiral.
#  The spiral becomes tighter for smaller values of "b" and wider for larger values.
#  - @f$r(\theta) = a + b \theta.@f$
#
#  The Archimedean spiral has two arms, one for @f$\theta > 0@f$ and one for @f$\theta < 0.@f$
#  - The two arms are smoothly connected at the origin. 
#
#  The negative arm is shown in red on the accompanying graph. 
#  - Taking the mirror image of this arm across the y-axis will yield the other arm.
#
#  @param c scale factor to be applied.
#  @param t parametric value.
#  @param a origin of the spiral: (a,0).
#  @param b controls the distance between successive turnings.
#  @return a tuple @f$(r, \theta)@f$ representing a point in polar coordinates.
#
#  @see https://en.wikipedia.org/wiki/Archimedean_spiral
#
def f0 (c, t, a = 0, b=1/(2*pi)): 
    setColor(t)
    return (c * (a + b * t), t)

## A rose of \e n or \e 2n petals.
#  - @f$r(\theta) = a\ 2\ sin(n \theta).@f$
#
#  If \e n is an integer, the curve will be rose-shaped with
#  - \e 2n petals if \e n is even, and
#  - \e n petals if \e n is odd.
#
#  @param a scale to be applied on the curve.
#  @param t parametric value @f$\theta.@f$
#  @return a tuple @f$(r, \theta)@f$ representing a point in polar coordinates.
#  @see https://en.wikipedia.org/wiki/Rose_(mathematics)
#
f1 = lambda a, t, n=4: (a * 2*sin(n*t), t)

## A rose of five petals.
f2 = lambda a, t: f1(a,t,5)

## A rose of three petals.
f3 = lambda a, t: f1(a,t,3)

## A rose of four petals.
f4 = lambda a, t: f1(a,t,2)

## Double Loop.
#  - @f$r(\theta) = a\ cos(\frac{\theta}{2}).@f$
#
#  @see http://jwilson.coe.uga.edu/emt668/emat6680.2003.fall/shiver/assignment11/polargraphs.htm
#
f5 = lambda a, t: (a * cos(t/2.0), t)

## Lemniscate of Bernoulli.
#  - @f$r^2(\theta) = 2 a^2\ cos\ (2 \theta).@f$
#  - @f$r(\theta) = \pm a\ \sqrt {2\ cos\ (2 \theta)}.@f$
#
#  The length is 2a. Valid angle ranges into  \[\], and invalid into \(\).
#  - \[-pi/4 , pi/4\] \(pi/4 , 3pi/4\) \[3pi/4 , 5pi/4\] \(5pi/4 - 7pi/4\)
#
#  Negative angles in red.
#
#  @param a scale to be applied on the curve.
#  @param t parametric value.
#  @return 0 for invalid angles or @f$(r, \theta)@f$ otherwise.
#  @see https://en.wikipedia.org/wiki/Lemniscate_of_Bernoulli
#
def f6(a,t):
    if (t > -pi/4 and t < pi/4) or (t > 3*pi/4 and t < 5*pi/4):
        setColor(t)
        return (a * sqrt(cos(2*t)), t)
    elif (t > pi/4 and t < 3*pi/4) or (t > 5*pi/4 and t < 7*pi/4):
        return (0,t)
    else:
        return (0,t)

## Circle.
#  Centered at (0,a) and diameter 2a.
#  - @f$r(\theta) = 2a\ sin(\theta).@f$
#
#  @param a radius.
#  @param t parametric value.
#  @return a tuple @f$(r, \theta)@f$ representing a point in polar coordinates.
#
f7 = lambda a, t: (a * 2 * sin(t), t)

## Bowtie.
#  - @f$r(\theta) = 2\ sin(2 \theta) + 1.@f$
#
#  @see http://jwilson.coe.uga.edu/emat6680fa08/kimh/assignment11hjk/assignment11.html
#
f8 = lambda a, t: (a * (2*sin(2*t)+1), t)

## Oscar's butterfly.
#  - @f$r(\theta) = cos^{2}(5 \theta) + sin(3 \theta) + 0.3.@f$
#
#  @see http://jwilson.coe.uga.edu/emt668/emat6680.2003.fall/shiver/assignment11/polargraphs.htm
#
f9 = lambda a, t: (a * (cos(5*t)**2 + sin(3*t) + 0.3), t)

## Crassula Dubia.
#  - @f$r(\theta) = sin(\theta) + sin^{3}(5 \frac{\theta}{2}).@f$
#
#  @see http://jwilson.coe.uga.edu/emt668/emat6680.2003.fall/shiver/assignment11/polargraphs.htm
#
f10 = lambda a, t: (a * (sin(t) + sin(5*t/2)**3), t)

## Majestic butterfly.
#  - @f$r(\theta) = 9 - 3\ sin (\theta) + 2 \sin \left(3\theta\right) - 3 \sin(7\theta) + 5\ cos(2\theta).@f$
#
#  @see https://www.desmos.com/calculator/pgyxrshobg
#
f11 = lambda a, t: (a/6 * (9 - 3*sin(t) + 2*sin(3*t) - 3*sin(7*t) + 5*cos(2*t)), t)

## Limaçon of Pascal.
#  - @f$r(\theta) = a + b\ sin(\theta).@f$
#
#  - When a < b: limacon with and inner loop.
#  - When a > b: dimpled limacon.
#  - When a >= 2b: convex limacon.
#  - When a = b: cardioid.
#
#  Changing from sine to cosine does not affect the shape of the graph, just its orientation.
#  - Equations using sine will be symmetric to the vertical axis,
#  - while equations using cosine are symmetric to the horizontal axis.
#  - The sign of b will also affect their orientation.
#
#  @see https://en.wikipedia.org/wiki/Limaçon
#
def f12 (c, t, a=2, b=3):
    return (c/2 * (a + b*sin(t)), t)

## Hyperbolic Spiral.
#  - @f$r(\theta) = \frac{a}{\theta}.@f$ 
#
#  It begins at an infinite distance from the pole in the center 
#  (for @f$\theta@f$ starting from zero, @f$r = a/\theta@f$ starts from infinity), 
#  - and it winds faster and faster around as it approaches the pole;
#  - the distance from any point to the pole, following the curve, is infinite.
#
#  The spiral has an asymptote at y = a: 
#  - for t approaching zero the ordinate approaches a, while the abscissa grows to infinity.
#
#  @param a scale to be applied on the curve.
#  @param t parametric value.
#  @return a tuple @f$(r, \theta)@f$ representing a point in polar coordinates.
#  @see https://en.wikipedia.org/wiki/Hyperbolic_spiral
#
f13 = lambda a, t: ((100*a if t <= 0.01 else a/t), t)

## Cochleoid.
#  - @f$r(\theta) = a\ \frac{sin(\theta)}{\theta}.@f$
#  - @f$r(0) = a.@f$
#
#  Negative angles in red.
#
#  @param a scale to be applied on the curve.
#  @param t parametric value.
#  @return a tuple @f$(r, \theta)@f$ representing a point in polar coordinates.
#  @see https://en.wikipedia.org/wiki/Cochleoid
#
def f14(a, t): 
    setColor(t)
    return ((3*a if t == 0 else 3 * a * sin(t)/t), t)

## Fermat's Spiral.
#  - @f$ r^2(\theta) = a^2\ \theta.@f$
#  - @f$ r(\theta) = \pm a \sqrt\theta.@f$
#
#  Negative angles (red) return @f$ r = -a \sqrt\theta.@f$
#
#  @param a scale to be applied on the curve.
#  @param t parametric value.
#  @return a tuple @f$(r, \theta)@f$ representing a point in polar coordinates.
#  @see https://en.wikipedia.org/wiki/Fermat%27s_spiral
#
def f15(a, t):
    sign = -1 if t <= 0 else 1
    setColor(sign)
    return (sign*sqrt(a*a/4 * abs(t)), abs(t))

## A Face.
#  - @f$r(\theta) = sin(2^{\theta}) - 1.7.@f$
#
#  @see https://www.intmath.com/plane-analytic-geometry/8-curves-polar-coordinates.php
#
f16 = lambda a, t: (a * (sin (2**t) - 1.7), t)

## Heart.
#  - @f$r(\theta) = 2 - 2\ sin(\theta) + sin(\theta) \frac{\sqrt{ \left| cos(\theta) \right| }} {sin(\theta) + 1.4}.@f$
#
#  @see http://mathworld.wolfram.com/HeartCurve.html
#
f17 = lambda a, t: (a*0.8 * (2 - 2 * sin(t) + sin(t) * (sqrt(abs(cos(t)) / (sin(t) + 1.4)))), t)

## Ameba.
#  - @f$r(\theta) = 1 - cos(\theta)\ sin(3 \theta).@f$
#
#  @see https://brilliant.org/wiki/polar-curves/
#
f18 = lambda a, t: (a * (1 - cos(t) * sin(3*t)), t)

## Parabola.
#  - @f$r(\theta) = \frac{l} {1 +\ e\ cos(\theta)}.@f$
#
#  @param a scale factor to be applied.
#  @param t parametric value.
#  @param e is the eccentricity of the conic section, 
#  @param l is the length of the semi-latus rectum (the distance along the y-axis from the pole to the curve).
#
#  Using the equation above, the conic section will always have a focus at the pole.
#
#  The directrix will be the line @f$ x = \frac{1}{e}@f$
#    - @f$r = \frac{1}{e} sec(\theta)@f$ in polar form. 
#
#  Different values of \e e will give different kinds of conic sections:
#   - If  e == 0, then the curve is a circle.
#   - If  0 < e < 1, then the curve is an ellipse.
#   - If  e == 1, then the curve is a parabola.
#   - If  e > 1, then the curve is a hyperbola.
#
#  @see https://brilliant.org/wiki/polar-curves/
#
def f19 (a, t, e=1, l=1):
    setColor(t)
    return (a * (l / (1 + e*cos(t))), t)

## Hyperbola.
#  - @f$r(\theta) = \frac{1} {1 + 1.5\ cos(\theta)}.@f$
#  - If @f$cos(\theta) = -\frac{1}{1.5} \Rightarrow \theta = acos(-\frac{1}{1.5}) = 
#                         \pm 2.30052 \text{ rad} = \pm 131.81^\circ \Rightarrow @f$ 
#    - @f$lim_{\theta \rightarrow -2.3^-} r(\theta) = \infty@f$ 
#    - @f$lim_{\theta \rightarrow -2.3^+} r(\theta) = - \infty@f$ 
#    - @f$lim_{\theta \rightarrow 2.3^-} r(\theta) = \infty@f$ 
#    - @f$lim_{\theta \rightarrow 2.3^+} r(\theta) = - \infty@f$ 
#  - Throw an exception (raise ValueError) when @f$(2.05 \leq \theta  \leq 2.481) \text{ or } (-2.481 \leq \theta \leq -2.05).@f$
#
#  @see https://brilliant.org/wiki/polar-curves/
#
def f20 (a, t):
    if (t >= 2.05 and t <= 2.481) or (t >= -2.481 and t <= -2.05): 
        raise ValueError
    else: 
        return f19(a, t, 1.5, 1)

## Ellipse.
#  - @f$r(\theta) = \frac{1} {1 + 0.5\ cos(\theta)}.@f$
#
#  @see https://brilliant.org/wiki/polar-curves/
#
def f21 (a, t):
    return f19(a, t, 0.5, 1)

## Freeth’s Nephroid.
#  - @f$r(\theta) = a(1 + 2\ sin(\theta/2))@f$
#
#  @see https://elepa.files.wordpress.com/2013/11/fifty-famous-curves.pdf 
#
f22 = lambda a, t: (a * (1 + 2 * sin(t/2)), t)

## Star.
#  - @f$r(\theta) = sin^{2}(1.2\theta) + cos^{3}(6\theta)@f$
#
#  @see https://www.originlab.com/index.aspx?go=products/origin/graphing
#
def f23 (a,t):
    setColor(t)
    return (a * (sin(1.2*t)**2 + cos(6*t)**3), t)

## Cannabis.
#  - @f$r(\theta) = (1+0.9\ cos(8\theta))\ (1+0.1\ cos(24\theta))\ (0.9+0.1\ cos(200\theta))\ (1+sin(\theta))@f$
#
#  @see https://www.wolframalpha.com/input/?i=(1%2B0.9+cos(8+&theta;))+(1%2B0.1+cos(24+&theta;))+(0.9%2B0.1+cos(200+&theta;))+(1%2Bsin(&theta;))+polar+-pi+to+pi
#
def f24 (a,t):
    setColor(t)
    return (a * ((1+0.9*cos(8*t))*(1+0.1*cos(24*t))*(0.9+0.1*cos(200*t))*(1+sin(t))), t)

## Draw a curve defined by a set of points.
#
#  @param i a point index.
#  @param j a dummy parameter.
#  @return ith point on the list, or anything else if j is passed.
#
def f25 (i,j=None):
    if j is None: return pointList[i]
    return 0,0

## Initialize the PointList.
#
#  @param fname file name with points.
#  @return pointList bounding box.
#
def initPointList(fname):
    global curveList
    fbox = None
    try:
        f = open(fname,'r')
    except IOError as e:
        print ("Could not open file %s" % fname)
        raise e
    for row in f:
        line = row.split(",")
        if len(line) == 2 or len(line) == 3:
           try:
              p = list(map(float,line))
           except:
              print("Invalid line %s in file: %s" % (row,fname))
              continue
           pointList.append(p)
           fbox = updateBBOX(p, fbox)
        else:
           print("Invalid line %s in file: %s" % (row,fname))
    f.close()
    # Update curveList to include the calculated number of segments
    curveList[25] = (f25,2*pi,0,"Point List Based",len(pointList)-1)
    return fbox

## Print curve identifications.
def help(j=None):

    if j is None:
        print("-1: Display help.")
        print("-2: Toggle debugging mode.")
        for i,s in enumerate(curveList):
            print("%d: %s." % (i,s[3]))
        print("q: Exit.")
    else:
        return curveList[j][3]

## List of tuples with: polar equation function, angle range, initial angle, title and number of segments.
curveList = [(f0,12*pi,-6*pi,"Archimedean spiral"), 
             (f1,2*pi,0,"A rose of eight petals"),
             (f2,pi,0,"A rose of five petals"), 
             (f3,pi,0,"A rose of three petals"),
             (f4,2*pi,0,"A rose of four petals"),
             (f5,4*pi,0,"Double Loop"), 
             (f6,6*pi/4,-pi/4,"Lemniscate of Bernoulli"), 
             (f7,pi,0,"Circle"), 
             (f8,2*pi,0,"Bowtie"), 
             (f9,2*pi,0,"Oscar's butterfly"), 
             (f10,4*pi,0,"Crassula Dubia"), 
             (f11,2*pi,0,"Majestic butterfly"), 
             (f12,2*pi,0,"Limaçon"), 
             (f13,8*pi,0.25,"Hyperbolic Spiral",120), 
             (f14,12*pi,-6*pi,"Cochleoid"), 
             (f15,12*pi,-6*pi,"Fermat's Spiral"), 
             (f16,2*pi,0,"A Face"),
             (f17,2*pi,0,"A Heart"),
             (f18,2*pi,0,"Ameba"),
             (f19,8*pi/5,-4*pi/5,"Parabola"), 
             (f20,2*pi,-pi,"Hyperbola"),
             (f21,2*pi,-pi,"Ellipse"),
             (f22,4*pi,0,"Freeth’s Nephroid"),
             (f23,10*pi,-5*pi,"Star"),
             (f24,2*pi,-pi,"Cannabis",600),
             (f25,2*pi,0,"Point List Based")]

## Move the turtle to a given point. 
#  - > direction of movement
#  - ] turtle head.
#
#  @param x coordinate.
#  @param y coordinate.
#  @param mode whether to use setposition, or use
#  only forward, left and right.
#
def move(x,y,mode=True):
    joe.penup()
    joe.home()
    if mode:
       joe.setposition(x,y)
    else:
       joe.forward(x)
       if y > 0:
          # ----->] F
          #      ^ R 
          #      | L
          # ----->]
          #   F 
          joe.left(90)
          joe.forward(y)
          joe.right(90)
       elif y < 0:
          # F (actually backward, keep looking forward)
          # <]-----
          # | R
          # | L
          # ----->] F
          #
          joe.right(90)
          joe.forward(abs(y))
          joe.left(90)
    joe.pendown()

## Draw a box.
def drawBox(b):
    joe.color("violet")
    move(b[0], b[2], False)
    joe.forward(b[1]-b[0])
    joe.left(90)
    joe.forward(b[3]-b[2])
    joe.left(90)
    joe.forward(b[1]-b[0])
    joe.left(90)
    joe.forward(b[3]-b[2])
    

## Draw some polar equations.
#
#  We should keep three points: (x0,y0), (x1,y1), (x2,y2).
#  - @f$(x0,y0) \rightarrow (x1,y1)@f$ is the previous segment.
#  - @f$(x1,y1) \rightarrow (x2,y2)@f$ is the current segment.
#
#  \image html zVSPv.png
#
#  First, we calculate the angle @f$\gamma@f$ between these two segments, by using the dot product: 
#  - @f$c = cos(\gamma) = \frac{(x_1-x_0,y_1-y_0)}{\sqrt {{(x_1-x_0)}^2+{(y_1-y_0)}^2}} \cdot \frac{(x_2-x_1, y_2-y_1)}{\sqrt {{(x_2-x_1)}^2+{(y_2-y_1)}^2}} = 
#                         \frac{(x1-x0) * (x2-x1) + (y1-y0) * (y2-y1)} {\sqrt {({(x_1-x_0)}^2+{(y_1-y_0)}^2)\ ({(x_2-x_1)}^2+{(y_2-y_1)}^2)}}@f$
#  - @f$\gamma = acos(min(max(c,-1),1)),@f$
#
#  so the turtle makes a left or right turn, based on the sign of the cross product of the two segments: 
#
# @f$ Or_2 (P_0, P_1, P_2) = \text{sign} \begin{vmatrix} 1 & 1 & 1 \\ x_0 & x_1 & x_2 \\ y_0 & y_1 & y_2 \end{vmatrix} = @f$
# @f$x_1 y_2 + x_2 y_0 + x_0 y_1 - x_1 y_0 - x_2 y_1 - x_0 y_2 = @f$
#
#  - @f$x_1 (y_2 - y_0 - y_1 + y_1) - x_2 (y_1 - y_0) - x_0 (y_2 - y_1) = @f$
#  - @f$x_1 (y_2 - y_1) + x_1 (y_1 - y_0)  - x_2 (y_1 - y_0) - x_0 (y_2 - y_1) = @f$
#  - @f$(x_1 - x_0) (y_2 - y_1) - (y_1 -y_0) (x_2 - x_1) \Rightarrow@f$
#
#    - @f$(x_1-x_0,y_1-y_0) \times (x_2-x_1, y_2-y_1) = (x1-x0)*(y2-y1) - (y1-y0)*(x2-x1)@f$
#      - @f$< 0 \rightarrow@f$ right turn
#      - @f$> 0 \rightarrow@f$ left turn
#
#  Then, the turtle moves forward by a distance equal to the length of the current segment: @f$\sqrt {{(x_2-x_1)}^2+{(y_2-y_1)}^2}@f$
#
#  For the first point, we need the angle @f$\alpha \in [0,2\pi]@f$ between the \e x-axis and the vector @f$(x_1-x_0,y_1-y_0):@f$
#  - @f$\alpha = atan2(y0-y1,x0-x1)+\pi@f$
#    - @f$atan2(y,x) \rightarrow \alpha \in [-\pi,\pi]@f$
#    - @f$atan2(-y,-x) + \pi \rightarrow \alpha \in [0,2\pi]@f$
#  
#  @param func equation.
#  @param turns polar angle range (extension).
#  @param initialAng initial polar angle.
#  @param title curve name.
#  @param nseg number of segments.
#
#  @see https://en.wikipedia.org/wiki/Inverse_trigonometric_functions
#  @see https://docs.python.org/3/library/math.html
#  @see https://www.mathsisfun.com/algebra/vectors-dot-product.html
#
def polarRose(func, turns, initialAng = 0.0, title=None, nseg=None):
    global usingFlail, __toDebug__

    if nseg is None:
        nseg = num_sides
    joe.reset()
    if not usingFlail: 
       axes(LW,LH,Xc,Yc)
    joe.pensize(3)
    joe.color("blue")
    joe.setheading(0)

    ang = initialAng
    p0 = polar2Cartesian(*func(radius,ang))
    box = updateBBOX(p0,None)
    move(p0[0],p0[1],False)

    angle = turns / nseg
    ang += angle
    p1 = polar2Cartesian(*func(radius,ang))
    updateBBOX(p1,box)
    len0 = veclen(p1,p0)
    # to return an angle in [0,2pi] -> atan2(-y,-x) + pi
    p10 = subvec(p1,p0)
    dir = toUBAM(degrees(atan2(p10[1],p10[0])+pi))
    if __toDebug__: print("left turn\n")
    joe.left(dir)
    ascension(p0,p1)
    lmin = len0
    lmax = len0
    for i in range(1,nseg):
        ang += angle
        try:
           p = polar2Cartesian(*func(radius,ang))
        except ValueError:
           print("Going to infinity.")
           joe.penup()
           continue
        updateBBOX(p,box)
        len1 = veclen(p,p1)
        len0 = veclen(p1,p0)

        if len0 > 0 and len1 > 0:
            # get the angle between the previous and the current direction.
            cang = clamp(dotprod (p0,p1,p) / len0 / len1)
            # y = acos(x): −1 ≤ x ≤ 1  ->  0 ≤ y ≤ π   or   0° ≤ y ≤ 180°
            cang = toUBAM(degrees(acos(cang)))
            # check whether it is a right or left turn.
            if crossprod(p0,p1,p) < 0:
               if __toDebug__: print("right turn\n")
               joe.right(cang)
            else: 
               if __toDebug__: print("left turn\n")
               joe.left(cang)
            ascension(p1,p)
            lmin = min(len1,lmin)
            lmax = max(len1,lmax)
            joe.pendown()

            p0 = p1
       	    p1 = p
        else:
            print("Null vector")
    if not usingFlail:
       drawBox(box)
    print("%s Bounding Box: %s" % (title,box))
    r1, t1 = cartesian2Polar(box[0], box[2])
    r2, t2 = cartesian2Polar(box[1], box[3])
    t1 = degrees(t1)
    t2 = degrees(t2)
    uf = usingFlail
    db = __toDebug__
    usingFlail = True
    __toDebug__ = False
    print("LLC length: %f = %d, %f = %u" % (r1,toInt(r1),t1,float2UBAM(t1)))
    print("UPC length: %f = %d, %f = %u" % (r2,toInt(r2),t2,float2UBAM(t2)))
    print("Minimum length: %f = %d" % (lmin,toInt(lmin)))
    print("Maximum length: %f = %d" % (lmax,toInt(lmax)))
    usingFlail = uf
    __toDebug__ = db


## Control the turtle's ascension.
#  If pointList is set, then a file is being used to describe the trajectory.
#  In this case, decide whether to use the forward-up method or the staircase method.
#  Forward-up method: move forward until the turtle reaches the second point, then ascend to meet it.
#  Staircase method: move forward-upwards incrementally until the second point is reached.
#
#  @param p0 initial point.
#  @param p1 end point.
#
def ascension(p0, p1):
    # length onto plane XY
    flen = veclen(p0[:2],p1[:2])
    forw_disp = toInt(flen)
    z_disp = 0 
    if len(pointList) > 0 and len(p0)>2:
       z0,z1 = p0[2],p1[2]
       z_disp = z1 - z0
       z_disp = toInt(z_disp)
    if __toDebug__:
        print("Forw disp: %f Z Disp: %f" % (forw_disp, z_disp))

    if (z_disp == 0 or not usingFlail):
        joe.forward(forw_disp)
    elif (not staircase):
        if (z_disp > 0):
            joe.forward(forw_disp)
            joe.ascend(z_disp)
        elif (z_disp < 0):
            joe.descend(toInt(abs(z1 - z0)))
            joe.forward(forw_disp)
    else:
        if (abs(z_disp) > 0):
            inst = []
            n = 5
            z_dispIter = toInt(abs(z1 - z0)/n)
            forw_dispIter = toInt(abs(flen)/n)
            if __toDebug__:
               print("Forw: %f For_conv: %f" % (flen, forw_disp))
               print("Z disp: %f Z_disp_conv: %f" % (z1 - z0, z_disp))
               print("Z iterations: %f" %z_dispIter)

            # if z_dispIter is 0, don't bother doing a repeat and splitting up forward inst
            if (z_dispIter > 0):
                if (z_disp > 0):
                    inst.append((joe.ascend, z_dispIter))
                elif (z_disp < 0):
                    inst.append((joe.descend, z_dispIter))
                inst.append((joe.forward, forw_dispIter))
                joe.repeat(n, inst)
            else:
                joe.forward(forw_disp)

## Draw the c-th curve.
def drawCurve(c,toRead,NS):
    global tfile, LW , LH, Xc, Yc, pointList, num_sides

    if usingFlail:
       joe.reset()
    # start over with an empty point list
    pointList = []
    polar2Cartesian.listIndex = 0        
    cname = curveList[c][3]
    if cname == "Point List Based":
        try:
           fbox = initPointList(toRead)
        except:
           return
        if fbox is None:
           print("Empty file %s" % toRead)
           return
        LW = fbox[1]-fbox[0]
        LH = fbox[3]-fbox[2]
        if LW == 0: LW=1
        if LH == 0: LH=1
        LW = LH = max(LW,LH)
        Xc = (fbox[1]+fbox[0])/2.0
        Yc = (fbox[3]+fbox[2])/2.0
    else:
        LW = LH = radius * 8.5
        Xc = Yc = 0
    turtle.setworldcoordinates(Xc-LW/2.0,Yc-LH/2.0,Xc+LW/2.0,Yc+LH/2.0) 
    turtle.title("%d: %s" % (c, help(c)))
    nturns = int(curveList[c][1]/(2*pi))
    num_sides = NS
    if nturns > 0:
       num_sides *= nturns
    print ("Number of segments = %d " % (num_sides if len(curveList[c]) < 5 else curveList[c][4]))
    # write the curve on a file
    if len(pointList) == 0:
       tfile = open("turtle.txt", 'w')
    polarRose(*curveList[c])
    if tfile:
       tfile.close()
    if not usingFlail: # flailDriver is not being used
       cname = 'images/' + cname
       cname += '.ps'
       with open(cname, 'wb') as ps:
          ps.write(turtle.Screen().getcanvas().postscript().encode('utf-8'))
       cname = cname.replace (' ','\ ')
       cname = cname.replace ("\'","\\'")
       cnameo = cname.replace (".ps",".png")
       # convert to pdf
       if find_executable("ps2pdf") is not None:
          os.system("ps2pdf %s" % cname)
          cnamePDF = cname[7:].replace(".ps", ".pdf")
          os.rename(cnamePDF, "images/"+cnamePDF)
       # convert to png
       if find_executable("gs") is not None:
          os.system("gs -dNOPAUSE -dBATCH -sDEVICE=png16m -sOutputFile=%s %s" % (cnameo,cname))

## Initialize some polar global variables. 
def setup(startx=0, starty=0):
    global num_sides, radius, joe

    # Since the overflow is expected, the warning can be shut with:
    numpy.warnings.simplefilter("ignore", RuntimeWarning)

    turtle.title("Polar Rose")

    # Screen object.
    #screen = turtle.Screen()
    #print(screen.screensize())
    # set canvas dimensions.
    #screen.screensize(canvwidth=WIDTH, canvheight=HEIGHT, bg=None)
    #print(screen.screensize())

    # Set the size and position of the main window.
    turtle.setup (WIDTH, HEIGHT, startx, starty)

    print ("Window width = %d " % turtle.window_width())
    print ("Window height = %d " % turtle.window_height())

    # set background color.
    turtle.bgcolor(1.0, 250/255.0, 205/255.0)

    # Speed: 1 - 10
    turtle.speed("fast")

    ## Turtle graphics object.
    joe = Turtle(shape="turtle", visible=False)

    ## number of segments to draw a curve.
    if num_sides is None:
       num_sides = 120
    ## scale factor to be applied on all curves.
    if radius is None:
       radius = LW / 8.5

## Main program.
#
#  @param argv list of arguments.
#  - polar.py -s 80 -n 120 -f plistfiles/TriangleMeasured1Cleaned.txt
#  - n number of segments to draw a curve.
#  - s scale factor to be applied on all curves.
#  - f point list file. <br> <br>
#
#  <br>
#  \htmlonly <style>div.image img[src="Majestic.png"]{width:300px;}</style> \endhtmlonly 
#  \htmlonly <style>div.image img[src="Crassula.png"]{width:300px;}</style> \endhtmlonly
#  \htmlonly <style>div.image img[src="Fermat.png"]{width:300px;}</style> \endhtmlonly
#  \htmlonly <style>div.image img[src="parabola.png"]{width:300px;}</style> \endhtmlonly
#  \htmlonly <style>div.image img[src="hyperbola.png"]{width:300px;}</style> \endhtmlonly
#  \htmlonly <style>div.image img[src="star.png"]{width:300px;}</style> \endhtmlonly
#  \htmlonly <style>div.image img[src="cannabis.png"]{width:300px;}</style> \endhtmlonly
#  \htmlonly <style>div.image img[src="Oscar.png"]{width:300px;}</style> \endhtmlonly
#  @image html Majestic.png "Majestic"
#  @image html Crassula.png "Crassula Dubia"
#  @image html Fermat.png "Fermat's Spiral"
#  @image html parabola.png "Parabola"
#  @image html hyperbola.png "Hyperbola"
#  @image html star.png "Star"
#  @image html cannabis.png "Cannabis"
#  @image html Oscar.png "Oscar's Butterfly"
#  \htmlonly
#  <p style="float: left; font-size: 12pt; text-align: center; width: 20%; margin-right: 1%; margin-bottom: 0.5em;"><img src="Majestic.png" style="width: 100%">Majestic</p>
#  <p style="float: left; font-size: 12pt; text-align: center; width: 20%; margin-right: 1%; margin-bottom: 0.5em;"><img src="Crassula.png" style="width: 100%">Crassula Dubia</p>
#  <p style="float: left; font-size: 12pt; text-align: center; width: 20%; margin-right: 1%; margin-bottom: 0.5em;"><img src="Fermat.png" style="width: 100%">Fermat's Spiral</p>
#  <p style="float: left; font-size: 12pt; text-align: center; width: 20%; margin-right: 1%; margin-bottom: 0.5em;"><img src="parabola.png" style="width: 100%">Parabola</p>
#  <p style="float: left; font-size: 12pt; text-align: center; width: 20%; margin-right: 1%; margin-bottom: 0.5em;"><img src="hyperbola.png" style="width: 100%">Hyperbola</p>
#  <p style="float: left; font-size: 12pt; text-align: center; width: 20%; margin-right: 1%; margin-bottom: 0.5em;"><img src="star.png" style="width: 100%">Star</p>
#  <p style="float: left; font-size: 12pt; text-align: center; width: 20%; margin-right: 1%; margin-bottom: 0.5em;"><img src="cannabis.png" style="width: 100%">Cannabis</p>
#  <p style="float: left; font-size: 12pt; text-align: center; width: 20%; margin-right: 1%; margin-bottom: 0.5em;"><img src="Oscar.png" style="width: 100%">Oscar's Butterfly</p>
#  \endhtmlonly
#
def main(argv = None):
    global num_sides, radius, __toDebug__

    if argv is None:
       argv = sys.argv

    toRead = "turtle.txt"

    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hs:n:f:d", ["help", "scale", "npoints", "file", "debug"])
        except getopt.GetoptError as msg:
           print ("Invalid Arguments")
           raise msg
        # opts is an option list of pairs [(option1, argument1), (option2, argument2)]
        # args is the list of program arguments left after the option list was stripped
        # for instance, "polar.py -h --help -s 90 1 2", sets opts and args to:
        # [('-h', ''), ('--help', ''), ('-s', 90)] ['1', '2']
        for o,a in opts:  # something such as [('-h', '')] or [('--help', '')]
            if o in ( "-h", "--help" ):
               print ("Usage: -h or --help -s or --scale float_value, -n or --npoints int_value, -f or --file str_value, -d or --debug.")
               help()
               return 1
            elif o in ( "-n", "--npoints" ):
               num_sides = int(a)
            elif o in ( "-s", "--scale" ):
               radius = float(a)
            elif o in ( "-f", "--file" ):
               toRead = a
               print ("PointList file: %s" % a)
            elif o in ( "-d", "--debug" ):
               __toDebug__ = True
               bam.__toDebug__ = True
               print("Debugging is ON.")
            else:
               assert False, "unhandled option"
        if len(args) < 2:                                                   
            print ("Usage: -h or --help -s or --scale float_value, -n or --npoints int_value, -f or --file str_value, -d or --debug.")
    # will be caught by the outer "try"                  
    except Exception as err:
        print (str(err) + "\nFor help, type: %s --help" % argv[0])
        return 2

    setup()

    NS = num_sides
    print ("Scale = %.1f " % radius)
    print ("Number of segments = %d " % num_sides)
    while True:
        try:
            c = int(input("Curve Number: "))
            print(help(c))
        except (ValueError,SyntaxError,KeyboardInterrupt):
            sys.exit()

        if c < 0:
           help()
           if c == -2:
              __toDebug__ = not __toDebug__
              bam.__toDebug__ = __toDebug__
        else:
           drawCurve(clampCurve(c),toRead,NS)

    turtle.done()


if __name__=="__main__":
    sys.exit(main())
