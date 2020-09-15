#!/bin/bash
# Arg1: Num Rounds
# Arg2: Num Players

for (( i=1; i<=$1; i++ ))
do
  python Precompute.py "Data/mrp${2}r${i}.json" $i
done
