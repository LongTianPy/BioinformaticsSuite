#!/usr/bin/python
"""
"""

# IMPORT
from MySQLdb import Connect
import sys
import shutil
import os

tmp_folder = '/home/linproject/Workspace/tmp_upload/'

# FUNCTIONS
def connect_to_db(from_db):
    conn = Connect("localhost", "root")
    c = conn.cursor()
    c.execute("use {0}".format(from_db))
    return conn, c

# MAIN
if __name__ == '__main__':
    from_db = sys.argv[1]
    # to_db = sys.argv[2]
    keyword = sys.argv[2]
    conn,c = connect_to_db(from_db=from_db)
    c.execute("select LIN.Genome_ID,Genome.FilePath,Genome.GenomeName from AttributeValue,Genome,LIN where "
              "AttributeValue.Genome_ID=Genome.Genome_ID and LIN.Genome_ID=Genome.Genome_ID AND "
              "LIN.Scheme_ID=4 AND AttributeValue.AttributeValue='{0}' and Genome.Interest_ID=1".format(keyword))
    tmp = c.fetchall()
    Genome_ID = [int(i[0]) for i in tmp]
    print(Genome_ID)
    FilePath = [i[1] for i in tmp]
    # for i in FilePath:
    #     shutil.copy(i,tmp_folder)
    GenomeName = [i.split("/")[-1] for i in FilePath]
    c.execute("select Attribute_IDs from Interest where Interest_ID=1")
    Attribute_IDs = c.fetchone()[0]
    Attribute_ID_list = Attribute_IDs.split(",")
    c.execute("select AttributeName from Attribute where Attribute_ID in ({0})".format(Attribute_IDs))
    tmp = c.fetchall()
    AttributeNames = [i[0] for i in tmp]
    Attribute_ID_to_Name = {}
    Attribute_ID_to_Value = {}
    Attribute_Name_to_Value = {}
    # for i in range(len(Attribute_ID_list)):
    #     Attribute_ID_to_Name[AttributeNames[i]] = str(Attribute_ID_list[i])
    #     Attribute_ID_to_Value[str(Attribute_ID_list[i])] = []
    for i in Genome_ID:
        c.execute("select Attribute.AttributeName,AttributeValue.AttributeValue from AttributeValue,Attribute where "
                  "Attribute.Attribute_ID=AttributeValue.attribute_ID and AttributeValue.Genome_ID={0}".format(i))
        tmp = c.fetchall()
        for each in tmp:
            if each[0] not in Attribute_Name_to_Value:
                Attribute_Name_to_Value[each[0]] = [str(each[1]).replace(" ","_")]
            else:
                Attribute_Name_to_Value[each[0]].append(str(each[1]).replace(" ","_"))
    print(Attribute_Name_to_Value["Strain"])
    with open("import_db_cmd.txt","w") as f:
        for i in range(len(Genome_ID)):
            attribute_value_list = []
            for each_attributename in AttributeNames:
                try:
                    attribute_value_list.append(Attribute_Name_to_Value[each_attributename][i])
                except:
                    print("index={0}; Genome_ID={1};".format(i,Genome_ID[i]))
                    sys.exit(0)
            attribute_value_list.append("N/A")
            attribute_value = "^^".join(attribute_value_list)
            arguments = "-i {0} -u 2 -s 1 -t {1}".format(GenomeName[i],attribute_value)
            cmd = "python /home/linproject/Projects/LIN_proto/workflow2.py {0}".format(arguments)
            f.write(cmd)
            f.write("\n")


