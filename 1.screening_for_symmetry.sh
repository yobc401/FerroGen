#!/bin/sh

mkdir 1.cif 2.cif

## Run FINDSYM for symmetry
python run_findsym.py generated_materials_cif/ 1.cif/

## Print space group name to "log_space_group.txt"
bash print_space_group.sh 1.cif > result_space_group.txt

## Filter polar space group
python run_polar_group.py result_space_group.txt > result_polar_group.txt



