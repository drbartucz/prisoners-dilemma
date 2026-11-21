# An example strategy. Read it for ideas, but write your own in the
# "strategies" folder (start from strategies/demo_strategy.py).

strategy_name = 'Late Betrayer'

# Like Grudge Holder, but also starts betraying after 100 rounds no matter what.

def move(my_history, their_history, my_score, their_score):
    if 'b' in their_history or len(their_history) > 100:
        return 'b'
    else:
        return 'c'
