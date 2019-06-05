//
//  interpreter.h
//  
//
//  Created by Flavia Cavalcanti on 8/25/18.
//
//

// If interpreter.h exists, define it
#ifndef interpreter_h
#define interpreter_h
#endif /* interpreter_h */

typedef int bool;
#define true 1
#define false 0

enum mode {distance, intensity};

typedef unsigned char byte;

// List of instruction bytes
typedef struct {
	byte ascend;
	byte forward;
	byte backward;
	byte left;
	byte right;
	byte rollL;
	byte rollR;
	byte descend;
	byte wait;
	byte waitMili;
    byte setMode;
	byte repeatNextInstFor;
} Instructions;

// List of instruction names - used to associate correct spelling for instructions
typedef struct {
    char* ascend;
    char* forward;
    char* backward;
    char* left;
    char* right;
    char* rollL;
    char* rollR;
    char* descend;
    char* wait;
    char* waitMili;
    char* setMode;
    char* repeat;
} InstructionList;

// List of previously called instructions
// This struct keeps track of how many times an instruction has been called
// This struct is used to prevent conflicting instructions (e.g. left and right) from being
// called at the same time.
typedef struct {
	int ascend;
	int descend;
	int forward;
	int backward;
	int left;
	int right;
	int rollL;
	int rollR;
} UsedInstructions;


// Association of specific bytes to instructions
const Instructions inst = {
	.ascend   = 0x1,
	.forward  = 0x2,
	.backward = 0x3,
	.left     = 0x4,
	.right    = 0x5,
	.rollL    = 0x6,
	.rollR    = 0x7,
	.descend  = 0x8,
	.wait     = 0x9,
	.waitMili = 0xA,
    .setMode = 0xB,
	.repeatNextInstFor = 0xC
};

// Association of specific instructions to their correct spelling
const InstructionList instList = {
    .ascend   = "Ascend",
    .forward  = "Forward",
    .backward = "Backward",
    .left     = "Left",
    .right    = "Right",
    .rollL    = "RollLeft",
    .rollR    = "RollRight",
    .descend  = "Descend",
    .wait     = "Wait",
    .waitMili = "WaitMili",
    .setMode  = "SetMode",
    .repeat   = "Repeat"
};


