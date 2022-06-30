# -*- coding: utf-8 -*-
# @Time    : 2022/6/29 16:02
# @Author  : Jinyi Li
# @FileName: EloRating.py
# @Software: PyCharm
import queue
import random
import threading
import time

import pandas as pd

from config import matching, summoner, gold_summoner


def log_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


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
        print("{} debug: compute rate: {}".format(log_time(), result))
        return result


class MatchingPoolThread(threading.Thread):
    matching_pool = {}
    matching_counts_left = 1000
    elo_rating = EloRating()
    result_matching_data = []
    is_end = False

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        last_time = time.time()
        while True:
            if int(time.time() - last_time) >= 2:
                print("{} debug: current pool size: {}".format(log_time(), len(self.matching_pool)))
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
            waiting_time = int(time.time() - k)
            score_gap = matching.value(waiting_time)
            if score_gap is None:
                print("{} debug: remove unmatchable summoner: {}".format(log_time(), len(v.split(",")[0])))
                del self.matching_pool[k]
                continue

            summoner_id, role = v.split(',')
            summoner_list = self.blue_team(summoner_id, role, score_gap)
            if "" in summoner_list:
                return

            summoner_list.extend(self.red_team(summoner_id, summoner_list, score_gap))
            if "" in summoner_list:
                return

            summoner_list.extend([self.elo_rating.compute_score()])
            self.matching_success(summoner_list)
            return

    def blue_team(self, summoner_id, role, score_gap):
        team = [False, False, False, False, False]
        team_list = ["", "", "", "", ""]
        team[int(role) - 1] = True
        team_list[int(role) - 1] = summoner_id
        for k in list(self.matching_pool.keys()):
            v = self.matching_pool.get(k)
            current_summoner_id, current_role = v.split(',')
            if abs(summoner.score(summoner_id) - summoner.score(current_summoner_id)) <= score_gap:
                if not team[int(current_role) - 1]:
                    team_list[int(current_role) - 1] = current_summoner_id
                    team[int(current_role) - 1] = True
                elif team.count(False) == 1 and int(time.time() - k) > 300:
                    fill_in_role = team.index(False)
                    team_list[fill_in_role] = current_summoner_id
                    team[fill_in_role] = True
            if False not in team:
                break

        print("{} debug: current blue team: {}".format(log_time(), team_list))
        return team_list

    def red_team(self, summoner_id, summoner_list, score_gap):
        team = [False, False, False, False, False]
        team_list = ["", "", "", "", ""]
        blue_team_score = self.get_team_score(summoner_list)
        is_change = True
        b_win = 0
        for k in list(self.matching_pool.keys()):
            v = self.matching_pool.get(k)
            current_summoner_id, current_role = v.split(',')
            if False in team:
                if current_summoner_id not in summoner_list and abs(
                        summoner.score(summoner_id) - summoner.score(current_summoner_id)) <= score_gap:
                    if not team[int(current_role) - 1]:
                        team_list[int(current_role) - 1] = current_summoner_id
                        team[int(current_role) - 1] = True
                    elif team.count(False) == 1 and int(time.time() - k) > 300:
                        fill_in_role = team.index(False)
                        team_list[fill_in_role] = current_summoner_id
                        team[fill_in_role] = True
            else:
                if is_change:
                    red_team_score = self.get_team_score(team_list)
                    self.elo_rating.rating_b = blue_team_score
                    self.elo_rating.rating_r = red_team_score
                    b_win = self.elo_rating.compute_score()
                    is_change = False

                    if b_win < 0.45:
                        if current_summoner_id not in summoner_list and abs(
                                summoner.score(summoner_id) - summoner.score(
                                        current_summoner_id)) <= score_gap and summoner.score(
                                team_list[int(current_role) - 1]) > summoner.score(current_summoner_id):
                            team_list[int(current_role) - 1] = current_summoner_id
                            is_change = True
                        elif int(time.time() - k) > 300:
                            for s in team_list:
                                if summoner.score(s) > summoner.score(current_summoner_id):
                                    s_index = team_list.index(s)
                                    team_list[s_index] = current_summoner_id
                                    is_change = True
                                    break
                    elif b_win > 0.55:
                        if current_summoner_id not in summoner_list and abs(
                                summoner.score(summoner_id) - summoner.score(
                                        current_summoner_id)) <= score_gap and summoner.score(
                                team_list[int(current_role) - 1]) < summoner.score(current_summoner_id):
                            team_list[int(current_role) - 1] = current_summoner_id
                            is_change = True
                        elif int(time.time() - k) > 300:
                            for s in team_list:
                                if summoner.score(s) < summoner.score(current_summoner_id):
                                    s_index = team_list.index(s)
                                    team_list[s_index] = current_summoner_id
                                    is_change = True
                                    break
                    else:
                        print("{} debug: current red team: {}".format(log_time(), team_list))
                        return team_list

        if "" in team_list:
            return team_list

        for i in range(5):
            if (b_win < 0.45 and summoner.score(summoner_list[i]) < summoner.score(team_list[i])) or (b_win > 0.55 and summoner.score(summoner_list[i]) > summoner.score(team_list[i])):
                temp = team_list[i]
                team_list[i] = summoner_list[i]
                summoner_list[i] = temp
                print("{} debug: internal exchange for role {}: {} vs {}".format(log_time(), i, summoner_list, team_list))
                self.elo_rating.rating_b = self.get_team_score(summoner_list)
                self.elo_rating.rating_r = self.get_team_score(team_list)
                b_win = self.elo_rating.compute_score()
            elif 0.45 <= b_win <= 0.55:
                return team_list

        return ["", "", "", "", ""]

    def get_team_score(self, team_list):
        score = 0
        for s in team_list:
            score += summoner.score(s)

        print("{} debug: current team score: {}".format(log_time(), score))
        return score

    def enter_pool(self, summoner_id, role):
        current_time = time.time()
        value = str(summoner_id) + ',' + str(role)
        # print("enter queue: {}".format({current_time: value}))
        self.matching_pool.update({current_time: value})

    def matching_success(self, summoner_list):
        print("debug: matching success")
        for s in summoner_list:
            for k in list(self.matching_pool.keys()):
                if self.matching_pool[k].split(',')[0] == str(s):
                    del self.matching_pool[k]

        print("{} debug: remove summoners, current pool size: {}".format(log_time(), len(self.matching_pool)))
        self.matching_counts_left -= 1
        self.save_matching_data(summoner_list)

    def save_matching_data(self, summoner_list):
        self.result_matching_data.append(summoner_list)
        print("{} info: matching result: {}. Predict blue team win rate: {}".format(log_time(), summoner_list,
                                                                                    self.elo_rating.compute_score()))

    def save_to_csv(self):
        name = ["blue top", "blue jungle", "blue mid", "blue bottom", "blue support", "red top", "red jungle", "red mid", "red bottom", "red support", "blue team win rate"]
        csv_data = pd.DataFrame(columns=name, data=self.result_matching_data)
        csv_data.to_csv("MatchingResult.csv", encoding='utf-8')


matching_pool = MatchingPoolThread()
matching_pool.start()
# queue_order = random.sample(range(1,480423), 480422)
queue_order = random.sample(range(1, 131553), 131552)
for order in queue_order:
    apply_role = random.randint(1, 5)
    matching_pool.enter_pool(gold_summoner.ids(order), apply_role)
    if matching_pool.is_end:
        break
