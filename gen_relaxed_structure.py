import sys

from sevenn.calculator import SevenNetCalculator
from ase.io import read, write
from ase.constraints import FixSymmetry
from ase.filters import ExpCellFilter
from ase.optimize import BFGS

# Create SevenNetCalculator (using multi-fidelity model)
calc_0 = SevenNetCalculator(model='7net-0')

# Read structure from CIF file
file_input = sys.argv[1]
file_output = sys.argv[2] 

atoms = read(file_input)
constraint = FixSymmetry(atoms.copy())
atoms.set_constraint(constraint)

# Assign calculator
atoms.calc = calc_0

# Lattice optimization
ecf = ExpCellFilter(atoms)

optimizer = BFGS(ecf, logfile='relax.log', trajectory='relax.traj')

fmax = 0.05

optimizer.fmax = fmax  # ⭐️ explicitly set fmax value

max_steps = 1000  # set maximum steps to avoid overly long runs
for step in range(max_steps):
    optimizer.step()

    forces = atoms.get_forces()
    max_force = (forces**2).sum(axis=1).max()**0.5
    #print(max_force)
    if max_force < fmax:
        print(f"Converged at step {step}")
        break

# Save optimized structure as CIF file
write(file_output, atoms)

