#!/usr/bin/env python
# coding: UTF-8

import sys
from math import sin, cos, radians, degrees, atan2, acos, pi
sys.path.append('../')
from bam import toFloat, BAM2float, float2BAM

## Return m1 x m2 (m1 multiplied by m2).
matMul = lambda m1, m2: [[sum(i*j for i, j in zip(row, col)) for col in zip(*m2)] for row in m1]

## Return m x v (vector multiplied by matrix).
vecMul = lambda m, v: [sum(i*j for i, j in zip(row, v)) for row in m]

## Return vector v2 + v1.
vecAdd = lambda v1, v2: [(i+j) for i,j in zip(v2,v1)]

## Return vector v * s.
vecScale = lambda v,s: [i*s for i in v]

## Return a nxn identity matrix.
identMat = lambda n: [[int(x==y) for x in range(n)] for y in range(n)]

## Return a null vector of dimension n.
nullVec = lambda n: [0]*n

## Dot product of vectors v0 and v1.
dotProd = lambda v0,v1: sum([u*v for u,v in zip(v0,v1)])

## Cross product of vectors u and v.
def crossProd (u,v): return u[0]*v[1]-v[0]*u[1]

## counter-clockwise rotation about the Z axis
ROT_Z = lambda z: [[cos(z), -sin(z), 0, 0],
                   [sin(z),  cos(z), 0, 0],
                   [  0,       0,    1, 0],
                   [  0,       0,    0, 1]]

def title(s):
    pass

def setup (width, height, startx=0, starty=0):
    pass

def bgcolor (r,g,b):
    pass

def window_width():
    return 0

def window_height():
    return 0

def setworldcoordinates(x0,y0,x1,y1):
    pass

def speed(v):
    pass

class FlailDriver:

    ## integer format
    formati = "(%d);\n"
    ## unsigned format
    formatu = "(%u);\n"
    ## Matrix and vector dimension: 3x3 or 4x4.
    #  Note that matMul will work even ROT_Z being 4x4 and MDIM being 3.
    MDIM = 4

    def __init__(self, shape, visible):
        ## file handle for turtle-flail commands.
        self.f = open("../files/output.flail","w+")
        self.f.write("SetMode(distance);\n")
        ## file handle for gps coordinates.
        self.g = None

        self.wptOrder = 0
        self.altitude = 0

        ## Initial direction. Does not change.
        self.initialVector = nullVec(FlailDriver.MDIM)
        self.initialVector[0] = 1

        fmt = "%f, "*(len(self.initialVector)-1)
        ## format for printing a point.
        self.formatp = fmt[0:-2]+"\n"

        self.reset()

    def writePos(self):
        if self.g is None:
           self.g = open("../files/gps.txt","w+")

        p=map.windowToViewport(self.curPoint[0:-1])[0]

        waypointOrder = self.wptOrder
        msnStart = 1 if waypointOrder == 0 else 0 # mission start - 1, not - 0
        coordFrame = 0 if waypointOrder == 0 else 3 # absolute - 0, relative - 3
        actWpt = 16 # waypoint - 16, first entry is home
        timeLtr = 0
        uncRad = 5
        wptRad = 0
        yawRot = self.heading()
        lat = p[0]
        lon = p[1]
        alt = self.altitude
        contAuto = 1

        if waypointOrder == 0:
            self.g.write("QGC WPL 110\n")

        self.g.write("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%f\t%f\t%f\t%f\t%d\n" %
                     (waypointOrder, msnStart, coordFrame, actWpt, timeLtr, uncRad, wptRad, yawRot, lat, lon, alt, contAuto))

        #self.g.write(self.formatp % tuple(self.curPoint[0:-1]))

    def setposition(self, x, y):
        pass

    def goto(self, x, y):
        pass

    def write(self,t):
        pass

    def dot(self):
        pass

    def penup(self):
        pass

    def home(self):
        pass

    def pendown(self):
        pass

    def reset(self):
        print("RESET")
        if self.g is not None:
           self.g.close()
           self.g = None

        ## Current position.
        self.curPoint = nullVec(FlailDriver.MDIM)
        self.curPoint[-1] = 1

        ## Holds accumulated rotations.
        self.rotMatrix = identMat(FlailDriver.MDIM)

        ## Current direction.
        self.curVector = self.initialVector[:]

        self.writePos()

    def pensize(self, val):
        pass

    def color(self, c):
        pass

    def setheading(self, h):
        m = ROT_Z(radians(h))
        v = vecMul(m,self.initialVector)
        ang = float2BAM(degrees(acos(dotProd(self.curVector,v))))
        if crossProd(self.curVector,v) > 0:
           self.left(ang)
        else:
           self.right(ang)

    def heading(self):
        return degrees(atan2(-self.curVector[1],-self.curVector[0])+pi)


    def forward(self, dist):
        if dist != 0:
            # update current position
            self.curPoint = vecAdd(self.curPoint, vecScale(self.curVector, toFloat(dist)))
            self.f.write("Forward" + FlailDriver.formati % dist)
            self.wptOrder+=1
            self.writePos()

    def backward(self, dist):
        if dist != 0:
            # update current position
            self.curPoint = vecAdd(self.curPoint, vecScale(self.curVector, toFloat(-dist)))
            self.f.write("Backward" + FlailDriver.formati % dist)
            self.wptOrder+=1
            self.writePos()

    def left(self, ang):
        if ang != 0:
            self.rotMatrix = matMul(self.rotMatrix, ROT_Z(radians(BAM2float(ang))))
            self.curVector = vecMul(self.rotMatrix,self.initialVector)
            self.f.write("RollLeft" + FlailDriver.formatu % ang)

    def right(self, ang):
        if ang != 0:
            self.rotMatrix = matMul(self.rotMatrix, ROT_Z(radians(BAM2float(-ang))))
            self.curVector = vecMul(self.rotMatrix,self.initialVector)
            self.f.write("RollRight" + FlailDriver.formatu % ang)

    def ascend(self, dist):
        if dist != 0:
            self.f.write("Ascend" + FlailDriver.formati % dist)
            self.altitude += toFloat(dist)
            print(dist)

    def descend(self, dist):
        if dist != 0:
            self.f.write("Descend" + FlailDriver.formati % dist)

    def repeat(self, n, instructions):
        self.f.write("Repeat " + str(n) + " {\n")

        for f in instructions:
            # Given a tuple: (func, par), call func(par)
            f[0](*f[1:])
        self.f.write("}\n")

    def __del_(self):
        self.f.close();
        self.g.close();

def main():
    f = FlailDriver(0,0)
    f.right(float2BAM(30))
    print(f.heading())    # 330
    f.setheading(120)
    print(f.heading())    # 120
    f.left(float2BAM(45)) # 165
    print(f.heading())

if __name__=="__main__":
   sys.exit(main())
