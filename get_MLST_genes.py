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
    cmd = "makeblastdb -in genomes/blastdb.fasta -dbtype nucl -hash_index -out genomes/blastdb"
    os.system(cmd)

def run_blast(input_folder):
    inputs = [file for file in listdir(input_folder) if isfile(join(input_folder,file))]
    if not isdir("blast_out"):
        os.mkdir("blast_out")
    for input in inputs:
        cmd = "blastn -db genomes/blastdb -query {0} -num_threads 4 -outfmt 6 > {1}".format(join(input_folder,input)
                                                                                                ,join("blast_out",input))
        os.system(cmd)

def get_housekeeping_seqs(input_folder,c):
    db = SeqIO.index("genomes/blastdb.fasta", "fasta")
    blast_outs = [file for file in listdir("blast_out")]
    pool = {blast_out:{} for blast_out in blast_outs}
    for blast_out in blast_outs:
        f = open(join(input_folder,blast_out),"r")
        records = list(SeqIO.parse(f,"fasta"))
        f.close()
        gene_length = len(records[0].seq)
        f = open("blast_out/"+blast_out,"r")
        lines = [i.strip().split("\t") for i in f.readlines()]
        f.close()
        for line in lines:
            if lines[1] not in pool[blast_out].keys():
                if line[3] == gene_length:
                    start = int(line[8])-1
                    end = int(line[9])
                    seq = str(db[str(line[1])].seq)
                    pool[blast_out][str(line[1])] = seq
    union = set(pool[pool.keys()[0]].keys())
    for i in pool.keys():
        union = union & set(pool[i].keys())
    genome_list = list(union)
    print(genome_list)
    if not isdir("house_keeping"):
        os.mkdir("house_keeping")
    for blast_out in blast_outs:
        f = open(join("house_keeping",blast_out),"w")
        for genome in genome_list:
            c.execute("select AttributeValue from AttributeValue where Genome_ID={0} and Attribute_ID in (1,2,4)".format_map(int(genome)))
            tmp = c.fetchall()
            genus = tmp[0][0]
            species = tmp[1][0]
            strain = tmp[2][0]
            f.write(">{0} {1} {2}|{3}\n".format_map(genus,species,strain,genome))
            f.write(pool[blast_out][genome])
            f.write("\n")
        f.close()




# MAIN
if __name__ == '__main__':
    input_folder = sys.argv[1]
    LIN = sys.argv[2]
    conn,c = connect_to_db()
    #create_db_by_LIN(LIN,c)
    #run_blast(input_folder)
    get_housekeeping_seqs(input_folder,c)
