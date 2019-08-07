#!/usr/bin/env python
# coding: UTF-8
#
## @package bam
#
#  Handle conversion to BAM angles.
#
#  @author Flavia Roma
#  @date 01/01/2019
#
import numpy, sys

from math import ldexp, frexp

## Whether using the flail driver for writing a file, instead of turtle for drawing on screen.
usingFlail = None

## Wraps an angle to @f$\pm 180@f$
#
#  @see <a href="https://books.google.com.br/books?id=zvsYCwAAQBAJ&pg=PA241#v=onepage&q&f=false">3D Math Primer for Graphics and Game Development, page 241</a>.
wrapPi = lambda x: x - 360 * ((x + 180) // 360)

## Toggle debugging mode.
__toDebug__ = False

## Number of bits after binary point.
NBITS = 8

## Scale for fixed point: 256 or 65536, for instance.
BSCALE = 2**NBITS # 1<<NBITS

## Maps a float number to integer.
#
#  @see https://www.youtube.com/watch?v=wbxSTxhTmrs&fbclid=IwAR2f04_45mIFGtIczSOzbB8nxfqb6SX0pkVlxySfnnBf4n6e8KdKRHXkY2I
#  @see https://www.cl.cam.ac.uk/teaching/1011/FPComp/fpcomp10slides.pdf?fbclid=IwAR3G7UxIIrOGxOUJq7IMp8rzZMlBUex-9ZRyCyu_842LxPDTWaWyb4Xvyjc
float2Int = lambda f: int(f*BSCALE)

## Maps an integer number to float.
 # Reconstruct the number with NBITS bits after the binary point.
int2Float = lambda b: ldexp(float(b),-NBITS) # b*(2**-NBITS)

## Convert a float number, representing a length, to an integer, with a fixed number of bits.
#
#  Since we use polar coordinates, angles should be thought of as going from 0 to 360.
#  Using two decimal places, this means going from 0 to 36000. 
#  - Therefore, 16 bits (2 bytes) are enough. For distances, this is also satisfactory, 
#    for radii (scales) not too small.
#  - To keep the integers small, we use BAM whenever possible, so only 2 bytes are enough. 
#  - For radius < 4, BAM does not provide the appropriate precision for distances, and the curve may not even close.
#
#  @see https://ipfs.io/ipfs/QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco/wiki/Binary_scaling.html
#  @see https://en.wikipedia.org/wiki/Binary_scaling
#  @see https://www.allaboutcircuits.com/technical-articles/fixed-point-representation-the-q-format-and-addition-examples/
#  @see https://www.eecs.umich.edu/courses/eecs373/readings/floating-point-to-fixed.pdf
#
def toInt (x):
    t = ""

    if -180 <= x and x < 180:
       i = float2BAM(x)
       t = "underflow = " if i == 0 else "BAM = "
    else:
       i = float2Int(x) 
   
    f = toFloat(i)
 
    if __toDebug__:
       bin = toBinary(i)
       print("length = %s%d = %s= %d" % (t, i, bin, toDenary(bin)))
       # Return the mantissa and exponent of x as the pair (m, e). 
       # m is a float and e is an integer such that x == m * 2**e exactly. 
       m, e = frexp(x)
       print("x = m * 2**e = %f * %f" % (m,2**e))
       print("x = %.4f, f = %.4f, err = %f\n" % (x,f, x-f))

    return i if usingFlail else f

## Get the float representation of an integer number.
def toFloat(b):
    if -32768 <= b < 32768:
       return BAM2float(b)
    else:
       return int2Float(b)

## Get the binary representation of a number, recursively.
#
#  @param num number to be parsed.
#  @param count number of bits generated so far.
#  @param sign string holding the sign of the number.
#  @return string representing the number, with the [amount] and its set of bits:
#  - e.g. toBinary(15)   --> '[4] 1 1 1 1'
#  - e.g. toBinary(-215) --> '[8] -1 1 0 1 0 1 1 1 '
#
def toBinary (num, count=0, sign=""):
    if count == 0 and num < 0:
       sign = "-"
       num = -num

    count += 1
    if num < 2:
       return ("[%d] %s%d " % (count, sign, num))
    #                           num//2                 num%2
    return ("%s%d " % (toBinary(num>>1, count, sign), (num&1)))

## Converts a string representing a binary number to denary.
def toDenary(b):
    a = b.split()[1:]
    sign = 1
    if a[0][0] == '-': # < 0
       sign = -1
       a[0] = '1'
    #return sign*_toDenary(a)
    return sign*_toDenaryRec(a)

## Return the decimal number represented by binary digits in a list.
#  Non recursive version.
#
def _toDenary(a):
    n = 0
    for i,d in enumerate(a):
        n += int(d)*2**(len(a)-1-i)
    return n

## Return the decimal number represented by binary digits in a list.
#  Recursive version.
#  
def _toDenaryRec(a):
    if len(a) == 0:
       return 0
    return _toDenaryRec(a[1:]) + int(a[0]) * 2**(len(a)-1)

## Convert an angle to UBAM.
#  The main advantage is using only two bytes,
#  instead of the eight bytes of a float. 
#
#  If the goal is to send angles through the net
#  or write them on a file, we save 75% of space this way.
#
#  @param x an angle as a float.
#  @return another float angle, after coding x using two bytes.
#
#  @see https://blogs.msdn.microsoft.com/shawnhar/2010/01/04/angles-integers-and-modulo-arithmetic/
def toUBAM(x):
    i = float2UBAM(x)
    f = BAM2float(i)
    if __toDebug__:
        bin = toBinary(i)
        print("angle = UBAM = %d = %s= %d" % (i,bin,toDenary(bin)))
        print("x = %.4f, f = %.4f, err = %f"  % (x,f, x-f))
    return i if usingFlail else f

## BAM bit table.
#
#  sum(bam_bit_table) = 359.9939
#
bam_bit_table = [ 0.0055, 0.0109, 0.0219, 0.0439, 0.088, 0.1757, 0.3515, 0.703, 1.406, 2.8125, 5.625, 11.25, 22.5, 45.0,  90.0, 180.0 ]
#           LSB = 0       1       2       3       4      5       6       7      8      9       10     11     12    13     14    15 = MSB

## Word size for BAM.
WSIZE = len(bam_bit_table)-1

## Least Significant Bit.
#  
# LSB = bam_bit_table[0] = 2**-15 * 180 = 0.0054931640625
#
LSB = 2**-WSIZE * 180

## Convert a float number to an Unsigned Binary Angle Measurement (UBAM).
#  BAM data words are specifically designed to represent up to @f$360^{\circ}@f$ 
#  of angular displacements in binary form, often in steps, or increments of, as 
#  small as the LSB value (@f$0.0055^{\circ}@f$ for a 16 bit word).
#
#  This 16-bit word '11001000 00000000' @f$(b_{15}*2^{15} + ... +\ b_0*2^{0})@f$ can represent a @f$281.25^{\circ}@f$ angle:
#  - 281.25 = 180 + 90 + 11.25 
#  - float2UBAM(281.25) = @f$(1<<15) + (1<<14) + (1<<11) = 2^{15} + 2^{14} + 2^{11}@f$ = 51200
#
#
#  When set to one, the LSB (Least Significant Bit) is equal to @f$0.0055^{\circ}@f$, 
#  while the MSB (Most Significant Bit) is equal to @f$180^{\circ}@f$. 
#  - The MSB value represents half the maximum value that may be transmitted. 
#
#  When all 16 bits are set:
#  - an angle greater than @f$359.9939^{\circ}@f$ is indicated, 
#  - their sum is 359.9939, and corresponds to the maximum quantity that can be transmitted. 
#
#  When all bits in the BAM data word are clear (with ZEROS), a @f$0^{\circ}@f$ angle is represented. 
#
#  BAM words are also used to transmit non-angular values, such as range, length or height. 
#  - When non-angular values are being used, the LSB value contains the smallest step,
#  or increment of the quantity being transmitted. 
#  
#  In C language, integers overflow behavior is different regarding the integer signedness.
#
#  Two situations arise: (Basics of Integer Overflow)
#  - signed integer overflow : undefined behavior
#  - unsigned integer overflow : safely wraps around (UINT_MAX + 1 gives 0)
#
#  One way, of mimicking this behaviour in Python, is using uint16 from numpy.
#
#  @param num a float number.
#  @return an Unsigned short integer [0 to 65535] corresponding to an angle [0 to 360).
#
#  @see https://github.com/borcun/bams/blob/master/bams.c
#  @see http://electronicstechnician.tpub.com/14091/css/Binary-Angular-Measurement-316.htm
#  @see https://loicpefferkorn.net/2013/09/python-force-c-integer-overflow-behavior/
#  @see https://docs.scipy.org/doc/numpy-1.13.0/user/basics.types.html
#
def float2UBAM (num):
    #num %= 360
    res = numpy.uint16(0)
    for i in range(WSIZE, -1, -1):
        if num >= bam_bit_table[i]:
           num -= bam_bit_table[i]
           res += numpy.uint16(1<<i)
    return res

## Convert a float number to a signed Binary Angle Measurement (BAM).
#
#  @param _num a float number.
#  @return a Short Integer [-32768 to 32767] corresponding to an angle [-180 to 180).
#
#  @see https://github.com/borcun/bams/blob/master/bams.c
#  @see http://electronicstechnician.tpub.com/14091/css/Binary-Angular-Measurement-316.htm
#
def float2BAM (_num):
    # _num = wrapPi(_num)
    # bring the sign back.
    res = numpy.int16(float2UBAM(abs(_num)))
    #res = int(float2UBAM(abs(_num)))
    return res if _num > 0 else -res

## Convert BAM to float.
#  Adding @f$180^{\circ}@f$ to any angle is analogous to taking its two's complement.
#
#  Consider the LSB (least significant bit) of an \e n-bit word to be
#  @f$2^{-(n-1)}@f$, with most significant bit @f$(MSB) = 180^{\circ}.@f$
#  - sum(v * ((b>>i)&1) for i,v in enumerate(bam_bit_table)) =
#  - @f$(180\ b_{15} + 90\ b_{14} + 45\ b_{13} + 22.5\ b_{12} + ... +\ 0.0055\ b_{0}) = @f$
#  - @f$180\ (b_{15} + b_{14}\ 2^{-1} + b_{13}\ 2^{-2} + b_{12}\ 2^{-3} + ... +\ b_{0}\ 2^{-15}) = @f$
#  - @f$180 * 2^{-15} (b_{15}\ 2^{15} + b_{14}\ 2^{14} + b_{13}\ 2^{13} + b_{12}\ 2^{12} + ... +\ b_{0}) = @f$
#  - @f$180 * 2^{-15} * b@f$
#
#  The range of any angle @f$\theta@f$ represented this way is:
#  - @f$0^{\circ} \le \theta \le 360 - 180 \times {2^{-(n-1)}}^{\circ}.@f$
#
#  @param b BAM angle.
#  @return a float pointing number: b * LSB * MSB.
#  @see https://www.cs.cornell.edu/~tomf/notes/cps104/twoscomp.html
#  @see <a href="https://books.google.com.br/books?id=T-KvN5OiZCEC&printsec=frontcover">Software Engineering for Image Processing Systems, Page 154</a>
#
def BAM2float(b):
    return b * LSB

## Show UBAM angle wrap around.
def main():
    turns = 0
    j = numpy.uint16(0)
    step = float2UBAM(bam_bit_table[12])
    print("step = %d" % step)
    while turns < 5:
          f = BAM2float(j)
          print("BAM = %d, f = %.3f" % (j,f))
          j += step
          if f == 0: turns += 1

if __name__=="__main__":
    sys.exit(main())
