#!/usr/bin/env bash 

echo "Compiling flail.c" 
make

if [ "$1" == "" ]; then
	echo "Error: No flail file was given to script. Exiting..."
	exit 1
fi

./flail $1

echo "Compiling boilerplate.c" 
gcc -o boilerplate boilerplate.c 
