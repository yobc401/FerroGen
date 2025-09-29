# FerroGen

FerroGen is a Bash shell script for sequentially screening diffusion-model–generated inorganic crystal structures to identify promising ferroelectric candidates.
This is a multi-stage filtering pipeline that (1) applies symmetry filtering by polar space groups, (2) checks thermodynamic stability via oxidation state and energy above hull, (3) screens the band gap (a key ferroelectric photovoltaic property) and estimates synthesizability with a machine-learning–based crystal-likeness score. The workflow is orchestrated by a Bash script, while specific stages (e.g., FINDSYM, SevenNet-0, band gap, and etc.) call helper Python scripts where provided. 

# Prerequisites
