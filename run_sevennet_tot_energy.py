import numpy as np
from ase.io import read
from sevenn.calculator import SevenNetCalculator
import sys
import os
import pandas as pd


def calculate_energy_from_cif(cif_file_path, model_path=None):
    """
    Read a structure from a CIF file and calculate energy using SevenNet.
    
    Parameters:
    -----------
    cif_file_path : str
        Path to the CIF file
    model_path : str, optional
        Path to the SevenNet model file (if not provided, default model is used)
    
    Returns:
    --------
    dict : energy calculation results
    """
    
    try:
        # Read CIF file
        print(f"Read CIF file: {cif_file_path}")
        atoms = read(cif_file_path)
        print(f"Structure information:")
        print(f"  - Number of atoms: {len(atoms)}")
        print(f"  - Formula: {atoms.get_chemical_formula()}")
        print(f"  - Lattice constant: {atoms.cell.lengths()}")
        
        # Set SevenNet Calculator
        if model_path:
            calc = SevenNetCalculator(model_file=model_path)
        else:
            # Use default SevenNet model
            calc = SevenNetCalculator(model='7net-0')
        
        # Assign calculator to atoms object
        atoms.set_calculator(calc)
        
        # Calculate energy
        print("\nCalculate energy by SevenNet...")
        total_energy = atoms.get_potential_energy()
        forces = atoms.get_forces()
        
        # Energy per atom
        energy_per_atom = total_energy / len(atoms)
        
        # Force magnitudes
        force_magnitudes = np.linalg.norm(forces, axis=1)
        max_force = np.max(force_magnitudes)
        rms_force = np.sqrt(np.mean(force_magnitudes**2))
        
        results = {
            'total_energy': total_energy,
            'energy_per_atom': energy_per_atom,
            'forces': forces,
            'max_force': max_force,
            'rms_force': rms_force,
            'num_atoms': len(atoms),
            'chemical_formula': atoms.get_chemical_formula()
        }
        
        return results
        
    except Exception as e:
        print(f"Error occurs: {str(e)}")
        return None

def print_results(results):
    if results is None:
        print("No result!")
        return
    
    print("\n" + "="*50)
    print("SevenNet Energy Calculation Results")
    print("="*50)
    print(f"Formula: {results['chemical_formula']}")
    print(f"Number of atoms: {results['num_atoms']}")
    print(f"Total energy: {results['total_energy']:.6f} eV")
    print(f"Energy per atom: {results['energy_per_atom']:.6f} eV/atom")
    print(f"Max force: {results['max_force']:.6f} eV/Å")
    print(f"RMS force: {results['rms_force']:.6f} eV/Å")
    print("="*50)


def batch_calculate(cif_directory, model_path=None):
    """
    Batch calculation for multiple CIF files
    
    Parameters:
    -----------
    cif_directory : str
        Directory containing CIF files
    model_path : str, optional
        Path to SevenNet model file
    """
    
    if not os.path.exists(cif_directory):
        print(f"Directory does not exist: {cif_directory}")
        return
    
    cif_files = [f for f in os.listdir(cif_directory) if f.endswith('.cif')]
    
    if not cif_files:
        print(f"No CIF files found in {cif_directory}.")
        return
    
    print(f"Found {len(cif_files)} CIF files.")
    
    all_results = {}
    cif_files_list = []
    total_energy_list = []

    for cif_file in cif_files:
        cif_path = os.path.join(cif_directory, cif_file)
        print(f"\nProcessing: {cif_file}")
        
        results = calculate_energy_from_cif(cif_path, model_path)
        
        if results:
            all_results[cif_file] = results
            print_results(results)
            cif_files_list.append(cif_file)
            total_energy_list.append(results['total_energy'])
 
    
    # Summary of results
    if all_results:
        print(f"\n\nCompleted calculations for {len(all_results)} structures")
        print("Energy summary:")
        for filename, result in all_results.items():
            print(f"{filename:30s}: {result['total_energy']:8.4f} eV")

    return cif_files_list, total_energy_list

def main():
    """Main function"""
    
    # Usage example
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file: python script.py structure.cif [model_path]")
        print("  Batch mode: python script.py directory/ [output_dir/] [model_path]")
        return
    
    input_path = sys.argv[1]
    model_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].endswith('.pth') else None
    
    if os.path.isfile(input_path) and input_path.endswith('.cif'):
        # Single CIF file
        results = calculate_energy_from_cif(input_path, model_path)
        print_results(results)
        
        # Save results
        if results:
            output_file = input_path.replace('.cif', '_energy.txt')
            save_results(results, output_file)
            
    elif os.path.isdir(input_path):
        # Process all CIF files in directory
        output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].endswith('.pth') else None
        cif_files_list, total_energy_list = batch_calculate(input_path, model_path)

        df = pd.DataFrame({
                'cif_file': cif_files_list,
                'total_energy': total_energy_list
        })
 
        df.to_csv('total_energy_list.csv', index=False, encoding='utf-8-sig') 

    else:
        print("Please provide a valid CIF file or directory.")

if __name__ == "__main__":
    main()

