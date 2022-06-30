# -*- coding: utf-8 -*-
# @Time    : 2022/6/28 15:06
# @Author  : Jinyi Li
# @FileName: dataset.py
# @Software: PyCharm
import json

import pandas as pd
import numpy as np

df = pd.read_csv("SummIds2016.csv")
counts = df[df["Rank"] == "BRONZE"].count()
bronze = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
bronze_index = 0

counts = df[df["Rank"] == "SILVER"].count()
silver = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
silver_index = 0

counts = df[df["Rank"] == "GOLD"].count()
gold = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
gold_index = 0

counts = df[df["Rank"] == "PLATINUM"].count()
platinum = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
platinum_index = 0

counts = df[df["Rank"] == "DIAMOND"].count()
diamond = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
diamond_index = 0

counts = df[df["Rank"] == "MASTER"].count()
master = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
master_index = 0

for index, row in df.iterrows():
    if row["Rank"] == "BRONZE":
        score = 1000 + int(bronze[bronze_index])
        bronze_index += 1
    elif row["Rank"] == "SILVER":
        score = 1250 + int(silver[silver_index])
        silver_index += 1
    elif row["Rank"] == "GOLD":
        score = 1500 + int(gold[gold_index])
        gold_index += 1
    elif row["Rank"] == "PLATINUM":
        score = 1750 + int(platinum[platinum_index])
        platinum_index += 1
    elif row["Rank"] == "DIAMOND":
        score = 2000 + int(diamond[diamond_index])
        diamond_index += 1
    elif row["Rank"] == "MASTER":
        score = 2000 + int(master[master_index])
        master_index += 1
    else:
        print("Unknown rank + {}".format(row["Rank"]))
        raise TypeError
    print("current summoner's({}) score is {}".format(index, score))
    df.loc[index, 'Score'] = score

df.to_csv("SummIds2016.csv")