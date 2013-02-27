#!/bin/bash

# This example assumes that you code in Python

# want to use provided btrees
#export PYTHONPATH=/course/cs158/src/lib/btrees/py26:$PYTHONPATH
export PYTHONPATH=pybin:$PYTHONPATH # comment out and swap for above export call on department machines
# Main program to be executed
MAIN="queryIndex.py"

# Call $MAIN and pass all the script arguments
python2.6 $MAIN $@

