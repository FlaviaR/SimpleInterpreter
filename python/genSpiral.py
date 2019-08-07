import math
# Generate a list of points of a 3D spiral
# x = cx + r * sin(a)
# y = cy + r * cos(a)
# where x,y is a resultant point in the circle's circumference
# cx, cy is the center of the spiral
# r is the radius of the circle
# a is the current angle - vary from 0 to 360 or 0 to 2PI

def generateSpiral(r, cx, cy):
	
	f= open("spiral.txt","w+")

	a = 0
	z = 0
	
	for a in range (0, 7):
		x = cx + r * math.cos(a)
		z = cx + r * math.sin(a)
		y = 0
#		z += 10
#		r += 5

		f.write("%d, %d, %d\n" %(x,y,z))

generateSpiral(10, 0, 0)


