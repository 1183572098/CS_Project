# -*- coding: utf-8 -*-
# @Time    : 2022/7/1 13:45
# @Author  : Jinyi Li
# @FileName: evaluation.py
# @Software: PyCharm
import pandas as pd
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

print("Run it to evaluate the matchmaking result")
# df = pd.read_csv("results/MatchingResult1.csv")
df = pd.read_csv("optimization_results/OptimizationMatchingResult6.csv")

# fig = plt.figure(figsize=(10,6))
# plt.plot(df["blue team win rate"],linestyle='-',linewidth=2,color='steelblue',marker='o',markersize=2,markeredgecolor='black',markerfacecolor='steelblue')
# plt.title('blue team win rate')
# plt.xlabel('0')
# plt.ylabel('win rate')
#
# plt.show()
# d1 = df["blue team win rate"].hist().get_figure()
# d1.savefig("results/win_rate.jpg")
# d1.savefig("optimization_results/win_rate.jpg")
win_rate = []
top_gap = []
jungle_gap = []
mid_gap = []
bottom_gap = []
support_gap = []
team_gap = []
cosine = []
elo_rate = []

print("Blue team win rate(average): {}".format(df["blue team win rate"].mean()))
gold_summoner = pd.read_csv("datasets/GoldSummData2016.csv")


def compute_score(blue_score, red_score):
    k = [76, 280, 214, 288, 295]
    gap_vector = (np.array(red_score) - np.array(blue_score))*np.array(k)/sum(k)

    cosine = np.array(red_score).dot(gap_vector)
    if cosine > 0:
        d = -np.linalg.norm(gap_vector)
    else:
        d = np.linalg.norm(gap_vector)
    result = 1 / (1 + pow(10, d / 400))
    return result


log_counts = 0
bad_counts = 0
for index, row in df.iterrows():
    win_rate.append(row["blue team win rate"])
    blue_team_score = [gold_summoner[gold_summoner["SummonerId"] == row["blue top"]]["Score"].values[0], gold_summoner[gold_summoner["SummonerId"] == row["blue jungle"]]["Score"].values[0], gold_summoner[gold_summoner["SummonerId"] == row["blue mid"]]["Score"].values[0], gold_summoner[gold_summoner["SummonerId"] == row["blue bottom"]]["Score"].values[0], gold_summoner[gold_summoner["SummonerId"] == row["blue support"]]["Score"].values[0]]
    red_team_score = [gold_summoner[gold_summoner["SummonerId"] == row["red top"]]["Score"].values[0], gold_summoner[gold_summoner["SummonerId"] == row["red jungle"]]["Score"].values[0], gold_summoner[gold_summoner["SummonerId"] == row["red mid"]]["Score"].values[0], gold_summoner[gold_summoner["SummonerId"] == row["red bottom"]]["Score"].values[0], gold_summoner[gold_summoner["SummonerId"] == row["red support"]]["Score"].values[0]]
    elo_rate.append(compute_score(blue_team_score, red_team_score))
    if compute_score(blue_team_score, red_team_score) < 0.445 or compute_score(blue_team_score, red_team_score) > 0.555:
        bad_counts += 1
    if 0.51 >= compute_score(blue_team_score, red_team_score) >= 0.49:
        top_score_gap = blue_team_score[0] - red_team_score[0]
        top_gap.append(abs(top_score_gap))
        jungle_score_gap = blue_team_score[1] - red_team_score[1]
        jungle_gap.append(abs(jungle_score_gap))
        mid_score_gap = blue_team_score[2] - red_team_score[2]
        mid_gap.append(abs(mid_score_gap))
        bottom_score_gap = blue_team_score[3] - red_team_score[3]
        bottom_gap.append(abs(bottom_score_gap))
        support_score_gap = blue_team_score[4] - red_team_score[4]
        support_gap.append(abs(support_score_gap))

    # normalize

        blue_team_score = (blue_team_score-np.mean(blue_team_score))/np.std(blue_team_score)
        red_team_score = (red_team_score-np.mean(red_team_score))/np.std(red_team_score)
        cosine_sim = np.dot(blue_team_score, red_team_score) / (np.linalg.norm(blue_team_score)*np.linalg.norm(red_team_score))
        cosine_dist = -np.log(cosine_sim/2+0.5)
        cosine.append(cosine_dist)
        team_gap.append(abs((top_score_gap*76 + jungle_score_gap*280 + mid_score_gap*214 + bottom_score_gap*288 + support_score_gap*295)/1153))
        log_counts += 1
        print("print log counts to show the evaluation is processing...{}".format(log_counts))

# gap_dict = {"top gap": top_gap, "jungle gap":jungle_gap, "mid gap":mid_gap, "bottom gap":bottom_gap, "support gap": support_gap, "team gap": team_gap}
# data_gap = DataFrame(gap_dict)
ax = sns.displot(top_gap, kde=True)
# ax.savefig("results/top gap.jpg")
ax.savefig("optimization_results/top gap.jpg")

ax = sns.displot(jungle_gap, kde=True)
# ax.savefig("results/jungle gap.jpg")
ax.savefig("optimization_results/jungle gap.jpg")

ax = sns.displot(mid_gap, kde=True)
# ax.savefig("results/mid gap.jpg")
ax.savefig("optimization_results/mid gap.jpg")

ax = sns.displot(bottom_gap, kde=True)
# ax.savefig("results/bottom gap.jpg")
ax.savefig("optimization_results/bottom gap.jpg")

ax = sns.displot(support_gap, kde=True)
# ax.savefig("results/support gap.jpg")
ax.savefig("optimization_results/support gap.jpg")

ax = sns.displot(team_gap, kde=True)
# ax.savefig("results/team gap.jpg")
ax.savefig("optimization_results/team gap.jpg")

ax = sns.displot(cosine, kde=True)
# ax.savefig("results/cosine.jpg")
ax.savefig("optimization_results/cosine.jpg")

print("The biggest score gap between summoners as for Top is: {}".format(max(top_gap)))
print("The biggest score gap between summoners as for jungle is: {}".format(max(jungle_gap)))
print("The biggest score gap between summoners as for mid is: {}".format(max(mid_gap)))
print("The biggest score gap between summoners as for bottom is: {}".format(max(bottom_gap)))
print("The biggest score gap between summoners as for support is: {}".format(max(support_gap)))
# 213

print("The average score gap between summoners as for Top is: {}".format(np.mean(top_gap)))
print("The average score gap between summoners as for jungle is: {}".format(np.mean(jungle_gap)))
print("The average score gap between summoners as for mid is: {}".format(np.mean(mid_gap)))
print("The average score gap between summoners as for bottom is: {}".format(np.mean(bottom_gap)))
print("The average score gap between summoners as for support is: {}".format(np.mean(support_gap)))
# 213

# top_gap.sort(reverse=True)
# print("3.55% biggest score gap as for top is: {}".format(top_gap[212]))
# jungle_gap.sort(reverse=True)
# print("3.55% biggest score gap as for jungle is: {}".format(jungle_gap[212]))
# mid_gap.sort(reverse=True)
# print("3.55% biggest score gap as for mid is: {}".format(mid_gap[212]))
# bottom_gap.sort(reverse=True)
# print("3.55% biggest score gap as for bottom is: {}".format(bottom_gap[212]))
# support_gap.sort(reverse=True)
# print("3.55% biggest score gap as for support is: {}".format(support_gap[212]))
# team_gap.sort(reverse=True)
# print("3.55% biggest score gap between the teams is: {}".format(team_gap[212]))
#
# cosine.sort(reverse=True)
# print("3.55% smallest cosine similarity is: {}".format(cosine[212]))

# elo = {"win_rate": elo_rate}
# dr = sns.displot(elo, x="win_rate")
# # d1.savefig("results/win_rate.jpg")
# dr.savefig("results/win_rate2.jpg")

di = {"win_rate": win_rate}
d1 = sns.displot(di, x="win_rate")
d1.savefig("optimization_results/win_rate.jpg")

print("bad match counts: {}".format(bad_counts))