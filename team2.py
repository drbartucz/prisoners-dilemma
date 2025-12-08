####
# Each team's file must define four tokens:
#     team_name: a string
#     strategy_name: a string
#     strategy_description: a string
#     move: A function that returns 'c' or 'b'
####

team_name = 'Nikolai' # Only 10 chars displayed.
strategy_name = 'Douglas, the Gnome of ...something'
strategy_description = 'Decides based on gut-feelings and however they\'re feeling that day (probabilities)'
    
def move(my_history, their_history, my_score, their_score):
    ''' Arguments accepted: my_history, their_history are strings.
    my_score, their_score are ints.'''
    
    import random
    
    #Douglas gets suspicious if the other person does the same thing for the past couple of turns, so they switch their strategy to avoid losing that much 
    if len(their_history) > 4:
        if "b" not in their_history[-5]:
            return "b"
        else:
            return "c"
    
    if len(my_history) > 0: #Douglas hates betrayals, so they'll betray the other person a bunch of times after Douglas gets betrayed, unless it was just a one time thing and Douglas also betrayed them
        if my_history[-1] == "c" and their_history[-1] == "b": #Here, Douglas is very mad
            return "c"
        elif my_history[-1] == "b" and their_history[-1] == "b":
            if len(my_history) > 1:
                if their_history[-2] == "c":
                    return "b"
                else:
                    return "c"
            else:
                return "c"
    
    if my_score >= 20: #If Douglas is winning by a lot, they'll be excessively confident in themselves, so they'll only betray to get back at the other person
        return "c"
    elif my_score <= -150: #If Douglas is losing by a lot, they'll be very sad, so they'll just collude to prevent losing more points
        return "b"
    
    if len(my_history) < 10: #Sometimes, Douglas likes variety
        if "c" not in my_history:
            return "c"
        elif "b" not in my_history:
            return "b"
    else:
        if "c" not in my_history[-10]:
            return "c"
        elif "b" not in my_history[-10]:
            return "b"
    
    total_weight = 0
    betray_weight = 0
    #Will choose based on a weighted average based on random numbers and historical data; Douglas loves history
    #Basically, the closer the betray weight is to the total weight, the more likely it is to betray
    
    #Firstly, Douglas has to have breakfast, but sometimes, the breakfast isn't that good, and on some days, the breakfast is really, really bad.
    #If the breakfast is bad, Douglas is more likely to betray, and vise versa
    day_week = random.randint(1,7)
    total_weight += 7
    day_weight = 0
    if day_week == 1:
        day_weight = random.randint(0,2)
    elif day_week == 2:
        day_weight = random.randint(6,7)
    elif day_week == 3:
        day_weight = random.randint(2,5)
    elif day_week == 4:
        day_weight = random.randint(1,6)
    elif day_week == 5:
        day_weight = random.randint(3,5)
    elif day_week == 6:
        day_weight = random.randint(5,6)
    elif day_week == 7:
        day_weight = random.randint(1,3)
    betray_weight += day_weight
    
    #Does Douglas have boring paperwork to do? If he does, add one to the betray weight
    paper_chance = random.randint(1,100)
    total_weight += 1
    paper_weight = 0
    if paper_chance < 90:
        paper_weight += 1
    betray_weight += paper_weight
    
    #Finally, does Douglas have the time to do their favorite hobby—counting the number of bugs on their mushroom house (the record is two!)
    #If they don't, add 5 to the betray weight (they're very serious about their hobby)
    bug_chance = random.randint(1,2)
    total_weight += 5
    bug_weight = 0
    if bug_chance == 1:
        bug_weight += 5
    betray_weight += bug_weight
    
    #Betray calculations; Douglas is okay at math
    betray_ratio =  betray_weight/total_weight
    if random.random() > betray_ratio:
        return "c"
    else:
        return "b"
    
def test_move(my_history, their_history, my_score, their_score, result):
    '''calls move(my_history, their_history, my_score, their_score)
    from this module. Prints error if return value != result.
    Returns True or False, dpending on whether result was as expected.
    '''
    real_result = move(my_history, their_history, my_score, their_score)
    if real_result == result:
        return True
    else:
        print("move(" +
            ", ".join(["'"+my_history+"'", "'"+their_history+"'",
                       str(my_score), str(their_score)])+
            ") returned " + "'" + real_result + "'" +
            " and should have returned '" + result + "'")
        return False

if __name__ == '__main__':
     
    # Test 1: Betray on first move.
    if test_move(my_history='',
              their_history='', 
              my_score=0,
              their_score=0,
              result='b'):
         print ('Test passed')
     # Test 2: Continue betraying if they collude despite being betrayed.
    test_move(my_history='bbb',
              their_history='ccc', 
              # Note the scores are for testing move().
              # The history and scores don't need to match unless
              # that is relevant to the test of move(). Here,
              # the simulation (if working correctly) would have awarded 
              # 300 to me and -750 to them. This test will pass if and only if
              # move('bbb', 'ccc', 0, 0) returns 'b'.
              my_score=0, 
              their_score=0,
              result='b')