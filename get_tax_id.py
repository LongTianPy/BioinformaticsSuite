#!/usr/bin/python3
"""This script takes the output files (classes.txt and labels.txt) from pyani's genome downloading script.
by using ncbi's eutils's api in python, retrieve taxonomy id, if there is any.
"""

# IMPORT
import eutils.client
import sys
import os
from os import listdir
from os.path import isdir, isfile, join
import pandas as pd

# FUNCTIONS
def search_taxonomy(folder):
    classes_file = join(folder,"classes.txt")
    labels_file = join(folder,"labels.txt")
    handler_classes = open(classes_file,"r")
    classes = [i.strip().split("\t") for i in handler_classes.readlines()]
    handler_classes.close()
    handler_labels = open(labels_file,"r")
    labels = [i.strip().split("\t") for i in handler_labels.readlines()]
    handler_labels.close()
    classes_dict = {i[0]:i[1] for i in classes}
    labels_dict = {i[0]:i[1] for i in labels}
    genomes = labels_dict.keys()
    metadata = pd.DataFrame()
    genera = []
    specieses = []
    strains = []
    organism_names = []
    types=[]
    tax_ids = []
    for genome in genomes:
        genus_species = classes_dict[genome]
        genus_species_list = genus_species.split(" ")
        if "sp." in genus_species_list or "Candidatus" in genus_species_list:
            organism_name = genus_species
            if "sp." in genus_species_list:
                genus = genus_species_list[0]
                species = "sp."
                strain = genus_species_list[-1]
            elif "Candidatus" in genus_species_list:
                genus = "_".join(genus_species_list[:2])
                species = "_".join(genus_species_list[2:])
                label_split = labels_dict[genome].split(" ")
                strain = label_split[-1]
            if "type strain" in labels_dict[genome]:
                type_strain = "Yes"
            else:
                type_strain = "No"
            if strain == species:
                organism_name == organism_name
            else:
                organism_name = organism_name + " " + strain
        else:
            genus = genus_species_list[0]
            species = genus_species_list[1]
            label_split = labels_dict[genome].split(" ")
            strain_split = label_split[len(genus_species_list):]
            strain_whole = " ".join(strain_split)
            if "type" in strain_whole:
                type_strain = "Yes"
                strain = "_".join(strain_split[2:])
            else:
                type_strain = "No"
                strain = "_".join(strain_split)
            organism_name = genus_species + " " + strain
        genera.append(genus)
        specieses.append(species)
        strains.append(strain)
        organism_names.append(organism_name)
        types.append(type_strain)
        term = organism_name
        ec = eutils.client.Client()
        search = ec.esearch(db="taxonomy", term=term)
        try:
            tax_id = search.ids[0]
        except:
            tax_id = "N/A"
        tax_ids.append(tax_id)
    metadata["Genus"]=genera
    metadata["Species"]=specieses
    metadata["Strain"] = strains
    metadata["Tax_ID"] = tax_ids
    metadata["Type_strain"] = types
    metadata["organism_name"] = organism_names
    metadata["File"] = genomes
    metadata.to_csv(join(folder,"metadata.csv"))




# MAIN
if __name__ == '__main__':
    folder = sys.argv[1]
    search_taxonomy(folder)
