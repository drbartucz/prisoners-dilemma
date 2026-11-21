# An example strategy. Read it for ideas, but write your own in the
# "strategies" folder (start from strategies/demo_strategy.py).

strategy_name = 'Grudge Holder'

# Colludes until the other player betrays even once. After that, betrays forever.

def move(my_history, their_history, my_score, their_score):
    if 'b' in their_history:
        return 'b'
    else:
        return 'c'
