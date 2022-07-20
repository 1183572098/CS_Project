# -*- coding: utf-8 -*-
# @Time    : 2022/7/7 22:53
# @Author  : Jinyi Li
# @FileName: optimization.py
# @Software: PyCharm

import random
from EloRating import MatchingPoolThread, logger, EloRating
import pandas as pd
import numpy as np
from config import gold_summoner


class OptimizationEloRating(EloRating):
    k = [76, 280, 214, 288, 295]
    ELO_RATING_DEFAULT = [1500, 1500, 1500, 1500, 1500]

    rating_b = None
    rating_r = None

    def __init__(self, rating_b=None, rating_r=None):
        super().__init__()
        if rating_r is None:
            self.rating_r = self.ELO_RATING_DEFAULT
        if rating_b is None:
            self.rating_b = self.ELO_RATING_DEFAULT

    def compute_score(self):
        gap_vector = (np.array(self.rating_r) - np.array(self.rating_b))*np.array(self.k)/sum(self.k)

        cosine = np.array(self.rating_r).dot(gap_vector)
        if cosine > 0:
            d = -np.linalg.norm(gap_vector)
        else:
            d = np.linalg.norm(gap_vector)
        result = 1 / (1 + pow(10, d / 400))
        logger.debug("compute rate: {}".format(result))
        return result


class OptimizationMatchingPoolThread(MatchingPoolThread):
    k = [76, 280, 214, 288, 295]
    cosine_k = 2.6066033960030635
    elo_rating = OptimizationEloRating()
    win_rate_max = 0.555
    win_rate_min = 0.445

    def __init__(self):
        super().__init__()

    # def score(self, summoner_id, role=None):
    #     if role is None:
    #         return None
    #
    #     summoner = self.gold_summoner[self.gold_summoner["SummonerId"] == int(summoner_id)]
    #     top_role_num = len(str(summoner["Top"].values[0]).split(" "))
    #     jungle_role_num = len(str(summoner["Jungle"].values[0]).split(" "))
    #     mid_role_num = len(str(summoner["Mid"].values[0]).split(" "))
    #     bottom_role_num = len(str(summoner["Adc"].values[0]).split(" "))
    #     support_role_num = len(str(summoner["Support"].values[0]).split(" "))
    #

    # def get_team_score(self, team_list):
    #     team_score_list = []
    #     for s in team_list:
    #         team_score_list.append(self.score(s))
    #     score_list = [x*y for x, y in zip(team_score_list, self.k)]
    #     logger.debug("current team score: {}".format(sum(score_list) / sum(self.k)))
    #     return sum(score_list) / sum(self.k)

    def get_team_score(self, team_list):
        team_score_list = []
        for s in team_list:
            team_score_list.append(self.score(s))
        logger.debug("current team score: {}".format(team_score_list))
        return team_score_list

    def internal_exchange(self, summoner_list, team_list, b_win):
        return ["", "", "", "", ""]

    def cosine_similarity(self, blue_team, red_team):
        blue_team_score = []
        for s in blue_team:
            blue_team_score.append(self.score(s))

        red_team_score = []
        for s in red_team:
            red_team_score.append(self.score(s))

        blue_team_score = (blue_team_score-np.mean(blue_team_score))/np.std(blue_team_score)
        red_team_score = (red_team_score-np.mean(red_team_score))/np.std(red_team_score)
        cosine_sim = np.dot(blue_team_score, red_team_score) / (np.linalg.norm(blue_team_score)*np.linalg.norm(red_team_score))
        cosine_dist = -np.log(cosine_sim/2+0.5)
        logger.debug("current matching cosine similarity distance: {}".format(cosine_dist))
        if cosine_dist < self.cosine_k:
            return True
        else:
            return False

    def save_to_csv(self):
        name = ["blue top", "blue jungle", "blue mid", "blue bottom", "blue support", "red top", "red jungle", "red mid", "red bottom", "red support", "blue team win rate"]
        csv_data = pd.DataFrame(columns=name, data=self.result_matching_data)
        csv_data.to_csv("optimization_results/OptimizationMatchingResult6.csv", encoding='utf-8')


if __name__ == "__main__":
    matching_pool = OptimizationMatchingPoolThread()
    matching_pool.start()
    # queue_order = random.sample(range(1,480423), 480422)
    queue_order = random.sample(range(1, 131553), 131552)
    order_counts = 0
    for order in queue_order:
        apply_role = random.randint(1, 5)
        matching_pool.enter_pool(gold_summoner.ids(order), apply_role)
        order_counts += 1
        if order_counts % 10000 == 0:
            logger.debug("debug: {} summoners entered pool".format(order_counts))
        if matching_pool.is_end:
            break
