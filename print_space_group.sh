#!/bin/bash

folder=$1

if [ ! -d "$folder" ]; then
    echo "Folder '$folder'is not exist."
    exit 1
fi

for cif_file in "$folder"/*.cif; do
    if [ ! -f "$cif_file" ]; then
        echo "No cif file in '$folder'."
        exit 1
    fi

    #echo "Filename: $cif_file"
    space_group=$(grep "_symmetry_Int_Tables_number" "$cif_file" | awk '{print $2}' | tr -d '"')
    #space_group=$(grep "_symmetry_space_group_name_H-M" "$cif_file" | awk '{print $2$3}' | tr -d '"')

    temp_file=$(mktemp)

    # _atom_site_occupancy
    grep -A 100 "_atom_site_fract_symmform" "$cif_file" | awk '!/_atom_site_fract_x/ {print $2}' | tail -n +2 | head -n -2 | sort | uniq -c | awk '{print $2, $1}' > "$temp_file"

    total_atoms=0
    formula=""
    while read -r line; do
        element=$(echo "$line" | awk '{print $1}')
        count=$(echo "$line" | awk '{print $2}')
        #echo "$element: $count"
        total_atoms=$((total_atoms + count))
        formula+="$element$count"
    done < "$temp_file"

    echo "filename: $cif_file formula: $formula number of atoms: $total_atoms space group: $space_group"

    rm "$temp_file"
done
