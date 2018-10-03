//
//  interpreter.h
//  
//
//  Created by Flavia Cavalcanti on 8/25/18.
//
//

#ifndef interpreter_h
#define interpreter_h


#endif /* interpreter_h */

typedef unsigned char byte;

// List of instructions
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
} Instructions;

// List of previously called instructions
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
	.ascend = 0x0,
	.forward = 0x1,
	.backward = 0x2,
	.left = 0x3,
	.right = 0x4,
	.rollL = 0x5,
	.rollR = 0x6,
	.descend = 0x7,
	.wait = 0x8,
	.waitMili = 0x9
};

