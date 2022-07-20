# -*- coding: utf-8 -*-
# @Time    : 2022/6/29 16:02
# @Author  : Jinyi Li
# @FileName: EloRating.py
# @Software: PyCharm
import random
import threading
import time
import logging
import pandas as pd

from config import matching, gold_summoner


def log_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


logger = logging.getLogger()
logger.setLevel('DEBUG')
basic_format = "%(asctime)s %(levelname)s: %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(basic_format, date_format)
chlr = logging.StreamHandler()
chlr.setFormatter(formatter)
chlr.setLevel("DEBUG")
fhlr = logging.FileHandler("log/ELORating_{}.log".format(time.time()))
fhlr.setFormatter(formatter)
logger.addHandler(chlr)
logger.addHandler(fhlr)


class EloRating:
    ELO_RESULT_WIN = 1
    ELO_RESULT_LOSS = -1
    ELO_RESULT_TIE = 0

    ELO_RATING_DEFAULT = 1500

    rating_b = 0
    rating_r = 0

    def __init__(self, rating_b=ELO_RATING_DEFAULT, rating_r=ELO_RATING_DEFAULT):
        self.rating_b = rating_b
        self.rating_r = rating_r

    def compute_score(self):
        result = 1 / (1 + pow(10, (self.rating_r - self.rating_b) / 400))
        logger.debug("compute rate: {}".format(result))
        return result


class MatchingPoolThread(threading.Thread):
    matching_pool = {}
    matching_counts_left = 6000
    elo_rating = EloRating()
    result_matching_data = []
    is_end = False
    win_rate_max = 0.55
    win_rate_min = 0.45

    def __init__(self):
        threading.Thread.__init__(self)
        self.gold_summoner = pd.read_csv("datasets/GoldSummData2016.csv")

    def run(self):
        last_time = time.time()
        while True:
            if int(time.time() - last_time) >= 2:
                logger.debug("current pool size: {}".format(len(self.matching_pool)))
                last_time = time.time()

            self.matching_process()
            if self.matching_counts_left == 0:
                self.save_to_csv()
                self.is_end = True
                break

    def matching_process(self):
        if len(self.matching_pool) < 10:
            return

        for k in list(self.matching_pool.keys()):
            v = self.matching_pool.get(k)
            if v is None:
                continue
            waiting_time = int(time.time() - v)
            score_gap = matching.value(waiting_time)
            if score_gap is None:
                # print("{} debug: remove unmatchable summoner: {}".format(log_time(), v.split(",")[0]), file=log_file, flush=True)
                del self.matching_pool[k]
                self.matching_pool.update({k: time.time()})
                logger.debug("reenter unmatchable summoner: {}, current pool size: {}".format(k.split(",")[0], len(self.matching_pool)))
                continue

            summoner_id, role = k.split(',')
            summoner_list = self.blue_team(summoner_id, role, score_gap)
            if "" in summoner_list:
                continue

            summoner_list.extend(self.red_team(summoner_id, summoner_list, score_gap))
            if "" in summoner_list:
                continue

            summoner_list.extend([self.elo_rating.compute_score()])
            self.matching_success(summoner_list)
            return

    def score(self, summoner_id, role=None):
        summoner = self.gold_summoner[self.gold_summoner["SummonerId"] == int(summoner_id)]
        return int(summoner["Score"].values[0])

    def win_rate(self, summoner_id):
        summoner = self.gold_summoner[self.gold_summoner["SummonerId"] == int(summoner_id)]
        return float(summoner["WinRate"].values[0])

    def blue_team(self, summoner_id, role, score_gap):
        team = [False, False, False, False, False]
        team_list = ["", "", "", "", ""]
        team[int(role) - 1] = True
        team_list[int(role) - 1] = summoner_id

        # if gold_summoner.win_rate(summoner_id) > 0.5:
        #     if random.random() > 0.5:
        #         balance_player_number = 2
        #     else:
        #         balance_player_number = 1
        #
        #     print("{} debug: find {} balance summoner(s)".format(log_time(), balance_player_number))
        #     for k in list(self.matching_pool.keys()):
        #         v = self.matching_pool.get(k)
        #         current_summoner_id, current_role = v.split(',')
        #         if gold_summoner.score(summoner_id) > gold_summoner.score(current_summoner_id):
        #             if not team[int(current_role) - 1]:
        #                 team_list[int(current_role) - 1] = current_summoner_id
        #                 team[int(current_role) - 1] = True
        #                 balance_player_number -= 1
        #             elif team.count(False) == 1 and int(time.time() - k) > 300:
        #                 fill_in_role = team.index(False)
        #                 team_list[fill_in_role] = current_summoner_id
        #                 team[fill_in_role] = True
        #                 balance_player_number -= 1
        #
        #             if balance_player_number == 0:
        #                 break

        for k in list(self.matching_pool.keys()):
            v = self.matching_pool.get(k)
            current_summoner_id, current_role = k.split(',')
            if abs(self.score(summoner_id) - self.score(current_summoner_id)) <= score_gap:
                if not team[int(current_role) - 1]:
                    team_list[int(current_role) - 1] = current_summoner_id
                    team[int(current_role) - 1] = True
                elif team.count(False) == 1 and int(time.time() - v) > 300:
                    fill_in_role = team.index(False)
                    team_list[fill_in_role] = current_summoner_id
                    team[fill_in_role] = True

            if False not in team:
                break

        logger.debug("current blue team: {}".format(team_list))
        return team_list

    def red_team(self, summoner_id, summoner_list, score_gap):
        team = [False, False, False, False, False]
        team_list = ["", "", "", "", ""]
        is_change = True
        b_win = 0
        for k in list(self.matching_pool.keys()):
            v = self.matching_pool.get(k)
            current_summoner_id, current_role = k.split(',')
            if False in team:
                if current_summoner_id not in summoner_list and abs(
                        self.score(summoner_id) - self.score(current_summoner_id)) <= score_gap:
                    if not team[int(current_role) - 1]:
                        team_list[int(current_role) - 1] = current_summoner_id
                        team[int(current_role) - 1] = True
                    elif team.count(False) == 1 and int(time.time() - v) > 300:
                        fill_in_role = team.index(False)
                        team_list[fill_in_role] = current_summoner_id
                        team[fill_in_role] = True
            else:
                if is_change:
                    self.elo_rating.rating_b = self.get_team_score(summoner_list)
                    self.elo_rating.rating_r = self.get_team_score(team_list)
                    b_win = self.elo_rating.compute_score()
                    is_change = False
                    cosine_similarity_test = self.cosine_similarity(summoner_list, team_list)

                    if cosine_similarity_test:
                        if b_win < self.win_rate_min:
                            if current_summoner_id not in summoner_list and abs(
                                    self.score(summoner_id) - self.score(
                                            current_summoner_id)) <= score_gap and self.score(
                                    team_list[int(current_role) - 1]) > self.score(current_summoner_id):
                                team_list[int(current_role) - 1] = current_summoner_id
                                is_change = True
                            elif int(time.time() - v) > 300:
                                for s in team_list:
                                    if self.score(s) > self.score(current_summoner_id):
                                        s_index = team_list.index(s)
                                        team_list[s_index] = current_summoner_id
                                        is_change = True
                                        break
                        elif b_win > self.win_rate_max:
                            if current_summoner_id not in summoner_list and abs(
                                    self.score(summoner_id) - self.score(
                                            current_summoner_id)) <= score_gap and self.score(
                                    team_list[int(current_role) - 1]) < self.score(current_summoner_id):
                                team_list[int(current_role) - 1] = current_summoner_id
                                is_change = True
                            elif int(time.time() - v) > 300:
                                for s in team_list:
                                    if self.score(s) < self.score(current_summoner_id):
                                        s_index = team_list.index(s)
                                        team_list[s_index] = current_summoner_id
                                        is_change = True
                                        break
                        else:
                            logger.debug("current red team: {}".format(team_list))
                            return team_list
                    else:
                        if current_summoner_id not in summoner_list and abs(self.score(summoner_id) - self.score(current_summoner_id)) <= score_gap:
                            team_list[int(current_role) - 1] = current_summoner_id
                            is_change = True

        return self.internal_exchange(summoner_list, team_list, b_win)

        # if "" in team_list:
        #     return team_list
        #
        # for i in range(5):
        #     if (b_win < 0.45 and self.score(summoner_list[i]) < self.score(team_list[i])) or (b_win > 0.55 and self.score(summoner_list[i]) > self.score(team_list[i])) or not self.cosine_similarity(summoner_list, team_list):
        #         temp = team_list[i]
        #         team_list[i] = summoner_list[i]
        #         summoner_list[i] = temp
        #         logger.debug("internal exchange for role {}: {} vs {}".format(i, summoner_list, team_list))
        #         self.elo_rating.rating_b = self.get_team_score(summoner_list)
        #         self.elo_rating.rating_r = self.get_team_score(team_list)
        #         b_win = self.elo_rating.compute_score()
        #     elif 0.45 <= b_win <= 0.55:
        #         return team_list
        #
        # return ["", "", "", "", ""]

    def internal_exchange(self, summoner_list, team_list, b_win):
        if "" in team_list:
            return team_list

        for i in range(5):
            if (b_win < self.win_rate_min and self.score(summoner_list[i]) < self.score(team_list[i])) or (b_win > self.win_rate_max and self.score(summoner_list[i]) > self.score(team_list[i])) or not self.cosine_similarity(summoner_list, team_list):
                temp = team_list[i]
                team_list[i] = summoner_list[i]
                summoner_list[i] = temp
                logger.debug("internal exchange for role {}: {} vs {}".format(i, summoner_list, team_list))
                self.elo_rating.rating_b = self.get_team_score(summoner_list)
                self.elo_rating.rating_r = self.get_team_score(team_list)
                b_win = self.elo_rating.compute_score()
            elif self.win_rate_min <= b_win <= self.win_rate_max:
                return team_list

        return ["", "", "", "", ""]

    def get_team_score(self, team_list):
        score = 0
        for s in team_list:
            score += self.score(s)

        score /= 5
        logger.debug("current team average score: {}".format(score))
        return score

    def cosine_similarity(self, blue_team, red_team):
        return True

    def enter_pool(self, summoner_id, role):
        current_time = time.time()
        key = str(summoner_id) + ',' + str(role)
        # print("enter queue: {}".format({current_time: value}))
        self.matching_pool.update({key: current_time})

    def matching_success(self, summoner_list):
        print("matching success")
        for s in summoner_list:
            for k in list(self.matching_pool.keys()):
                if k.split(',')[0] == str(s):
                    del self.matching_pool[k]

        self.matching_counts_left -= 1
        logger.debug("remove summoners, current pool size: {}. Left matching size: {}".format(len(self.matching_pool), self.matching_counts_left))
        self.save_matching_data(summoner_list)

    def save_matching_data(self, summoner_list):
        self.result_matching_data.append(summoner_list)
        logger.info("matching result: {}. Predict blue team win rate: {}".format(summoner_list, self.elo_rating.compute_score()))

    def save_to_csv(self):
        name = ["blue top", "blue jungle", "blue mid", "blue bottom", "blue support", "red top", "red jungle", "red mid", "red bottom", "red support", "blue team win rate"]
        csv_data = pd.DataFrame(columns=name, data=self.result_matching_data)
        csv_data.to_csv("results/MatchingResult5.csv", encoding='utf-8')


if __name__ == "__main__":
    matching_pool = MatchingPoolThread()
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
