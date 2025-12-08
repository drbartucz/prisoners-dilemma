team_name = 'Emily' # Only 10 chars displayed.
strategy_name = 'a_good_strategy'
strategy_description = 'betray if betrayed, always betray if alternating'

def move(my_history, their_history, my_score, their_score):
    ''' Arguments accepted: my_history, their_history are strings.
    my_score, their_score are ints.'''

    import random
    if len(my_history)==0: 
        return "c"
    else:
        revenge = False
        alternate = True
        for i in range(1, len(their_history)):
            if their_history[i] == their_history[i-1]:
                alternate = False
        if alternate == True and len(their_history) > 10:
            revenge = True
        elif my_history[-1] =='c' and their_history[-1] =='b':
            revenge = True
       
    if revenge == True:
        return 'b'
    if revenge == False:
        return 'c'