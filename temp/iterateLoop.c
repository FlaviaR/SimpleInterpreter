#include "flail.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <stdarg.h>
#include <fcntl.h>

// Bytes allocated for the final command byte array
size_t bytes_alloc = 1;
size_t bytes_used = 0;
byte* bytes = NULL;

UsedInstructions* usedInstructions;

// Bytes allocated for the loop byte array
size_t loopB_alloc = 1;
size_t loopB_used = 0;
byte* loopBytes = NULL;

int numberOfRepetitions = 2;

// Reallocates more space for the given bytes array if necessary
void checkByteArrSize(byte** byteArr, size_t num_bytes_used, size_t* num_bytes_alloc) {
    if (num_bytes_used == *num_bytes_alloc) {
        *num_bytes_alloc *= 2;
        *byteArr = realloc(*byteArr, *num_bytes_alloc * sizeof(byte));
    }
}

// Print the finalized byte array which at this point should contain all converted instructions
void printByteArr(byte* byteArr, size_t num_bytes_used) {
    int i;
    if (num_bytes_used > 0) {
        printf("Byte Array -> [");
        for (i = 0 ; i < num_bytes_used; i+=2) {
            printf("%d (%d), ", byteArr[i], byteArr[i+1]);
        }
        printf("]\n");
    }
}

// Iterate through the loop array and add the stored commands 'numberOfRepetitions' times to the byte array.
void iterateLoopArr() {
    int i, j;
    if (loopB_used > 0) {
        for (i = 0; i < numberOfRepetitions; i++) {
            for (j = 0 ; j < loopB_used; j++) {
                checkByteArrSize(&bytes, bytes_used, &bytes_alloc);
                bytes[bytes_used++] = loopBytes[j];
            }
        }
    }
}

int main(int argc, char* argv[]) {
    
    
    bytes = calloc(bytes_alloc, sizeof(byte));
    
    loopB_used = 12;
    loopBytes = calloc(loopB_used, sizeof(byte));

    loopBytes[0] = 0x5;
    loopBytes[1] = 0x23;
    loopBytes[2] = 0xa;
    loopBytes[3] = 0xff;
    loopBytes[4] = 0xa;
    loopBytes[5] = 0xff;
    loopBytes[6] = 0xa;
    loopBytes[7] = 0xff;
    loopBytes[8] = 0xa;
    loopBytes[9] = 0xeb;
    loopBytes[10] = 0x5;
    loopBytes[11] = 0x0;
    loopBytes[12] = '\0';
    

    iterateLoopArr();
    printByteArr(loopBytes, loopB_used);

    // attempts to resize the memory block pointed to by bytes
    // that was previously allocated with a call to malloc or calloc.
    bytes = realloc(bytes, (bytes_used + 1) * sizeof(byte));
    bytes[bytes_used] = '\0'; // lets put a (char *)0 to mark the end of the array
    
    printByteArr(bytes, bytes_used);
    
}
