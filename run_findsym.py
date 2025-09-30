import sys

import subprocess,glob,os

# Set this path to where your CIFs are. You can also set the variable to os.getcwd()+'/' to automatically set the path to the current working directory

#DIR = '/folder/path/for/CIFs/' #(os.getcwd()+'/')
DIR = sys.argv[1]

DIR_result = sys.argv[2]
# Change the tolerance according to your needs

print("DIR:",DIR)
print("DIR_result",DIR_result)

latticeTolerance = 0.1

atomicPositionTolerance = 0.1

atomicPositionMaxTolerance = 0.330E+00

occupationTolerance = 0.100E-02

def findsym(material):

   # Set the path to the FINDSYM executable

   findsym_path = 'iso/'#'/folder/path/isobyu/'

   # Set the input file name and path

   input_file_name = str(material)+'.cif'

   input_file = DIR+input_file_name

   # Run findsym_cifinput as an external command. This generates a FINDSYM input (called tempfile) from a non-symmetrized CIF file.

   command_cifinput = findsym_path+'findsym_cifinput '+input_file+' > tempfile'

   subprocess.run(command_cifinput,shell=True)

   # Change the tolerances in the tempfile to what was specified above

   lines = []

   with open('tempfile') as f:

       for i, line in enumerate(f):
           lines.append(line)

       lines[4] = str(latticeTolerance)+'\n'

       lines[6] = str(atomicPositionTolerance)+'\n'

       lines[8] = str(atomicPositionMaxTolerance)+'\n'

       lines[10] = str(occupationTolerance)+'\n'

   new_tempfile = open('tempfile_new','w+')

   for item in lines:

       new_tempfile.write(item)

   new_tempfile.close()

   # Run findsym to generate the symmetrized CIF

   command_findsym = findsym_path+'findsym tempfile_new'

   subprocess.run(command_findsym,shell=True)

   # Change the default CIF name to <Material>_sym.cif

   change_name = 'mv findsym.cif '+ DIR_result + str(material)+'_sym.cif'

   subprocess.run(change_name,shell=True)



# Iterate over all CIFs in the DIR path
nDIR = len(DIR)

ntype = len(".cif")

pathlist = glob.glob(DIR+'*.cif')

for path in pathlist:
   print(path) 
   path_in_str = str(path)

   material = path_in_str[nDIR:-ntype]

   if material == "":break
   print(material)
   findsym(material)
