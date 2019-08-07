## Class for handling the mapping from window coordinates
#  to viewport coordinates.
#
class mapper:
    ## Constructor.
    #
    #  @param world window rectangle.
    #  @param viewport screen rectangle.
    #  @param noDistortion whether to use the same scale for both X and Y.
    #
    def __init__(self, world, viewport, noDistortion=False):
        self.world = world
        self.viewport = viewport
        x_min, y_min, x_max, y_max = self.world
        X_min, Y_min, X_max, Y_max = self.viewport
        self.fx = float(X_max-X_min) / float(x_max-x_min)
        self.fy = float(Y_max-Y_min) / float(y_max-y_min)

        if noDistortion:
           self.f = min(self.fx,self.fy)
           self.fx = self.fy = self.f

        x_c = 0.5 * (x_min + x_max)
        y_c = 0.5 * (y_min + y_max)
        X_c = 0.5 * (X_min + X_max)
        Y_c = 0.5 * (Y_min + Y_max)
        self.c_1 = X_c - self.fx * x_c
        self.c_2 = Y_c - self.fy * y_c

    ## Maps a single point from world coordinates to viewport (screen) coordinates.
    #
    #  @param x, y given point.
    #  @return a new point in screen coordinates.
    #
    def __windowToViewport(self, x, y):
        X = (self.fx * x + self.c_1)
        Y = (self.fy * y + self.c_2) 
        return X , Y

    ## Maps a single point from screen coordinates to window (world) coordinates.
    #
    #  @param x, y given point.
    #  @return a new point in world coordinates.
    #
    def viewportToWindow(self, x, y):
        X = (x - self.c_1) / self.fx
        Y = (y - self.c_2) / self.fy
        return X , Y

    ## Maps points from world coordinates to viewport (screen) coordinates.
    #
    #  @param p a variable number of points.
    #  @return two new points in screen coordinates.
    #
    def windowToViewport(self,*p):
        return [self.__windowToViewport(x[0],x[1]) for x in p]

if __name__ == "__main__":
    # maps the unit rectangle onto a viewport of 400x400 pixels.
    map = mapper([-1,-1,1,1], [0,0,400,400])
    p1, p2 = map.windowToViewport((0,0),(1,1))
    p = map.viewportToWindow(400,400)
    print ("%s - %s" % (p1,p2)) # (200, 200) - (400, 0)
    print ("(%d,%d)" % p)       # (1,1)
