# =============================================================================
#  PRISONER'S DILEMMA - YOUR STRATEGY FILE
# =============================================================================
#
#  To enter the tournament:
#
#    1. Change team_name below to your name or your team's name.
#    2. Replace the code inside move() with your own strategy.
#    3. Rename this file to anything else ending in .py
#       (for example:  maria_and_sam.py).
#
#  You must do BOTH 1 and 3. The tournament will refuse a file that is still
#  called demo_strategy.py with a new name inside it, or a renamed file that
#  still says 'Demo Strategy'.
#
#  To test it, put your file in the "strategies" folder and run
#  run_tournament.py. See README.md for the full rules.
# =============================================================================

import random

team_name = 'Demo Strategy'


def move(my_history, their_history, my_score, their_score):
    '''Decide what to do this round. Must return 'c' (collude) or 'b' (betray).

    This function is called once per round. You get four pieces of information
    about the game so far against THIS opponent:

    my_history     what you did in each earlier round, as a string like 'ccbc'
    their_history  what the other player did in each earlier round, e.g. 'cbbc'
    my_score       your total years in prison so far in this game (fewer is better)
    their_score    the other player's total years in prison so far in this game

    In the first round both histories are empty: ''

    Handy things you can do with a history string:
        len(their_history)          how many rounds have been played
        their_history[-1]           what they did last round (not in round 1!)
        their_history[-3:]          what they did in the last three rounds
        their_history.count('b')    how many times they have betrayed
        'b' in their_history        True if they have ever betrayed
    '''

    # ----- The demo strategy: do whatever the other player has done most. -----
    # Replace everything from here to the end of the function with your idea.

    times_they_colluded = their_history.count('c')
    times_they_betrayed = their_history.count('b')

    if times_they_colluded > times_they_betrayed:
        return 'c'
    elif times_they_betrayed > times_they_colluded:
        return 'b'
    else:
        # It's a tie (this includes the very first round): pick at random.
        return random.choice(['c', 'b'])


# -----------------------------------------------------------------------------
# You don't need to change anything below. If you run THIS file by itself, it
# shows what your move() does in a few made-up situations - a quick way to see
# whether your code works before you play a whole tournament.
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    situations = [('', ''), ('c', 'c'), ('c', 'b'), ('ccc', 'cbb'), ('bbbb', 'cccc')]
    print('Testing', team_name)
    for mine, theirs in situations:
        result = move(mine, theirs, 0, 0)
        print('  I played', repr(mine), 'and they played', repr(theirs),
              '-> my next move is', repr(result))
        if result not in ('c', 'b'):
            print("    PROBLEM: move() has to return 'c' or 'b'.")
