#!/usr/bin/env python3
import sys
import csv
import subprocess
import pandas as pd
from ase.spacegroup import Spacegroup

# -------------------------
# Polar space group helpers
# -------------------------
def format_spacegroup_name(name: str) -> str:
    # e.g., "P6_3mc" -> "P63mc"
    return name.replace('_1', '1').replace('_2', '2').replace('_3', '3')

def get_spacegroup_number(name: str):
    try:
        sg = Spacegroup(format_spacegroup_name(name))
        return int(sg.no)
    except Exception:
        return None

def load_polar_group_numbers(polar_csv_path: str = 'polar_spg.csv') -> set:
    """Load polar space group numbers from CSV."""
    df = pd.read_csv(polar_csv_path)
    if 'polar_spg' not in df.columns:
        raise ValueError("polar_spg.csv must contain 'polar_spg' column.")
    numbers = set()
    for name in df['polar_spg'].dropna().astype(str):
        n = get_spacegroup_number(name)
        if n is not None:
            numbers.add(n)
    # Exclude P1 (space group 1)
    numbers.discard(1)
    return numbers

# -------------------------
# Main filtering: polar groups only
# -------------------------
def extract_polar_only(file_path: str, delimiter: str = ' '):
    """
    Extract only entries whose space group belongs to the polar set.
    Returns: (total_rows, matched_rows, records_dict)
    """
    polar_numbers = load_polar_group_numbers('polar_spg.csv')

    file_data_polar = {}
    total_rows = 0
    matched_rows = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                if not row:
                    continue

                if len(row) < 11:
                    continue  # Skip incomplete rows

                total_rows += 1
                filename = row[1].strip()
                formula = row[3].strip()
                num_atoms = row[7].strip()

                try:
                    sg = int(str(row[10]).strip())
                except ValueError:
                    continue

                if sg in polar_numbers:
                    matched_rows += 1
                    file_data_polar[filename] = {
                        'filename': filename,
                        'formula': formula,
                        'num_of_atoms': num_atoms,
                        'space_group': sg
                    }
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error while reading {file_path}: {e}")
        sys.exit(1)

    return total_rows, matched_rows, file_data_polar

def print_and_copy_polar(file_data_polar: dict, total_rows: int, matched_rows: int):
    print("\n===== Polar Group Filter Result =====")
    if total_rows > 0:
        rate = (matched_rows / total_rows) * 100.0
        print(f"Matching rate (polar only): {rate:.2f}% ({matched_rows}/{total_rows})")

    for filename, rec in file_data_polar.items():
        # Copy file with new name: prepend '2' to filename
        src_file = '3-2'+filename[1:-4]+'_sym.cif'
        dest_file = '4' + filename[1:] if len(filename) >= 1 else '4' + filename
        command = f'cp "{src_file}" "{dest_file}"'
        subprocess.run(command, shell=True)
        print(
            f"filename: {dest_file}  "
            f"formula: {rec['formula']}  "
            f"num_atoms: {rec['num_of_atoms']}  "
            f"space_group: {rec['space_group']}"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_polar_group.py <input_file_path> [delimiter]")
        sys.exit(1)

    file_path = sys.argv[1]
    delimiter = sys.argv[2] if len(sys.argv) >= 3 else ' '

    total, matched, polar_records = extract_polar_only(file_path, delimiter=delimiter)
    print_and_copy_polar(polar_records, total, matched)

