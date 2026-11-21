# An example strategy. Read it for ideas, but write your own in the
# "strategies" folder (start from strategies/demo_strategy.py).

team_name = 'Copycat'

# Colludes in the first round, then copies whatever the other player did last round. (Game theorists call this one Tit for Tat.)

def move(my_history, their_history, my_score, their_score):
    if len(their_history) == 0:     # first round: nothing to copy yet
        return 'c'
    return their_history[-1]        # [-1] means "the most recent one"
