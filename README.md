# FerroGen

FerroGen is a Bash shell script for sequentially screening diffusion-model–generated inorganic crystal structures to identify promising ferroelectric candidates.
This is a multi-stage filtering pipeline that (1) applies symmetry filtering by polar space groups, (2) checks thermodynamic stability via oxidation state and energy above hull, (3) screens the band gap (a key ferroelectric photovoltaic property), (4) evaluates double-well potential and polarization, and (5) estimates synthesizability with a machine-learning–based crystal-likeness score.
The workflow is orchestrated by a Bash script, while specific stages (e.g., band gap and synthesizability) call helper Python scripts where provided. This protocol enables efficient down-selection of generated structures toward experimentally viable ferroelectrics for photocurrent applications.
