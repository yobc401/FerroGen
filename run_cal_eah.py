import os
import sys
import pandas as pd
from pymatgen.core import Structure, Composition
from pymatgen.entries.computed_entries import ComputedEntry  # use ComputedEntry instead of ComputedStructureEntry
from pymatgen.entries.compatibility import MaterialsProject2020Compatibility
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDEntry
from pymatgen.ext.matproj import MPRester
from pymatgen.io.vasp.sets import MPRelaxSet

# ======== User input (modify only these four) ========
API_KEY = 'YOUR_API_KEY'  ##### COPY KEY
TARGET_DIR    = sys.argv[1]                  # folder containing structure files
CSV_FILE      = "total_energy_list.csv"      # input CSV (formula/energy etc.)
NAME_COLUMN   = "cif_file"                   # structure file name (extension optional) - displayed as formula in output
ENERGY_COLUMN = "total_energy"               # total energy [eV]
# =====================================================

def load_structure(base_dir: str, name: str) -> Structure:
    """
    If 'name' contains an extension, read it directly.
    Otherwise, try in order: .cif, POSCAR, CONTCAR.
    """
    candidates = []
    p = os.path.join(base_dir, name)
    if os.path.isfile(p):
        candidates.append(p)
    else:
        # If only a 'formula' without extension is provided, try in the following order
        for ext in (".cif", "POSCAR", "CONTCAR"):
            candidates.append(os.path.join(base_dir, name + ("" if ext in ("POSCAR", "CONTCAR") else ext)))
            if ext in ("POSCAR", "CONTCAR"):
                candidates.append(os.path.join(base_dir, ext))
    for path in candidates:
        if os.path.isfile(path):
            return Structure.from_file(path)
    raise FileNotFoundError(f"[load_structure] Not found: {name} (searched in {base_dir})")

# Read input CSV
df_in = pd.read_csv(os.path.join('./', CSV_FILE))
names   = df_in[NAME_COLUMN].tolist()
energies= df_in[ENERGY_COLUMN].astype(float).tolist()

compat = MaterialsProject2020Compatibility()
chemsys_cache = {}  # cache: chemsys(str) -> mp_entries
ehull_list = []     # list to save NAME_COLUMN value and Ehull

with MPRester(API_KEY) as mpr:
    for name, E_tot in zip(names, energies):
        try:
            # 1) Load structure
            structure = load_structure(TARGET_DIR, name)
            comp      = structure.composition
            chemsys   = Composition(structure.formula).chemical_system

            # 2) Auto-detect LDAU/POTCAR settings from MP (MPRelaxSet)
            mp_set = MPRelaxSet(structure)
            incar  = mp_set.incar
            ldauu  = incar.get("LDAUU", [])
            elems  = [sp.symbol for sp in comp.elements]
            hubbards = {el: float(U) for el, U in zip(elems, ldauu) if float(U) > 0}
            is_hubbard = bool(hubbards)
            run_type   = "GGA+U" if is_hubbard else "GGA"
            potcar_symbols = [f"PBE {lbl}" for lbl in mp_set.potcar_symbols]

            # 3) Create own entry
            params = {
                "run_type": run_type,
                "is_hubbard": is_hubbard,
                "hubbards": hubbards,
                "potcar_symbols": potcar_symbols,
                "pseudo_potential": {
                    "functional": "PBE",
                    "labels": [s.split()[1] for s in potcar_symbols],
                    "pot_type": "paw",
                },
            }
            my_raw = ComputedEntry(Composition(structure.formula), E_tot, parameters=params)

            # 4) Attempt correction
            processed = compat.process_entries([my_raw], clean=True, on_error="warn")
            my_for_pd = processed[0] if processed else PDEntry(Composition(structure.formula), E_tot)

            # 5) Cache MP entries
            if chemsys not in chemsys_cache:
                chemsys_cache[chemsys] = mpr.get_entries_in_chemsys(
                    chemsys.split("-"), compatible_only=True
                )
            mp_entries = chemsys_cache[chemsys]

            # 6) Compute Ehull
            phase = PhaseDiagram(mp_entries)
            e_above_hull = phase.get_e_above_hull(my_for_pd, allow_negative=True)

            # Print result (NAME_COLUMN + Ehull)
            print(f"{name:30s} -> Ehull = {e_above_hull:.6f} eV/atom")

            # Append to CSV list (NAME_COLUMN + Ehull)
            ehull_list.append({
                NAME_COLUMN: name,
                " Ehull_eV_per_atom": " "+str(e_above_hull)
            })

        except Exception as e:
            print(f"{name:30s} -> FAILED: {e}")
            ehull_list.append({
                NAME_COLUMN: name,
                " Ehull_eV_per_atom": " "+str(float('nan'))
            })

# 7) Save results: both NAME_COLUMN and Ehull
out_path = os.path.join("ehull_output_final.csv")
pd.DataFrame(ehull_list).to_csv(out_path, index=False)
print(f"[DONE] Saved {NAME_COLUMN} & hull energies to: {out_path}")

