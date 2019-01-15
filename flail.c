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
 *       - A function call
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


#include "flail.h"
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

#define PERCENT_TO_INT(x) ((int)(atof(x) * 100))
#define INCREMENT_LAST (*num_bytes_used)++


byte* bytes = NULL;
size_t bytes_alloc = 16;
size_t bytes_used = 0;

UsedInstructions* usedInstructions;


byte* loopBytes = NULL;
size_t loopB_alloc = 16;
size_t loopB_used = 0;
// Are we currently within a "Repeat" loop?
bool inRepeatLoop = false;
// How many repetitions must the loop execute?
int numberOfRepetitions = 0;

/** Current interpretation mode.
* The default is to expect intensity parameters.
* The setMode instruction must be called to alternate between intensity and distance.
* Where intensity bases the movement of the drone off of some percentage of its maximum speed,
* while the distance expects integer values to designate the distance to be traveled.
*/
enum mode mode;

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
    *tokens = NULL;
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

// Adds the given byte to 'byte array' and reallocates more space if necessary
void addToBytes(byte toAdd) {

    if (bytes_used >= bytes_alloc) {
        bytes_alloc *= 2;
        bytes = realloc(bytes, bytes_alloc * sizeof(byte));
    }

	bytes[bytes_used++] = toAdd;
}

// Adds the given byte to 'loopBytes array' and reallocates more space if necessary
void addToLoopBytes (byte toAdd) {

    if (loopB_used >= loopB_alloc) {
        loopB_alloc *= 2;
        loopBytes = realloc(loopBytes, loopB_alloc * sizeof(byte));
    }

	loopBytes[loopB_used++] = toAdd;
}

// Adds the given byte to either loopBytes or to bytes depending on whether inRepeatLoop is set or not.
void addToByteArray(byte toAdd) {
	if (inRepeatLoop) addToLoopBytes(toAdd);
	else addToBytes(toAdd);
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

// Launch error if instructions aren't separated by a ';' within the token array 
void tokenizationError() {
    printf("\nTokenization error: Make sure that your instructions are separated by a ';'.\n\n");
    exit(1);
}

// Thrown when the intensity parameter is not within the [0.0, 1.0] range
void percentageError() {
    printf("\nParameter error: Make sure that the given percentage parameters are between 0.0 and 1.0.\n\n");
    exit(1);
}

// Thrown when an instruction is called and never reset before a conflicting instruction is called.
// Should only be considered when in intensity mode, as multiple instructions can be set at once in this mode.
// Ex: Left(0.95);
//     Right(0.75);
void usageError(char** tokens) {
    if (mode != distance) {
        printf("Conflicting instructions found before %s %s. Please re-check your work.\n\n", tokens[0], tokens[1]);
        exit(1);
    }
}

void repeatSyntaxCheck(char **tokens, size_t nt) {
    
    // it is expected that a "repeat" command will always be followed by the number of repetitions
    // required for the loop
    if (nt < 2) {
        printf ("Parameter error: Make sure that the 'Repeat' command is followed by the number of required repetitions. \n\n");
        exit(1);
    }
    
    if (nt >= 3) {
        if (strcmp(tokens[2], "{")) {
            printf ("Parameter error: Make sure that 'Repeat' follows the following structure: 'Repeat [times] [{] [commands] [}]. \n\n");
            exit(1);
        }
    }
}

// Iterate through the loop array and add the stored commands 'numberOfRepetitions' times to the byte array.
void iterateLoopArr() {
    int i, j;
    for (i = 0; i < numberOfRepetitions; i++) {
        for (j = 0 ; j < loopB_used; j++) {
			addToBytes(loopBytes[j]);
        }
    }
}

// Keep track of which instructions are currently active
// Reset them when the parameter is 0
void trackInstruction(int* inst, int param) {
    *inst = (param > 0) ? 1 : 0;
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
    // Command found in file
    char* cmd;
    // Corresponding command byte to be added to the byte array
    byte c;
    // Parameter associated with the command found in file
    int param, i;
    
    // No tokens given
    if (nt < 1) return -1;
    
    cmd = tokens[0];
    
    // Currently, it is expected that each token array will contain two elements,
    // an instruction and a parameter, if there are more elements, then the instructions probably
    // weren't split correctly by a ';'
    // The only exception is the 'Repeat' command.
    if (nt > 2 && strcmp(cmd, instList.repeat)) tokenizationError();
    
    if (!strcmp(cmd, instList.repeat)) {
        repeatSyntaxCheck(tokens, nt);
        
        if (inRepeatLoop) {
            printf ("\nError: Do not use nested loops. Exiting...\n\n");
            exit(0);
        }
        
        inRepeatLoop = true;
        numberOfRepetitions = atoi(tokens[1]);
        
    } else if (!strcmp(cmd, "}") && inRepeatLoop) {
        inRepeatLoop = false;
        
        loopBytes = realloc(loopBytes, (loopB_used + 1) * sizeof(byte));
        loopBytes[loopB_used] = '\0';
        iterateLoopArr();
        
    } else {
        
        if (!strcmp(cmd, instList.ascend)) {
            if (usedInstructions->descend > 0) usageError(tokens);
            c = inst.ascend;
            trackInstruction(&(usedInstructions->ascend), param);
            
        } else if (!strcmp(cmd, instList.forward)) {
            if (usedInstructions->backward > 0) usageError(tokens);
            c = inst.forward;
            trackInstruction(&(usedInstructions->forward), param);
            
        } else if (!strcmp(cmd, instList.backward)) {
            if (usedInstructions->forward > 0) usageError(tokens);
            c = inst.backward;
            trackInstruction(&(usedInstructions->backward), param);
            
        } else if (!strcmp(cmd, instList.left)) {
            if (usedInstructions->right > 0) usageError(tokens);
            c = inst.left;
            trackInstruction(&(usedInstructions->left), param);
            
        } else if (!strcmp(cmd, instList.right)) {
            if (usedInstructions->left > 0) usageError(tokens);
            c = inst.right;
            trackInstruction(&(usedInstructions->right), param);
            
        } else if (!strcmp(cmd, instList.rollL)) {
            if (usedInstructions->rollR > 0) usageError(tokens);
            c = inst.rollL;
            trackInstruction(&(usedInstructions->rollL), param);
            
        } else if (!strcmp(cmd, instList.rollR)) {
            if (usedInstructions->rollL > 0) usageError(tokens);
            c = inst.rollR;
            trackInstruction(&(usedInstructions->rollR), param);
            
        } else if (!strcmp(cmd, instList.descend)) {
            if (usedInstructions->ascend > 0) usageError(tokens);
            c = inst.descend;
            trackInstruction(&(usedInstructions->descend), param);
            
        } else if (!strcmp(cmd, instList.wait)) {
            c = inst.wait;
            
        } else if (!strcmp(cmd, instList.waitMili)) {
            c = inst.waitMili;
            
        } else if (!strcmp(cmd, instList.setMode)) {
            if (!strcmp(tokens[1], "intensity")) mode = intensity;
            else if (!strcmp(tokens[1], "distance")) mode = distance;
            else printf("\nError: Unknown mode. Accepted modes are: 'intensity' and 'distance'. \nExiting...\n\n");
            c = inst.setMode;

        } else {
            printf("\nINVALID COMMAND found: %s \n", cmd );
            exit(1);
        }
        
        // Ignore if the parameter is zero
		if (tokens[1] != 0) addToByteArray(c);
        
        int curCmdWait = !strcmp(cmd, instList.wait) || !strcmp(cmd, instList.waitMili);
        int curCmdSetMode = !strcmp(cmd, instList.setMode);
        
        // --------------- Parameters ------------------------------------------------
        
        // Parameter interpretation
        // Interpretation of commands:
        // Wait(n) - n is in seconds, limited to a single unsigned byte hence 255 seconds
        // WaitMili(n) - n is in miliseconds. The parameter has to be split up accordingly into bytes
        // If the current mode is set to 'distance', then each command must be split accordingly into bytes
		// If the current mode is set to 'intensity' then every non-wait command is expected to receive a percentage or an intensity level as a parameter
        if (curCmdSetMode) {
            // intensity -> 1, distance -> 2
            param = (mode == intensity) ? 1 : 2;
			addToByteArray(param);

        } else if (curCmdWait || mode == distance) {

            int i;
            param = atoi(tokens[1]);
           
            //if (mode == distance && ) {
            //    printf ("Current mode is set to DISTANCE. Only integer parameters are allowed.\n Use SetMode(intensity) to switch modes.\nExiting...\n\n");
            //    exit(0);
            //}
            
            if (param <= 255) {
				addToByteArray(param);

			} else {
                // Split up the parameter into chunks of 255 bits
                int rep = param / 255;
                int remainder = param - (rep * 255);
                if (rep) {
					addToByteArray((byte)255);
                    for (i = 1; i < rep; i++) {
                        addToByteArray(c);
                        addToByteArray((byte)255);
                    }
                }
                if (remainder) {
                	addToByteArray(c);
                	addToByteArray((byte)remainder);
                }
            }
            
        } else {
            // If the mode is set to intensity, we are expecting a float between 0 and 1.
            param = PERCENT_TO_INT(tokens[1]);
            
            if (param > 100) {
                printf("\nERROR on: %s %d", cmd, param);
                percentageError();
            }
            addToByteArray((byte)param);
        }
    }
    return 0;
}

/**
 *  Reads a file containing a subset of flail commands and interprets them.
 *  To make sure that each command is separated by a ';', each line is first tokenized by using
 *  ';' as a delimiter, each element found within the resulting token array is then tokenized by using
 *  ' ,(,)' [space, (, and )] as delimiters.
 *
 *  @param script - name of the script file.
 */
int parseScript(const char* script) {
    FILE *fp;
    int i;
    size_t nt; // number of tokens separated by ';'
    size_t ntInst; // number of tokens within the tokens array separated by ' ', '(', or ')'
    char buf[256]; // lines limited to 256B
    char **tokens = NULL;
    char	**tokensInst = NULL;
    
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
            
            // First split the lines by ';'
            char delim[] = ";";
            tokens = strsplit (buf, delim, &nt);
            
#ifdef __DEBUG__
            //findComment (tokens, &nt);
            fprintf (stderr, "\nnumber of tokens = %lu\n", nt);
            
            for (i = 0; i < nt; ++i) {
                fprintf (stderr, "token %d: %s\n", i, tokens[i]);
            }
#endif
            
            if (nt) {
                int i;
                for (i = 0; i < nt; i++) {
                    char delimInst[] =  " ,(,),\t";
                    tokensInst = strsplit(tokens[i], delimInst, &ntInst);
                    
                    if (ntInst == 0) {
                        tokenizationError();
                    }
                    
                    findComment (tokensInst, &ntInst); // Ignore comments
                    
                    interpretTokens (tokensInst, ntInst);
                    
                    if (tokensInst) {
                        freeTokens(tokensInst, ntInst);
                        tokensInst = NULL;
                    }
                }
            }
            
            // If the tokens array was successfully allocated, free every element
            if (tokens) {
                freeTokens(tokens,nt);
                tokens = NULL;
            }
        }
        
        if (inRepeatLoop) {
            printf ("Warning: Unclosed loop. At least one of the 'Repeat' commands was not closed with a '}'. \nPlease check your work.\n\n");
            exit(0);
        }
        
        // attempts to resize the memory block pointed to by bytes
        // that was previously allocated with a call to malloc or calloc.
        bytes = realloc(bytes, (bytes_used + 1) * sizeof(byte));
        bytes[bytes_used] = '\0'; // lets put a (char *)0 to mark the end of the array
        
        free(loopBytes);
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
    fprintf(fp, "typedef unsigned char byte; \n\n");
    fprintf(fp, "typedef struct { \n\
            \tbyte ascend; \n\
            \tbyte forward; \n\
            \tbyte backward; \n\
            \tbyte left; \n\
            \tbyte right; \n\
            \tbyte rollL; \n\
            \tbyte rollR; \n\
            \tbyte descend; \n\
            \tbyte wait; \n\
            \tbyte waitMili; \n\
            \tbyte setMode; \n\
            } Instructions; \n\n\
            // Association of specific bytes to instructions \n\
            const Instructions inst = {\n\
            \t.ascend = 0x%x,\n\
            \t.forward = 0x%x, \n\
            \t.backward = 0x%x, \n\
            \t.left = 0x%x, \n\
            \t.right = 0x%x, \n\
            \t.rollL = 0x%x, \n\
            \t.rollR = 0x%x, \n\
            \t.descend = 0x%x, \n\
            \t.wait = 0x%x, \n\
            \t.waitMili = 0x%x, \n\
            \t.setMode = 0x%x \n\
            \t};\n\n", inst.ascend, inst.forward, inst.backward, inst.left, inst.right, inst.rollL, inst.rollR, inst.descend, inst.wait, inst.waitMili, inst.setMode);
    
    fprintf(fp, "size_t size = %lu; \n\n", bytes_used + 1);
    
    int i;
    if (bytes_used > 0) {
        fprintf(fp, "byte bytes[%lu] = {", bytes_used + 1); // make enough space for '\0' at the end
        for (i = 0 ; i < bytes_used; i++) {
            fprintf(fp, "0x%x, ", bytes[i]);
        }
        fprintf(fp, "'\\0'};\n");
    } else {
        printf ("\nEmpty bytes array. Check your input file.\n\n");
        exit(0);
    }
    
    fprintf(fp, "void interpretBytes() { \n \
            \tint i; \n\
            \tint param;\n\n \
            \tfor (i = 0; i < size - 1; i += 2) { \n\
            \t\tparam = (int)bytes[i+1];\n \
            \t\tswitch(bytes[i]) { \n \
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"Ascend (%%d)\\n\", param); \n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"Forward (%%d)\\n\", param); \n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"Backwards (%%d)\\n\", param); \n\
            \t\t\t\tbreak; \n\n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"Left (%%d)\\n\", param); \n\
            \t\t\t\tbreak; \n\n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"Right (%%d)\\n\", param); \n\
            \t\t\t\tbreak; \n\n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"RollL (%%d)\\n\", param); \n\
            \t\t\t\tbreak; \n\n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"RollR (%%d)\\n\", param); \n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"Descend (%%d)\\n\", param); \n\
            \t\t\t\tbreak; \n\n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"Wait (%%d)\\n\", param); \n\
            \t\t\t\tbreak; \n\n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"WaitMili (%%d)\\n\", param); \n\
            \t\t\t\tbreak; \n\n\
            \t\t\tcase 0x%x: \n\
            \t\t\t\tprintf(\"SetMode(%%d)\\n\", param); \n\
            \t\t\t\tbreak; \n\n\
            \t\t\tdefault: \n\
            \t\t\t\tbreak; \n\
            \t\t} \n\
            \t} \n\
            } \n\n\
            int main() { \n\
            \tinterpretBytes(); \n\
            }", inst.ascend, inst.forward, inst.backward, inst.left, inst.right, inst.rollL, inst.rollR, inst.descend, inst.wait, inst.waitMili, inst.setMode);
}

// Create the byte array text used in the unity simulation
void createByteArrText() {
    char* simByteArray = "byteArray.txt";
    // Remove any pre-existent copy of boilerplate.c before writing to the file.
    remove(simByteArray);
    
    FILE *fp = fopen(simByteArray, "ab+");
    int i;
    if (bytes_used > 0) {
        fprintf(fp, "0x%x", bytes[0]);
        for (i = 1 ; i < bytes_used; i++) {
            fprintf(fp, " 0x%x", bytes[i]);
        }
    }
}

void initUsedInst() {
    usedInstructions ->  ascend = 0;
    usedInstructions ->  descend = 0;
    usedInstructions ->  forward = 0;
    usedInstructions ->  backward = 0;
    usedInstructions ->  left = 0;
    usedInstructions ->  right = 0;
    usedInstructions ->  rollL = 0;
    usedInstructions ->  rollR = 0;
}

int main(int argc, char* argv[]) {
    
    if (argc < 2) {
        printf ("\nFlail: No file was given.\n\n");
        exit(1);
    }
    
    mode = intensity;
    usedInstructions = malloc (sizeof (UsedInstructions));
    initUsedInst();
    
    bytes = calloc(bytes_alloc, sizeof(byte));
    loopBytes = calloc(loopB_alloc, sizeof(byte));
    
    char filename[256];
    
    // to prevent trash from appearing in "filename", fill it with '0's
    memset(filename, '\0', sizeof(filename));
    
    // save the first argument passed on the command line to "filename"
    // Strncpy - warning - if there are no null byte among the first n bytes of the src, the string placed
    // in dest will not be null-terminated.
    strncpy (filename, argv[1], sizeof(filename)-1);
    
    parseScript (filename);
    free(usedInstructions);
    
    printByteArr(bytes, bytes_used);
    
    createBoilerplate();
    createByteArrText();
    
    free(bytes);
}
