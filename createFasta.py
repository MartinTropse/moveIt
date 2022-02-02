# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 20:16:11 2022

@author: martin.andersson-li
"""

import os 
import pandas as pd

os.chdir("C:/Bas/AquaBiota/Projekt/ECWA-NOR/PCR_Sekvenser/211220EN-003")
files=os.listdir()

text_file = open("ompF-F2.fasta", "w")

for file in files:
    seqStr = str()
    if file.endswith("ompF-F.txt"):
        df=pd.read_table(file, sep='\t', header=None)
        topStr=str(df.iloc[0,0])+"?"+str(df.iloc[0,1])+"!"
        df=df.drop(df.columns[1],axis =1)
        for x in range(1, df.shape[0]):
            seqStr=seqStr+df.iloc[x,0]
        mrgStr=topStr+seqStr        
        mrgStr=mrgStr.replace("!", "\n")
        mrgStr=mrgStr.replace("?", "\t")                   
        mrgStr=mrgStr+"\n\n"
        n = text_file.write(mrgStr)

text_file.close()

str1=str(df.iloc[0,0])
str2=str(df.iloc[0,1])   
topStr=str1+"?"+str2+"!"





    




text_file.close()
