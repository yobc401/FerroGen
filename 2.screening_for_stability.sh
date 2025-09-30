#!/bin/sh

mkdir 3.cif 3-1.cif 3-2.cif 4.cif

## Filter polar space group
python run_oxidation_state.py result_polar_group.txt > result_oxidation_state.txt

## Run SevenNet-0
python run_sevennet.py 3.cif/ 3-1.cif/
# double-check whether it is in polar group or not
python run_findsym.py 3-1.cif/ 3-2.cif/  
bash print_space_group.sh 3-2.cif > result_space_group_after_relax.txt
python run_polar_group_after_relax.py result_space_group_after_relax.txt > result_polar_group_after_relax.txt
rm -rf 3-1.cif 3-2.cif


