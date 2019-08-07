#!/usr/bin/env python
# coding: UTF-8
#
## @package smooth
#
#  Laplacian smooth.
#  - Finite difference discretization of second derivative = Laplace operator in one dimension.
#  - @f$L(p_i) = \frac{1}{2} (p_{i+1}+p_{i-1}) - p_i@f$
#  
#  Repeat for m iterations:
#  - @f$p_i \rightarrow p_i + \lambda L(p_i)@f$
#
#  @author Flavia Roma.
#  @date 15/06/2019
#
#  @see http://graphics.stanford.edu/courses/cs468-10-fall/LectureSlides/06_smoothing.pdf
#  @see https://cs.nyu.edu/~panozzo/ustc/05%20-%20Laplacian%20Operator.pdf

import math, sys

## Removes noisy points, that is, too distant from the curve.
#  Edges too long have their vertices projected onto the segment
#  connecting the previous and next vertices.
#
#  @param origproj array with 3D points.
#  @param niter number of iterations.
#
def smoothProj (origproj, niter=10):
    # origproj can be a list of tuples and we need a list of lists.
    proj = list(map(list,origproj))

    # length of vector (p-q).
    dist   = lambda p,q: math.sqrt(sum([(i-j)**2 for i,j in zip(p,q)]))
    # middle point of segment p,q.
    median = lambda p,q: [(i+j)*0.5 for i,j in zip(p,q)]

    avgEdgeLen = 0
    # find the average edge length
    for i in range(1, len(proj)): 
        avgEdgeLen += dist(proj[i],proj[i-1])
    avgEdgeLen /= (len(proj)-1)

    maxLen = avgEdgeLen*1.2
    if smoothProj.toDebug:
       print (avgEdgeLen)

    nrelax = 0
    for steps in range(0, niter):
        newproj = [proj[0]]
        # for each point i, calculate L(pi)
        for i in range(1, len(proj)-1):
            a,b,c = proj[i-1],proj[i],proj[i+1]
            # pi -->  L(pi) + pi for "long" edges only.
            if (dist(a,b) > maxLen and dist(b,c) > maxLen):
                newproj.append ( median(a,c) )
                nrelax += 1
            else: newproj.append(b)
        newproj.append(proj[-1])

        # for each point i, pi = 1/2 (pi + (L(pi) + pi)) = pi + 1/2 L(pi)
        for i in range (1, len(proj)-1):
            p,q = proj[i],newproj[i]
            for i,j in enumerate(median(p,q)):
                p[i] = j 
    if smoothProj.toDebug:
       print (nrelax, "relaxations")
    return proj
smoothProj.toDebug = False

def main(argv=None):
    if argv is None:
       argv = sys.argv

    import pylab as plt

    pts = [[0,1.5,7],[2,2,7],[3,1,7],[4,0.5,7],[4.5,15,7],[5,1,7],[6,2,7],[7,3,7]]
    #pts = [[0,1.5],[2,2],[3,1],[4,0.5],[4.5,15],[5,1],[6,2],[7,3]]
    if len(argv) > 1:
       smoothProj.toDebug = True
    print(pts)
    x,y,z = zip(*pts)
    plt.plot(x,y)
    pts = smoothProj(pts,3)
    print(pts)
    # Convert the Catmull-Rom curve points into x and y arrays and plot
    x,y,z = zip(*pts)
    plt.plot(x,y)
    plt.show()

if __name__=="__main__":
    sys.exit(main())
