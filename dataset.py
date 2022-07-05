# -*- coding: utf-8 -*-
# @Time    : 2022/6/28 15:06
# @Author  : Jinyi Li
# @FileName: dataset.py
# @Software: PyCharm

import pandas as pd
import numpy as np
from config import summoner

# df = pd.read_csv("SummIds2016.csv")
# counts = df[df["Rank"] == "BRONZE"].count()
# bronze = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
# bronze_index = 0
#
# counts = df[df["Rank"] == "SILVER"].count()
# silver = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
# silver_index = 0
#
# counts = df[df["Rank"] == "GOLD"].count()
# gold = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
# gold_index = 0
#
# counts = df[df["Rank"] == "PLATINUM"].count()
# platinum = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
# platinum_index = 0
#
# counts = df[df["Rank"] == "DIAMOND"].count()
# diamond = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
# diamond_index = 0
#
# counts = df[df["Rank"] == "MASTER"].count()
# master = np.random.normal(loc=125,scale=45,size=(counts["SummonerId"]))
# master_index = 0
#
# for index, row in df.iterrows():
#     if row["Rank"] == "BRONZE":
#         score = 1000 + int(bronze[bronze_index])
#         bronze_index += 1
#     elif row["Rank"] == "SILVER":
#         score = 1250 + int(silver[silver_index])
#         silver_index += 1
#     elif row["Rank"] == "GOLD":
#         score = 1500 + int(gold[gold_index])
#         gold_index += 1
#     elif row["Rank"] == "PLATINUM":
#         score = 1750 + int(platinum[platinum_index])
#         platinum_index += 1
#     elif row["Rank"] == "DIAMOND":
#         score = 2000 + int(diamond[diamond_index])
#         diamond_index += 1
#     elif row["Rank"] == "MASTER":
#         score = 2000 + int(master[master_index])
#         master_index += 1
#     else:
#         print("Unknown rank + {}".format(row["Rank"]))
#         raise TypeError
#     print("current summoner's({}) score is {}".format(index, score))
#     df.loc[index, 'Score'] = score
#
# df.to_csv("SummIds2016.csv")

# df = pd.read_csv("datasets/GoldSummData2016.csv")
# counts = df.count()
# win_rate = np.random.normal(loc=0.5,scale=0.05,size=(counts["SummonerId"]))
# win_rate_index = 0
# for index, row in df.iterrows():
#     summoner_id = row["SummonerId"]
#     score = summoner.score(summoner_id)
#     df.loc[index, 'Score'] = score
#     df.loc[index, 'WinRate'] = float(win_rate[win_rate_index])
#     print("current summoner's({}) score is {}, win rate is {}".format(index, score, float(win_rate[win_rate_index])))
#     win_rate_index += 1
#
# df.to_csv("GoldSummData2016.csv")

# df = pd.read_csv("datasets/matches.csv")
#
# invalid_matches = df[df["duration"] <= 300]
# rolling_matches = df[df["duration"] <= 1200]
# bad_matches = (rolling_matches.count()["id"] - invalid_matches.count()["id"])/(df.count()["id"]-invalid_matches.count()["id"])
# with open("statistic parameters.txt", "w+") as f:
#     f.write("bad matches rate: " + str(bad_matches))

good_top_influence = {}
good_jungle_influence = {}
good_mid_influence = {}
good_bottom_influence = {}
good_support_influence = {}
bad_top_influence = {}
bad_jungle_influence = {}
bad_mid_influence = {}
bad_bottom_influence = {}
bad_support_influence = {}
df = pd.read_csv("datasets/participants.csv")
matches_df = pd.read_csv("datasets/matches.csv")
participants_df = pd.read_csv("datasets/participants.csv")
stats1_df = pd.read_csv("datasets/stats1.csv")
stats2_df = pd.read_csv("datasets/stats2.csv")
for k, v in df.groupby("matchid").groups.items():
    print("start match {}".format(k))

    if len(v) != 10:
        # bad data
        continue

    if matches_df[matches_df["id"] == k]["duration"].values[0] <= 300:
        continue
    else:
        participants = participants_df[participants_df["index"].isin(v)]
        top_participants = participants[participants["position"] == "TOP"]
        jungle_participants = participants[participants["position"] == "JUNGLE"]
        mid_participants = participants[participants["position"] == "MID"]
        bottom_participants = participants[participants["role"] == "DUO_CARRY"]
        support_participants = participants[participants["role"] == "DUO_SUPPORT"]
        if len(top_participants) != 2 or len(jungle_participants) != 2 or len(mid_participants) != 2 or len(bottom_participants) != 2 or len(support_participants) != 2:
            continue

        if participants["id"].max() <= 1028381:
            stats_df = stats1_df[stats1_df["id"] <= participants["id"].max()]
            stats_df = stats_df[stats_df["id"] >= participants["id"].min()]
        elif participants["id"].min() > 1028381:
            stats_df = stats2_df[stats2_df["id"] <= participants["id"].max()]
            stats_df = stats_df[stats_df["id"] >= participants["id"].min()]
        else:
            stats_df_1 = stats1_df[stats1_df["id"] >= participants["id"].min()]
            stats_df_2 = stats2_df[stats2_df["id"] <= participants["id"].max()]
            stats_df = stats1_df.append(stats_df_2)

        win_team_kills = stats_df[stats_df["win"] == 1]["kills"].sum()
        win_team_assists = stats_df[stats_df["win"] == 1]["assists"].sum()
        loss_team_deaths = stats_df[stats_df["win"] == 0]["deaths"].sum()
        top_influence = 0
        for index, row in top_participants.iterrows():
            if stats_df[stats_df["id"] == row["id"]]["win"].values[0] == 0:
                if loss_team_deaths == 0:
                    top_influence += 0.2
                else:
                    top_influence += stats_df[stats_df["id"] == row["id"]]["deaths"].values[0] / loss_team_deaths
            else:
                if win_team_kills + win_team_assists == 0:
                    top_influence += 0.2
                else:
                    top_influence += (stats_df[stats_df["id"] == row["id"]]["kills"].values[0] + stats_df[stats_df["id"] == row["id"]]["assists"].values[0]) / (win_team_kills + win_team_assists)
        top_influence /= 2

        jungle_influence = 0
        for index, row in jungle_participants.iterrows():
            if stats_df[stats_df["id"] == row["id"]]["win"].values[0] == 0:
                if loss_team_deaths == 0:
                    jungle_influence += 0.2
                else:
                    jungle_influence += stats_df[stats_df["id"] == row["id"]]["deaths"].values[0] / loss_team_deaths
            else:
                if win_team_kills + win_team_assists == 0:
                    jungle_influence += 0.2
                else:
                    jungle_influence += (stats_df[stats_df["id"] == row["id"]]["kills"].values[0] + stats_df[stats_df["id"] == row["id"]]["assists"].values[0]) / (win_team_kills + win_team_assists)
        jungle_influence /= 2

        mid_influence = 0
        for index, row in mid_participants.iterrows():
            if stats_df[stats_df["id"] == row["id"]]["win"].values[0] == 0:
                if loss_team_deaths == 0:
                    mid_influence += 0.2
                else:
                    mid_influence += stats_df[stats_df["id"] == row["id"]]["deaths"].values[0] / loss_team_deaths
            else:
                if win_team_kills + win_team_assists == 0:
                    mid_influence += 0.2
                else:
                    mid_influence += (stats_df[stats_df["id"] == row["id"]]["kills"].values[0] + stats_df[stats_df["id"] == row["id"]]["assists"].values[0]) / (win_team_kills + win_team_assists)
        mid_influence /= 2

        bottom_influence = 0
        for index, row in bottom_participants.iterrows():
            if stats_df[stats_df["id"] == row["id"]]["win"].values[0] == 0:
                if loss_team_deaths == 0:
                    bottom_influence += 0.2
                else:
                    bottom_influence += stats_df[stats_df["id"] == row["id"]]["deaths"].values[0] / loss_team_deaths
            else:
                if win_team_kills + win_team_assists == 0:
                    bottom_influence += 0.2
                else:
                    bottom_influence += (stats_df[stats_df["id"] == row["id"]]["kills"].values[0] + stats_df[stats_df["id"] == row["id"]]["assists"].values[0]) / (win_team_kills + win_team_assists)
        bottom_influence /= 2

        support_influence = 0
        for index, row in support_participants.iterrows():
            if stats_df[stats_df["id"] == row["id"]]["win"].values[0] == 0:
                if loss_team_deaths == 0:
                    support_influence += 0.2
                else:
                    support_influence += stats_df[stats_df["id"] == row["id"]]["deaths"].values[0] / loss_team_deaths
            else:
                if win_team_kills + win_team_assists == 0:
                    support_influence += 0.2
                else:
                    support_influence += (stats_df[stats_df["id"] == row["id"]]["kills"].values[0] + stats_df[stats_df["id"] == row["id"]]["assists"].values[0]) / (win_team_kills + win_team_assists)
        support_influence /= 2

        # print(win_team_kills)
        # print(win_team_assists)
        # print(loss_team_deaths)
        # print(top_influence)
        # print(jungle_influence)
        # print(mid_influence)
        # print(bottom_influence)
        # print(support_influence)
        print(top_influence+jungle_influence+mid_influence+bottom_influence+support_influence)
        if matches_df[matches_df["id"] == k]["duration"].values[0] <= 1200:
            bad_top_influence.update({k: top_influence})
            bad_jungle_influence.update({k: jungle_influence})
            bad_mid_influence.update({k: mid_influence})
            bad_bottom_influence.update({k: bottom_influence})
            bad_support_influence.update({k: support_influence})
        else:
            good_top_influence.update({k: top_influence})
            good_jungle_influence.update({k: jungle_influence})
            good_mid_influence.update({k: mid_influence})
            good_bottom_influence.update({k: bottom_influence})
            good_support_influence.update({k: support_influence})
    print("finish match {}".format(k))

bad_top_influence_df = pd.DataFrame.from_dict(bad_top_influence,orient="index")
bad_top_influence_df.to_csv("bad_top_influence.csv")
bad_jungle_influence_df = pd.DataFrame.from_dict(bad_jungle_influence,orient="index")
bad_jungle_influence_df.to_csv("bad_jungle_influence.csv")
bad_mid_influence_df = pd.DataFrame.from_dict(bad_mid_influence,orient="index")
bad_mid_influence_df.to_csv("bad_mid_influence.csv")
bad_bottom_influence_df = pd.DataFrame.from_dict(bad_bottom_influence,orient="index")
bad_bottom_influence_df.to_csv("bad_bottom_influence.csv")
bad_support_influence_df = pd.DataFrame.from_dict(bad_support_influence,orient="index")
bad_support_influence_df.to_csv("bad_support_influence.csv")
good_top_influence_df = pd.DataFrame.from_dict(good_top_influence,orient="index")
good_top_influence_df.to_csv("good_top_influence.csv")
good_jungle_influence_df = pd.DataFrame.from_dict(good_jungle_influence,orient="index")
good_jungle_influence_df.to_csv("good_jungle_influence.csv")
good_mid_influence_df = pd.DataFrame.from_dict(good_mid_influence,orient="index")
good_mid_influence_df.to_csv("good_mid_influence.csv")
good_bottom_influence_df = pd.DataFrame.from_dict(good_bottom_influence,orient="index")
good_bottom_influence_df.to_csv("good_bottom_influence.csv")
good_support_influence_df = pd.DataFrame.from_dict(good_support_influence,orient="index")
good_support_influence_df.to_csv("good_support_influence.csv")

with open("statistic parameters.txt", "a+") as f:
    f.write("bad matches top max influence: " + str(max(bad_top_influence.values())))
    f.write("bad matches top min influence: " + str(min(bad_top_influence.values())))
    f.write("bad matches top average influence: " + str(np.mean(list(bad_top_influence.values()))))

    f.write("bad matches jungle max influence: " + str(max(bad_jungle_influence.values())))
    f.write("bad matches jungle min influence: " + str(min(bad_jungle_influence.values())))
    f.write("bad matches jungle average influence: " + str(np.mean(list(bad_jungle_influence.values()))))

    f.write("bad matches mid max influence: " + str(max(bad_mid_influence.values())))
    f.write("bad matches mid min influence: " + str(min(bad_mid_influence.values())))
    f.write("bad matches mid average influence: " + str(np.mean(list(bad_mid_influence.values()))))

    f.write("bad matches bottom max influence: " + str(max(bad_bottom_influence.values())))
    f.write("bad matches bottom min influence: " + str(min(bad_bottom_influence.values())))
    f.write("bad matches bottom average influence: " + str(np.mean(list(bad_bottom_influence.values()))))

    f.write("bad matches support max influence: " + str(max(bad_support_influence.values())))
    f.write("bad matches support min influence: " + str(min(bad_support_influence.values())))
    f.write("bad matches support average influence: " + str(np.mean(list(bad_support_influence.values()))))

    f.write("good matches top max influence: " + str(max(good_top_influence.values())))
    f.write("good matches top min influence: " + str(min(good_top_influence.values())))
    f.write("good matches top average influence: " + str(np.mean(list(good_top_influence.values()))))

    f.write("good matches jungle max influence: " + str(max(good_jungle_influence.values())))
    f.write("good matches jungle min influence: " + str(min(good_jungle_influence.values())))
    f.write("good matches jungle average influence: " + str(np.mean(list(good_jungle_influence.values()))))

    f.write("good matches mid max influence: " + str(max(good_mid_influence.values())))
    f.write("good matches mid min influence: " + str(min(good_mid_influence.values())))
    f.write("good matches mid average influence: " + str(np.mean(list(good_mid_influence.values()))))

    f.write("good matches bottom max influence: " + str(max(good_bottom_influence.values())))
    f.write("good matches bottom min influence: " + str(min(good_bottom_influence.values())))
    f.write("good matches bottom average influence: " + str(np.mean(list(good_bottom_influence.values()))))

    f.write("good matches support max influence: " + str(max(good_support_influence.values())))
    f.write("good matches support min influence: " + str(min(good_support_influence.values())))
    f.write("good matches support average influence: " + str(np.mean(list(good_support_influence.values()))))


