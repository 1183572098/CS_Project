# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.

from EloRating import matching_pool
from config import summoner
import random

queue_order = random.sample(range(1,480423), 480422)
for order in queue_order:
    role = random.randint(1, 5)
    matching_pool.enter_pool(summoner.ids(order), role)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
