#!/usr/bin/env python
# coding: UTF-8
#
## @package CatmullRom
#
#  Catmull-Rom spline algorithm.
#
#  @author Flavia Roma.
#  @date 13/06/2019
#
#  In computer graphics, centripetal Catmull–Rom spline is a variant form of Catmull-Rom spline 
#  formulated by Edwin Catmull and Raphael Rom according to the work of Barry and Goldman.
#
#  It is a type of interpolating spline (a curve that goes through its control points) defined by 
#  four control points @f$P_0, P_1, P_2, P_3@f$ with the curve drawn only from @f$P_1\ to\ P_2@f$. 
#
#  @see https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline
#
import numpy, sys, math

def CatmullRomSpline(P0, P1, P2, P3, nPoints=100):
  """
  P0, P1, P2, and P3 should be (x,y,z) point triples that define the Catmull-Rom spline.
  nPoints is the number of points to include in this curve segment.
  """
  # Convert the points to numpy so that we can do array multiplication
  P0, P1, P2, P3 = map(numpy.array, [P0, P1, P2, P3])

  # Calculate t0 to t4
  alpha = 0.5
  def tj(ti, Pi, Pj):
    return sum([(i-j)**2 for i,j in zip(Pi,Pj)])**alpha + ti

  t0 = 0
  t1 = tj(t0, P0, P1)
  t2 = tj(t1, P1, P2)
  t3 = tj(t2, P2, P3)

  # Only calculate points between P1 and P2
  t = numpy.linspace(t1,t2,nPoints)

  # Reshape so that we can multiply by the points P0 to P3
  # and get a point for each value of t.
  t = t.reshape(len(t),1)
  A1 = (t1-t)/(t1-t0)*P0 + (t-t0)/(t1-t0)*P1
  A2 = (t2-t)/(t2-t1)*P1 + (t-t1)/(t2-t1)*P2
  A3 = (t3-t)/(t3-t2)*P2 + (t-t2)/(t3-t2)*P3
  if CatmullRomSpline.toDebug:
     print(t)
     print(A1)
     print(A2)
     print(A3)
  B1 = (t2-t)/(t2-t0)*A1 + (t-t0)/(t2-t0)*A2
  B2 = (t3-t)/(t3-t1)*A2 + (t-t1)/(t3-t1)*A3

  C  = (t2-t)/(t2-t1)*B1 + (t-t1)/(t2-t1)*B2
  return C

CatmullRomSpline.toDebug = False

def CatmullRomChain(P,nP=100):
  """
  Calculate Catmull Rom for a chain of points and return the combined curve.
  """
  sz = len(P)

  # The curve C will contain an array of (x,y,z) points.
  C = []
  for i in range(sz-3):
    c = CatmullRomSpline(P[i], P[i+1], P[i+2], P[i+3], nP)
    C.extend(c)

  return C

def readPlistFile(fname):
    """"Read a point list file, and retun a list of 3D coordinates."""

    plist = []
    try:
      f = open(fname,'r')
    except IOError:
         print ('CatmullRom: Cannot open file %s for reading' % fname)
         raise
    for line in f:
        tempwords = [ t.strip('\n') for t in line.split(',') ]
        if len(tempwords) == 3:
           try:
               plist.append ([float(tempwords[0]), float(tempwords[1]), math.degrees(float(tempwords[2]))])
           except:
               print ('Número Inválido: %s\n' % tempwords)
               continue

    f.close()
    return plist

def main(argv=None):
    """
    Uses matplotlib for drawing a curve.
    """

    import pylab as plt

    if argv is None:
       argv = sys.argv

    # Define a set of points for curve to go through
    if len(argv) > 1:
       Points = readPlistFile(argv[1])
    else:
       Points = [[0,1.5,7],[2,2,7],[3,1,7],[4,0.5,7],[5,1,7],[6,2,7],[7,3,7]]

    # Turn debugging ON
    CatmullRomSpline.toDebug = False

    # Calculate the Catmull-Rom splines through the points
    c = CatmullRomChain(Points)

    # Convert the Catmull-Rom curve points into x and y arrays and plot
    x,y,z = zip(*c)
    plt.plot(x,y)

    # Plot the control points
    px, py, pz = zip(*Points)
    plt.plot(px,py,'or')

    #plt.show()

    # https://matplotlib.org/mpl_toolkits/mplot3d/tutorial.html

    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    import matplotlib.pyplot as plt

    mpl.rcParams['legend.fontsize'] = 10

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    #theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
    #z = np.linspace(-2, 2, 100)
    #r = z**2 + 1
    #x = r * np.sin(theta)
    #y = r * np.cos(theta)
    ax.plot(x, y, z, label='spline curve')
    ax.legend()

    plt.show()

if __name__=="__main__":
    sys.exit(main())
