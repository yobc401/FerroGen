#!/bin/sh

mkdir 5.cif

rm -f id_prop.csv
NUM=1
for file in "4.cif/"*
   do 
   if [ -f "$file" ]; then       
       FILEID=$(printf "%04d" $NUM)
       FILENAME=$(printf "%04d.cif" $NUM)
       echo $FILEID","$NUM".0" >> "5.cif/id_prop.csv"
       cp "$file" "5.cif/$FILENAME"
       ((NUM++))
   fi
    
done

cp atom_init.json 5.cif/

## Calculate band gap using CGCNN
python run_cgcnn.py pre-trained/band-gap.pth.tar 5.cif

## Calculate Energy above hull
python run_sevennet_tot_energy.py 5.cif
python run_cal_eah.py 5.cif

bash print_space_group_band_gap_eah.sh 5.cif > result_final_all.txt
