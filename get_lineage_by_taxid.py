#!/usr/bin/python
"""Getting full taxonomy lineage by taxonomy id provided.
"""

# IMPORT
import pandas as pd
from Bio import Entrez
import sys
Entrez.email = "aaa@bbb.com"

# FUNCTIONS
def get_lineage(metadata_file):
    df = pd.read_table(metadata_file,header=0)
    lineage_dict = {'superkingdom':[],'phylum':[],'class':[],'order':[],'family':[],'genus':[],'species':[],'subspecies':[]}
    for i in df.index:
        taxid = df.get_value(i,"Tax_ID")
        if taxid == "N/A":
            lineage_dict['superkingdom'].append("N/A")
            lineage_dict['phylum'].append("N/A")
            lineage_dict['class'].append('N/A')
            lineage_dict['order'].append('N/A')
            lineage_dict['family'].append('N/A')
            lineage_dict['genus'].append('N/A')
            lineage_dict['species'].append('N/A')
            lineage_dict['subspecies'].append('N/A')
        else:
            handle = Entrez.efetch(db="taxonomy", id=str(taxid), rettype="xml")
            record = Entrez.read(handle)[0]
            lineage = record["LineageEx"]
            for i in lineage:
                if i["Rank"] in lineage_dict:
                    lineage_dict[i["Rank"]].append(i["ScientificName"])
                    if lineage[-2]["Rank"] == "species":
                        lineage_dict["subspecies"].append(i["ScientificName"])
                    else:
                        lineage_dict["subspecies"].append("N/A")
    for i in lineage_dict.keys():
        df[i] = lineage_dict[i]
    df.to_csv("metadata_w_lineage.csv")







# MAIN
if __name__ == '__main__':
    metadata_file = sys.argv[1]
    get_lineage(metadata_file)