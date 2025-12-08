team_name = 'Carson H'
strategy_name = 'Modified Pavlov'
strategy_description = 'Collude unless losing, then betray; betray on last round.'
    
def move(my_history, their_history, my_score, their_score):
    ''' Arguments accepted: my_history, their_history are strings.
    my_score, their_score are ints.'''

    #Modified Pavlov Strat:
    last_score = 0
    if last_score > my_score or my_score < 0 or len(my_history) == 199:
        move = 'b'
    else:
        move = 'c'
    last_score = my_score
    return move    