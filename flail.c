/** @file flail.c
 *
 *  A very simple script interpreter 
 flail.
 *
 *  This program reads a file, containing flail commands, line by line.
 *  The lines are then split at white spaces, and an array of tokens is created.
 *  The number of white spaces is irrelevant.
 *
 *  Each array of tokens can contain:
 *      - An embedded command
 *      - A comment
 *  - A function call
 *      - A mixture of the above
 *
 *  For instance: 
 *      
 *  - func roll (int ang) { # rotate by ang  
 *
 *  - Number of tokens = 5 (tokens after a '#' are discarded)
 *
 *  <PRE>
 *         tokens[0]: func
 *         tokens[1]: roll
 *         tokens[2]: (int
 *         tokens[3]: ang)
 *         tokens[4]: {
 *         tokens[5]: #
 *         tokens[6]: rotate
 *         tokens[7]: by
 *         tokens[8]: ang
 *  </PRE>
 *
 *  The interpreter will then treat 'roll' as a function call. 
 *
 *  - The commands implemented are:
 *
 *      1. forwards 
 *      2. backwards
 *      3. left
 *      4. right
 *      5. roll
 *
 *  - To compile:
 *    - gcc flail.c -o flail-linux64
 *
 *  @author Flavia Roma
 *  @since 08/27/2018
 *
 *  @see http://www.quora.com/How-do-you-write-a-C-program-to-split-a-string-by-a-delimiter
 *  @see http://linux.die.net/man/3/strtok_r
 *  @see http://chris-sharpe.blogspot.com.br/2013/05/better-than-systemtouch.html
 *  @see http://creativeandcritical.net/str-replace-c 
 */
 
 
//#include "flail.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <stdarg.h>
#include <fcntl.h>
 
#if 1
#define __DEBUG__
#else
#undef  __DEBUG__
#endif
 
typedef unsigned char byte;
 
size_t bytes_alloc = 1;
size_t bytes_used = 0;
byte* bytes = NULL; 
 
/**
 *  Predicate for checking whether a string is made up entirely
 *  of white spaces (possibly with a newline ('\\n') at the end).
 *
 *  @param str given string.
 */ 
int isBlank ( const char * str ) {
    int i;
    if ( str == NULL ) return 1;
    for ( i = 0; i < strlen(str); ++i ) {
          if ( str[i] != ' ' && str[i] != '\n' ) return 0;
    }
    return 1;
}
 
/** Looks for a token beginning with '#', and updates
 *  the number of tokens to discard the next tokens.
 *
 * @param tokens array of tokens.
 * @param n number of tokens.
 * @return 1 if a comment was found, and 0 otherwise.
 */
int findComment ( char * const *tokens, size_t * n ) {
    size_t i;
    if ( tokens == NULL ) return 1;
    for ( i = 0; i < *n; ++i ) {
          if ( tokens[i][0] == '#' ) {
                  *n = i;
                  return 1;
          }
    }
    return 0;
}
 
/**
 *  Returns to the heap, the memory allocated for the array of tokens.
 *
 *  @param tokens array of tokens (arrays of char).
 *  @param nt tokens size.
 */
void freeTokens ( char** tokens, size_t nt ) {
   int i =0;
   if ( tokens == NULL ) return;
   for ( i = 0; i < nt; ++i )
        free (tokens[i]);
   free(tokens);
}
 
/** Splits a string in a set of tokens, using a given string as delimiter.
 *
 * @param str given string.
 * @param delim delimiter.
 * @param numtokens number of tokens found.
 * @return array of tokens (arrays of char).
 */
char **strsplit(const char* str, const char* delim, size_t* numtokens) {
     // copy the original string so that we don't overwrite parts of it
     // (don't do this if you don't need to keep the old line,
     // as this is less efficient)
     char *s = strdup(str);
      
     // these three variables are part of a very common idiom to
     // implement a dynamically-growing array
     size_t tokens_alloc = 1;
     size_t tokens_used = 0;
     char **tokens = calloc(tokens_alloc, sizeof(char*)); // calloc() zero-initializes the buffer, 
                                                          // while malloc() leaves the memory uninitialized.
     char *token, *strtok_ctx;
 
      /*As described by man strtok_r - On the first call to strtok_r(), str should point to the string  to  be
      parsed,  and the value of saveptr is ignored.  first call to strtok_r(), str should point to the string  to  be
      parsed,  and the value of saveptr is ignored.  In subsequent calls, str
      should be NULL, and saveptr should  be  unchanged  since  the  previous
      call.In subsequent calls, str should be NULL, and saveptr should  be  unchanged  
        since  the  previous call.
      */
     for (token = strtok_r(s, delim, &strtok_ctx); token != NULL; token = strtok_r(NULL, delim, &strtok_ctx)) {
          // check if we need to allocate more space for tokens
          if (tokens_used == tokens_alloc) {
              tokens_alloc *= 2;
              tokens = realloc(tokens, tokens_alloc * sizeof(char*));
          }
          tokens[tokens_used++] = strdup(token);
     }
       
     // cleanup
     if (tokens_used == 0) {
         free(tokens);
         tokens = NULL;
     } else {
         // attempts to resize the memory block pointed to by tokens
         // that was previously allocated with a call to malloc or calloc.
         tokens = realloc(tokens, (tokens_used+1) * sizeof(char*));
         tokens[tokens_used] = NULL; // lets put a (char *)0 to mark the end of the array
     }
     *numtokens = tokens_used;
     free(s);
 
     return tokens;
}
 
// Reallocates more space for the bytes array if necessary
void checkByteArrSize() {
    if (bytes_used == bytes_alloc) {
        bytes_alloc *= 2;
        bytes = realloc(bytes, bytes_alloc * sizeof(byte*));    
    }
}
 
void printByteArr() {
   int i;
	if (bytes_used > 0) {	
		printf("Byte Array -> [");
		for (i = 0 ; i < bytes_used - 1; i+=2) {
		     printf("%d (%d), ", bytes[i], bytes[i+1]);
		}
		printf("]\n");
	}
}
 
/**
 *  Executes the command corresponding to the given array of tokens.
 *  The first token is the command name, and the following tokens, its arguments.
 *
 *  @param tokens array of tokens.
 *  @param nt number of tokens in the array.
 *  @return 0 if no error has occurred.
 *
 *  @see http://www.manpagez.com/man/3/setenv/
 *  @see http://ss64.com/bash/export.html
 */
int interpretTokens(char **tokens, size_t nt){ 
   char* cmd;
   byte c; 
   int param, i;
 
   // No tokens given
   if (nt < 1) return -1;
 
   checkByteArrSize();
 
   cmd = tokens[0];
   if (!strcmp(cmd, "Forward")) {  
        c = 0;
   } else if (!strcmp(cmd, "Backward")) {
        c = 1;
   } else if (!strcmp(cmd, "Left")) {
        c = 2;
   } else if (!strcmp(cmd, "Right")) {
        c = 3;
   } else if (!strcmp(cmd, "Roll")) {
        c = 4;
   } else {
		printf("\nINVALID COMMAND found: %s \n", cmd );
		exit(1);
	}

    bytes[bytes_used++] = c;
 
    checkByteArrSize();
 
    param = atoi(tokens[1]) % 255; //Take the second argument in tokens which would be a number, and convert it to a character. Add it to the bytes array. NOTE - currently modded by 255 to prevent errors.
 
    bytes[bytes_used++] = (byte) param;
     
}
 
/**
 *  Reads a file containing a subset of bash commands and interprets them.
 *
 *  @param script - name of the script file.
*/
int parseScript(const char* script) {
    FILE *fp;
    int i;
    size_t nt; // number of tokens
    char buf[256]; // lines limited to 256B
    char **tokens = NULL;
 
    fp = fopen(script, "r");
     
    if (fp == NULL){
        printf ("Can't open file %s\n", script);
        exit(1);
   } else {
         
        /*if (fgets(buf, sizeof(buf)-1, fp ) == NULL) {
              printf ("No script provided or empty file\n");
              exit(1);
        }*/
 
        // fgets reads a file until an EOF or NULL is found
        // It stops reading a lineafter finding a /n and includes it in the buffer
        while ( fgets ( buf, sizeof(buf)-1, fp ) != NULL ) {  
            // Remove /n from the buffer string
            if (buf[strlen(buf)-1] == '\n')              
                 buf[strlen(buf)-1] = '\0';
 
                // Check for empty lines
            if (isBlank(buf)) continue;
 
				char delim[] = " ,(,),;";
            tokens = strsplit (buf, delim, &nt); 
            findComment (tokens, &nt);
 
 
            #ifdef __DEBUG__
             //findComment (tokens, &nt);
             fprintf (stderr, "\nnumber of tokens = %lu\n", nt);
 
             for (i = 0; i < nt; ++i) {
                   fprintf (stderr, "token %d: %s\n", i, tokens[i]);
             }
            #endif
 
             if (nt) {
 
                //char** split = splitFuncParam(tokens);
                interpretTokens (tokens, nt);
 
                // attempts to resize the memory block pointed to by bytes
                // that was previously allocated with a call to malloc or calloc.
                bytes = realloc(bytes, (bytes_used + 1) * sizeof(byte));
                bytes[bytes_used] = '\0'; // lets put a (char *)0 to mark the end of the array
                
             }
 
             // If the tokens array was successfully allocated, free every element
            if (tokens) {
                freeTokens(tokens,nt);
                tokens = NULL;
            }
        }
    }
 
    return 0;
}


/**
* Create a boilerplate file for the arduino containing the byte array and a function to interpret the commands.
*/
void createBoilerplate() {
	char* boilerplate = "boilerplate.c";
	
	// Remove any pre-existent copy of boilerplate.c before writing to the file.
	remove(boilerplate);
	
	FILE *fp = fopen(boilerplate, "ab+");
	fprintf(fp, "#include <stdio.h>\n#include <stdlib.h> \n#include <string.h> \n\n");
	fprintf(fp, "typedef unsigned char byte; \n");

	fprintf(fp, "size_t size = %d; \n\n", bytes_used + 1);

	int i;
	if (bytes_used > 0) {	
		fprintf(fp, "byte bytes[%d] = {", bytes_used + 1); // make enough space for '\0' at the end
		for (i = 0 ; i < bytes_used; i++) {
			fprintf(fp, "0x%x, ", bytes[i]);
		}
		fprintf(fp, "'\\0'};\n");
	}

	fprintf(fp, "void interpretBytes() { \n \
	\tint i; \n\
	\tint param;\n\n \
	\tfor (i = 0; i < size - 1; i += 2) { \n\
	\t\tparam = bytes[i+1];\n \
	\t\tswitch(bytes[i]) { \n \
	\t\t\tcase 0x0: \n\
	\t\t\t\tprintf(\"Forward\"); \n\
	\t\t\t\tbreak; \n\n\
	\t\t\tcase 0x1: \n\
	\t\t\t\tprintf(\"Backwards\"); \n\
	\t\t\t\tbreak; \n\n\
	\t\t\tcase 0x2: \n\
	\t\t\t\tprintf(\"Left\"); \n\
	\t\t\t\tbreak; \n\n\
	\t\t\tcase 0x3: \n\
	\t\t\t\tprintf(\"Right\"); \n\
	\t\t\t\tbreak; \n\n\
	\t\t\tcase 0x4: \n\
	\t\t\t\tprintf(\"Roll\"); \n\
	\t\t\t\tbreak; \n\n\
	\t\t\tdefault: \n\
	\t\t\t\tbreak; \n\
	\t\t} \n\
	\t} \n\
	} \n\n\
	int main() { \n\
	\tinterpretBytes(); \n\
	}");
}

int main(int argc, char* argv[]) {
 
    bytes = calloc(bytes_alloc, sizeof(byte*));
    char filename[256];
 
    if (argc < 2) {
        printf ("\nFlail: No file was given.\n\n");
        exit(1);    
    }
 
    // to prevent trash from appearing in "filename", fill it with '0's
    memset(filename, '\0', sizeof(filename)); 
 
    // save the first argument passed on the command line to "filename"
    // Strncpy - warning - if there are no null byte among the first n bytes of the src, the string placed
    // indest will not be null-terminated. 
    strncpy (filename, argv[1], sizeof(filename)-1); 
     
    parseScript (filename);
    printByteArr();

	createBoilerplate();
}
