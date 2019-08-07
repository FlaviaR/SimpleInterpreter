#!/bin/sh

# script for using flailDriver contained in docRose directory.

export PYTHONPATH=docRose:$PYTHONPATH:

python ./interface.py $@
