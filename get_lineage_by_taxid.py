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
    df = pd.read_csv(metadata_file,header=0)
    lineage_dict = {'superkingdom':["N/A"]*len(df.index),'phylum':["N/A"]*len(df.index),'class':["N/A"]*len(df.index),
                    'order':["N/A"]*len(df.index),'family':["N/A"]*len(df.index),'genus':["N/A"]*len(df.index),
                    'species':["N/A"]*len(df.index),'subspecies':["N/A"]*len(df.index),'full_lineage':["N/A"]*len(df.index)}
    for i in lineage_dict.keys():
        df[i] = lineage_dict[i]
    for i in df.index:
        try:
            taxid = int(df.loc[i,"Tax_ID"])
        except:
            taxid = "N/A"
        if taxid == "N/A":
            continue
        else:
            print(taxid)
            handle = Entrez.efetch(db="taxonomy", id=str(taxid), rettype="xml")
            record = Entrez.read(handle)[0]
            lineage = record["LineageEx"]
            for i in lineage:
                if i["Rank"] in lineage_dict:
                    # lineage_dict[i["Rank"]].append(i["ScientificName"])
                    df.loc[i,i["Rank"]] = i["ScientificName"]
                    if lineage[-2]["Rank"] == "species":
                        #lineage_dict["subspecies"].append(i["ScientificName"])
                        df.loc[i,"subspecies"] = i["ScientificName"]
            complete_name = ";".join(["{0}={1}".format(i["Rank"],i["ScientificName"]) for i in lineage[1:]])
            df.loc[i,"full_lineage"] = complete_name
    df.to_csv("metadata_w_lineage.csv")







# MAIN
if __name__ == '__main__':
    metadata_file = sys.argv[1]
    get_lineage(metadata_file)