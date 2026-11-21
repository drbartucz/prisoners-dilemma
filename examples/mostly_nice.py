# An example strategy. Read it for ideas, but write your own in the
# "strategies" folder (start from strategies/demo_strategy.py).

strategy_name = 'Mostly Nice'

# Betrays if betrayed in the last 10 rounds. Otherwise colludes 90% of the time and betrays 10% of the time, at random.

import random


def move(my_history, their_history, my_score, their_score):
    if 'b' in their_history[-10:]:      # [-10:] means "the last 10 rounds"
        return 'b'
    elif random.random() < 0.1:         # true about 10% of the time
        return 'b'
    else:
        return 'c'
