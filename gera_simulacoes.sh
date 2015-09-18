#!/bin/bash

# Parametros
# $1 100
# $2 3000
# $3 [0, 1, 2]
# $4 400

for ((i=$1; i<=$2; i+= 100));
do

 for ((j=0; j<3; j++));
 do
  ./modelo.py $3 $4 $j 1.0 $i
 done

 for j in 0.3 0.4 0.5 0.6 0.7 0.8 0.9;
 do
  ./modelo.py $3 $4 1 $j $i
 done

done
