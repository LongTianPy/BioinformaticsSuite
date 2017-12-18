#!/usr/bin/python
"""
"""

# IMPORT
from MySQLdb import Connect
import os
from os.path import isdir,isfile,join
import shutil
from Bio import SeqIO
from os import listdir
import sys


# FUNCTIONS
def connect_to_db():
    conn = Connect("localhost", "root")
    c = conn.cursor()
    c.execute("use LINdb_NCBI_RefSeq")
    return conn, c

def create_db_by_LIN(LIN,c):
    c.execute("select Genome.Genome_ID, Genome.FilePath from LIN,Genome WHERE Genome.Genome_ID=LIN.Genome_ID AND "
              "LIN LIKE '50,1,0,0,0,0,0,0,0,3%'")
    tmp = c.fetchall()
    Genome_ID = [str(i[0]) for i in tmp]
    FilePath = [i[1] for i in tmp]
    if not isdir("genomes"):
        os.mkdir("genomes")
    f = open("genomes/blastdb.fasta", "w")
    for i in range(len(Genome_ID)):
        f.write(">{0}\n".format(Genome_ID[i]))
        # shutil.copy(FilePath[i],"genomes/" + Genome_ID[i] + ".fasta")
        genome_handler = open(FilePath[i],"r")
        records = list(SeqIO.parse(genome_handler,"fasta"))
        genome_handler.close()
        for record in records:
            f.write(str(record.seq))
        f.write("\n")
    f.close()
    cmd = "mkblastdb -in genomes/blastdb.fasta -dbtype nucl -hash_index -out genomes/blastdb"
    os.system(cmd)

def run_blast(input_folder):
    inputs = [file for file in listdir(input_folder) if isfile(join(input_folder,file))]
    if not isdir("blast_out"):
        os.mkdir("blast_out")
    for input in inputs:
        cmd = "blastn -db genomes/blastdb -query {1} -num_threads 4 -outfmt 6 > {1}".format_map(join(input_folder,input)
                                                                                                ,join("blast_out",input))
        os.system(cmd)






# MAIN
if __name__ == '__main__':
    input_folder = sys.argv[1]
    LIN = sys.argv[2]