/**
 * @source : https://wilke.de/uploads/media/REAL_TO_BAM_Conversion_03.tig
 */

#include <stdio.h>
#include <math.h>
#include <stdlib.h>

/* bam bit table */
double bam_bit_table[ 16 ] = { 0.0055, 0.0109, 0.0219, 0.0439, 0.088, 0.1757, 0.3515, 0.703, 1.406, 2.8125, 5.625, 11.25, 22.5, 45.0, 90.0, 180.0 };

void print2base( int num, int count ) {
  if( 0 == num ) {
    printf( "[%d] 0 ", ++count );
    return;
  }
  else if( 1 == num || -1 == num ) {
    printf( "[%d] 1 ", ++count );
    return;
  }

  print2base( num / 2, ++count );
  printf( "%d ", abs(num) % 2 );
}

// Wrapping an angle between +- 180.
double wrapPi (double theta) {
   if (fabs(theta) <= M_PI) {
       // One revolution is 2 PI.
       const double TWOPI = 2.0*M_PI; 

       // Out of range. Determine how many revolutions we need to add.
       double revolutions = floor((theta+M_PI) / TWOPI);

       // Subtract it off.
       theta -= revolutions * TWOPI;
   }
   return theta;
}

// [0,359] -> [0, 65535]
unsigned short realToUBAM( const double _num ) {
  double num = _num;
  unsigned short res = 0;
  int i;
  
  if( num == 360.0 )
    return 0;

  for( i=15 ; i >=0 ; --i ) {
    if( num >= bam_bit_table[ i ] ) {
      num -= bam_bit_table[ i ];
      res += pow( 2, i );
    }
  }
  return res;
}

// [-180, 179] -> [-32768, 32767]
signed realToBAM( const double _num ) {
  double num = _num;
  signed short res = 0;
  int i;
  
  num = wrapPi ( num );
  
  for( i=15 ; i >= 0 ; --i ) {
    if( fabs( num ) >= bam_bit_table[ i ] ) {
      num = fabs( num ) - bam_bit_table[ i ];
      res += pow( 2, i );
    }
  }
  return _num >= 0 ? res : -res; 
}

double UBAMToReal( unsigned short b ) {
    return b * 180 * pow(2, -15);
}

double BAMToReal( short b ) {
    return b * 180 * pow(2, -15);
}

double IntToReal( int b ) {
    int BSCALE = 1<<8;

    if (-32768 <= b && b < 32768) {
        return BAMToReal(b);
    } else {
        return (float)b/BSCALE;
    }
}

int main( int argc, char **argv ) {

  if ( argc < 2 ) {
      printf("%s\n", "Argument missing.");
      exit(0);
  }  
  double real = atof( argv[1] );
  unsigned short ubam;
  short bam;
  
  ubam = realToUBAM( real );
  bam = realToBAM( real );

  printf( "%f degree = %u UBAM = %d BAM = ", real, ubam, bam );
  print2base( bam, 0 );
  printf( "binary\n" );
  printf("float(%u) = %f\n", ubam, UBAMToReal(ubam) );
  printf("float(%d) = %f\n", bam, BAMToReal(bam) );

  printf("float(%d) = %f\n", bam, IntToReal(bam) );
  printf("float(%d) = %f\n", 32767, IntToReal(32767) );
  printf("float(%d) = %f\n", 46080, IntToReal(46080) );

  // unsigned integer overflow : safely wraps around (UINT_MAX + 1 gives 0)
  printf("BAM(359) + BAM(5) = %f\n", BAMToReal(realToBAM(359) + realToBAM(5)));
  
  return 0;
}
