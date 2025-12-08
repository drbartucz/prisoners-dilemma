team_name = 'Carson H'
strategy_name = 'Modified Pavlov'
strategy_description = 'Collude unless losing, then betray; betray on last round.'
    
def move(my_history, their_history, my_score, their_score):
    ''' Arguments accepted: my_history, their_history are strings.
    my_score, their_score are ints.'''

    #Modified Pavlov Strat:
    alternate = True
    for i in range(1, len(their_history)):
        if their_history[i] == their_history[i-1]:
            alternate = False
    if len(their_history) == 0 or their_history[-1] == 'c':
        return 'c'
    elif alternate == True or 'b' in their_history[-20:-1]:
        return 'b'
    else:
        return 'b'
    
    '''const winner = yay!!'''