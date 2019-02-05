#!/usr/bin/python
"""
Sourmash is releasing its 2.0 version and the old signatures are no more supported.
Here we recreate the signatures with sourmash 2.0 to a different folder
"""

# IMPORT
from MySQLdb import Connect
import pandas as pd
import os
from os.path import join

# VARIABLES
sourmash_dir = "/home/linproject/Workspace/Sourmash2.0/all_sketches/"
rep_bac_dir = "/home/linproject/Workspace/Sourmash2.0/rep_bac/"
sourmash_tmp = "/home/linproject/Workspace/Sourmash2.0/tmp_2/"
sourmash_result = "/home/linproject/Workspace/Sourmash2.0/result/"

# FUNCTIONS
def connect_to_db():
    conn = Connect("127.0.0.1", "LINbase","Latham@537")
    c = conn.cursor()
    c.execute("use LINdb_NCBI_RefSeq_test")
    return conn, c

def fetch_genomes(c):
    c.execute("SELECT LIN.Genome_ID, LIN.LIN,Genome.FilePath FROM Genome,LIN WHERE Genome.Genome_ID=LIN.Genome_ID and LIN.Scheme_ID=4")
    tmp = c.fetchall()
    Genome_ID = [int(i[0]) for i in tmp]
    LIN = [i[1] for i in tmp]
    FilePath = [i[2] for i in tmp]
    df = pd.DataFrame()
    df["LIN"] = LIN
    df["FilePath"] = FilePath
    df.index = Genome_ID
    return df

def recompute_signatures(df):
    def get_LINgroup(genome_id):
        lin = df.loc[genome_id,'LIN']
        lingroup = ",".join(lin.split(",")[:6])
        return lingroup
    def compute_single_signature(genome_id,folder):
        cmd = "sourmash compute {0} -k 21,31,51 -n 1000 -o {1} > /dev/null 2>&1".format(df.loc[genome_id,"FilePath"], join(folder,str(genome_id)+".sig"))
        os.system(cmd)
    total = len(df.index)
    current = 1
    for genome_id in df.index:
        print("Processing {0} out of {1} genomes".format(current,total))
        lingroup = get_LINgroup(genome_id)
        lingroup_folder = join(sourmash_dir, lingroup)
        if not os.path.isdir(lingroup_folder):
            os.mkdir(lingroup_folder)
            compute_single_signature(genome_id,rep_bac_dir)
        compute_single_signature(genome_id, lingroup_folder)
        current += 1

# MAIN
if __name__ == '__main__':
    conn, c = connect_to_db()
    df = fetch_genomes(c)
    recompute_signatures(df)