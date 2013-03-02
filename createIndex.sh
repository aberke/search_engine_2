#!/bin/bash

# This example assumes that you code in Python

export PYTHONPATH=pybin:$PYTHONPATH # comment out and swap for above export call on department machines
# Main program to be executed
MAIN="createIndex.py"

# Call $MAIN and pass all the script arguments
python $MAIN $@

