# An example strategy. Read it for ideas, but write your own in the
# "strategies" folder (start from strategies/demo_strategy.py).

strategy_name = 'Alternate'

# Colludes, betrays, colludes, betrays, ... ignoring the other player.

def move(my_history, their_history, my_score, their_score):
    # len(my_history) is the number of rounds played so far: 0, 1, 2, ...
    if len(my_history) % 2 == 0:
        return 'c'
    else:
        return 'b'
