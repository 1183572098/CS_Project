# -*- coding: utf-8 -*-
# @Time    : 2022/6/29 17:04
# @Author  : Jinyi Li
# @FileName: config.py
# @Software: PyCharm

import os
import csv


class Config(object):
    file_name = None

    def __init__(self):
        self.config = []
        work_path = os.path.dirname(os.path.abspath(__file__))
        parameter_file = csv.DictReader(open(self.file_name, encoding="utf-8-sig"))
        for role in parameter_file:
            self.config.append(dict(role))


class Matching(Config):

    def __init__(self):
        self.file_name = 'matching.csv'
        super(Matching, self).__init__()

    def value(self, time):
        for para in self.config:
            if int(para["time"]) >= int(time):
                return int(para["score"])

        return None


matching = Matching()


class SummonerIds(Config):
    def __init__(self):
        self.file_name = 'datasets/SummIds2016.csv'
        super(SummonerIds, self).__init__()

    def score(self, ids):
        for para in self.config:
            if int(para["SummonerId"]) == int(ids):
                return int(para["Score"])

    def ids(self, row):
        for para in self.config:
            if int(para["id"]) == int(row):
                return int(para["SummonerId"])


summoner = SummonerIds()


class GoldSummonerIds(Config):

    def __init__(self):
        self.file_name = 'datasets/GoldSummData2016.csv'
        super(GoldSummonerIds, self).__init__()

    def ids(self, row):
        for para in self.config:
            if int(para["id"]) == int(row):
                return int(para["SummonerId"])

    def score(self, ids):
        for para in self.config:
            if int(para["SummonerId"]) == int(ids):
                return int(para["Score"])

    def win_rate(self, ids):
        for para in self.config:
            if int(para["SummonerId"]) == int(ids):
                return float(para["WinRate"])


gold_summoner = GoldSummonerIds()
