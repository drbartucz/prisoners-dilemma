# An example strategy. Read it for ideas, but write your own in the
# "strategies" folder (start from strategies/demo_strategy.py).

strategy_name = 'Retaliate'

# Colludes, except in the round right after it colluded and got betrayed.

def move(my_history, their_history, my_score, their_score):
    if len(my_history) == 0:        # first round
        return 'c'
    elif my_history[-1] == 'c' and their_history[-1] == 'b':
        return 'b'                  # I was just betrayed: get revenge once
    else:
        return 'c'
