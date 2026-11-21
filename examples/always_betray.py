# An example strategy. Read it for ideas, but write your own in the
# "strategies" folder (start from strategies/demo_strategy.py).

strategy_name = 'Always Betray'

# Betrays every single round, no matter what.

def move(my_history, their_history, my_score, their_score):
    return 'b'
