#!/usr/bin/python
"""
"""

# IMPORT
from Bio import SeqIO
from collections import OrderedDict
import sys
from os import listdir
from os.path import isfile

# FUNCTIONS
def check_duplication(file):
    with open(file,"r") as f:
        records = list(SeqIO.parse(f,"fasta"))
    pool = OrderedDict()
    for record in records:
        if record.seq not in pool:
            pool[record.seq] = [record.id]
        else:
            pool[record.seq].append(record.id)
    with open(file+'.nonredundant.fasta',"w") as f:
        for i in pool.keys():
            ids = pool[i]
            ids_string = "\n=".join(ids)
            f.write(">"+ids_string)
            f.write("\n")
            f.write(str(i))
            f.write('\n')

# MAIN
if __name__ == '__main__':
    input = sys.argv[1]
    files = [file for file in listdir(input) if isfile(file)]
    for file in files:
        check_duplication(file)