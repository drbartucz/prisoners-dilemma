# An example strategy. Read it for ideas, but write your own in the
# "strategies" folder (start from strategies/demo_strategy.py).

team_name = 'Pattern Matcher'

# Looks for an earlier round that went the same way as the last round, and plays what the other player did in that earlier round. If there is none, it colludes unless it was just betrayed.

def move(my_history, their_history, my_score, their_score):
    if len(my_history) == 0:
        return 'c'

    last_me = my_history[-1]
    last_them = their_history[-1]

    # Look through every round before the last one.
    for i in range(len(my_history) - 1):
        if my_history[i] == last_me and their_history[i] == last_them:
            return their_history[i]

    if last_me == 'c' and last_them == 'b':
        return 'b'
    else:
        return 'c'
