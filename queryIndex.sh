#!/bin/bash

# This example assumes that you code in Python
if [ ! -f searchio.so ];
then
	echo
	echo "*** WARNING: PLEASE MAKE FIRST ***"
	echo "Our project includes a C module that must be compiled."
	echo "Run \"make\" before trying to use this script."
	echo
	exit
fi

# want to use provided btrees
export PYTHONPATH=/course/cs158/src/lib/btrees/py26:$PYTHONPATH

# Main program to be executed
MAIN="queryIndex.py"

# Call $MAIN and pass all the script arguments
python2.6 $MAIN $@

