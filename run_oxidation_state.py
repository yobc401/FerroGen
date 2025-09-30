#!/usr/bin/env python3
import sys
import csv
import subprocess

import oxidation_state


def analyze_neutral_only(file_path: str, delimiter: str = ' '):
    """
    Read rows and keep only entries whose chemical formula is charge-neutral
    according to oxidation_state.OxidationStateAnalyzer.
    Expected columns (by index, same as your original):
        row[1] = filename
        row[3] = formula (a trailing char might exist in your original data)
        row[7] = number of atoms
        row[10] = space group (not used for filtering here)
    Returns: (total_rows, matched_rows, records_dict)
    """
    analyzer = oxidation_state.OxidationStateAnalyzer()

    records = {}
    total_rows = 0
    matched_rows = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                if not row:
                    continue

                if len(row) < 11:
                    # Skip incomplete rows
                    continue

                total_rows += 1
                filename = row[1].strip()
                formula = row[4].strip()
                num_atoms = row[7].strip()
                space_group_raw = row[10].strip()  # kept for output parity
                # Oxidation-state neutrality check
                try:
                    result = analyzer.is_neutral_compound(formula)
                except Exception:
                    # If the analyzer fails for any reason, skip this row
                    continue

                # Handle both bool and (bool, oxidation_states) returns
                if isinstance(result, tuple):
                    is_neutral, oxidation_states = result
                else:
                    is_neutral = bool(result)
                    oxidation_states = None

                if is_neutral:
                    matched_rows += 1
                    records[filename] = {
                        'filename': filename,
                        'formula': formula,
                        'num_of_atoms': num_atoms,
                        'space_group': space_group_raw,
                        'oxidation_states': oxidation_states,
                    }

    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error while reading {file_path}: {e}")
        sys.exit(1)

    return total_rows, matched_rows, records


def print_and_copy_neutral(records: dict, total_rows: int, matched_rows: int):
    print("\n===== Oxidation-State Neutral Filter Result =====")
    if total_rows > 0:
        rate = (matched_rows / total_rows) * 100.0
        print(f"Matching rate (neutral only): {rate:.2f}% ({matched_rows}/{total_rows})")

    for filename, rec in records.items():
        ox_state_str = (
            f"{rec['oxidation_states']}" if rec['oxidation_states'] is not None else "N/A"
        )

        # Keep your original copy rule: prepend '3' to the filename (after the first char)
        src_file = rec['filename']
        dest_file = '3' + src_file[1:] if len(src_file) >= 1 else '3' + src_file
        command = f'cp "{src_file}" "{dest_file}"'
        subprocess.run(command, shell=True)
        print(
            f"filename: {dest_file}  "
            f"formula: {rec['formula']}  "
            f"num_atoms: {rec['num_of_atoms']}  "
            f"space_group: {rec['space_group']}  "
            f"oxidation_states: {ox_state_str}"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_oxidation_state.py <input_file_path> [delimiter]")
        sys.exit(1)

    file_path = sys.argv[1]
    delimiter = sys.argv[2] if len(sys.argv) >= 3 else ' '

    total, matched, neutral_records = analyze_neutral_only(file_path, delimiter=delimiter)
    print_and_copy_neutral(neutral_records, total, matched)

