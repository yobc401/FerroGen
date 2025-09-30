import sys

import subprocess,glob,os

# Set this path to where your CIFs are. You can also set the variable to os.getcwd()+'/' to automatically set the path to the current working directory

#DIR = '/folder/path/for/CIFs/' #(os.getcwd()+'/')
DIR = sys.argv[1]

DIR_result = sys.argv[2]
# Change the tolerance according to your needs


def genrelaxed(material):

   # Set the input file name and path

   input_file_name = str(material)+'.cif'

   input_file = DIR+input_file_name
   output_file = DIR_result+input_file_name

   # Run findsym_cifinput as an external command. This generates a FINDSYM input (called tempfile) from a non-symmetrized CIF file.

   command_cifinput = 'python gen_relaxed_structure.py  '+input_file+' '+output_file

   subprocess.run(command_cifinput,shell=True)
   subprocess.run('sleep 30',shell=True)



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
   genrelaxed(material)
