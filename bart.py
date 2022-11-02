import random
from config import *

def burst_or_not(blow_num):
    lst = [0,1]
    deliminator = bart_max_balloon_capacity + 1 - blow_num
    prob = 1 / deliminator
    output = random.choices(lst,weights=(1-prob,prob),k=1)[0]
    return output