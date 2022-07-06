# -*- coding: utf-8 -*-
# @Time    : 2022/7/1 13:45
# @Author  : Jinyi Li
# @FileName: evaluation.py
# @Software: PyCharm
import pandas as pd
from pandas.core.frame import DataFrame

print("Run it to evaluate the matchmaking result")
df = pd.read_csv("results/MatchingResult.csv")

# fig = plt.figure(figsize=(10,6))
# plt.plot(df["blue team win rate"],linestyle='-',linewidth=2,color='steelblue',marker='o',markersize=2,markeredgecolor='black',markerfacecolor='steelblue')
# plt.title('blue team win rate')
# plt.xlabel('0')
# plt.ylabel('win rate')
#
# plt.show()
d1 = df["blue team win rate"].hist().get_figure()
d1.savefig("results/win_rate.jpg")
top_gap = []
jungle_gap = []
mid_gap = []
bottom_gap = []
support_gap = []
team_gap = []

print("Blue team win rate(average): {}".format(df["blue team win rate"].mean()))
gold_summoner = pd.read_csv("datasets/GoldSummData2016.csv")

log_counts = 0
for index, row in df.iterrows():
    top_score_gap = gold_summoner[gold_summoner["SummonerId"] == row["blue top"]]["Score"].values[0]-gold_summoner[gold_summoner["SummonerId"] == row["red top"]]["Score"].values[0]
    top_gap.append(abs(top_score_gap))
    jungle_score_gap = gold_summoner[gold_summoner["SummonerId"] == row["blue jungle"]]["Score"].values[0]-gold_summoner[gold_summoner["SummonerId"] == row["red jungle"]]["Score"].values[0]
    jungle_gap.append(abs(jungle_score_gap))
    mid_score_gap = gold_summoner[gold_summoner["SummonerId"] == row["blue mid"]]["Score"].values[0]-gold_summoner[gold_summoner["SummonerId"] == row["red mid"]]["Score"].values[0]
    mid_gap.append(abs(mid_score_gap))
    bottom_score_gap = gold_summoner[gold_summoner["SummonerId"] == row["blue bottom"]]["Score"].values[0]-gold_summoner[gold_summoner["SummonerId"] == row["red bottom"]]["Score"].values[0]
    bottom_gap.append(abs(bottom_score_gap))
    support_score_gap = gold_summoner[gold_summoner["SummonerId"] == row["blue support"]]["Score"].values[0]-gold_summoner[gold_summoner["SummonerId"] == row["red support"]]["Score"].values[0]
    support_gap.append(abs(support_score_gap))

    team_gap.append(top_score_gap*76 + jungle_score_gap*280 + mid_score_gap*214 + bottom_score_gap*288 + support_score_gap*295)
    log_counts += 1
    print("print log counts to show the evaluation is processing...{}".format(log_counts))

gap_dict = {"top gap": top_gap, "jungle gap":jungle_gap, "mid gap":mid_gap, "bottom gap":bottom_gap, "support gap": support_gap, "team gap": team_gap}
data_gap = DataFrame(gap_dict)
d2 = data_gap["top gap"].hist().get_figure()
d2.savefig("results/top gap.jpg")

d2 = data_gap["jungle gap"].hist().get_figure()
d2.savefig("results/jungle gap.jpg")

d2 = data_gap["mid gap"].hist().get_figure()
d2.savefig("results/mid gap.jpg")

d2 = data_gap["bottom gap"].hist().get_figure()
d2.savefig("results/bottom gap.jpg")

d2 = data_gap["support gap"].hist().get_figure()
d2.savefig("results/support gap.jpg")

d2 = data_gap["team gap"].hist().get_figure()
d2.savefig("results/team gap.jpg")

print("The biggest score gap between summoners as for Top is: {}".format(max(top_gap)))
print("The biggest score gap between summoners as for jungle is: {}".format(max(jungle_gap)))
print("The biggest score gap between summoners as for mid is: {}".format(max(mid_gap)))
print("The biggest score gap between summoners as for bottom is: {}".format(max(bottom_gap)))
print("The biggest score gap between summoners as for support is: {}".format(max(support_gap)))
# 213

top_gap.sort(reverse=True)
print("3.55% biggest score gap as for top is: {}".format(top_gap[212]))
jungle_gap.sort(reverse=True)
print("3.55% biggest score gap as for jungle is: {}".format(jungle_gap[212]))
mid_gap.sort(reverse=True)
print("3.55% biggest score gap as for mid is: {}".format(mid_gap[212]))
bottom_gap.sort(reverse=True)
print("3.55% biggest score gap as for bottom is: {}".format(bottom_gap[212]))
support_gap.sort(reverse=True)
print("3.55% biggest score gap as for support is: {}".format(support_gap[212]))
team_gap.sort(reverse=True)
print("3.55% biggest score gap between the teams is: {}".format(team_gap[212]))