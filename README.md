# prisoners-dilemma
Prisoner's Dilemma Tournament

# Place each team's strategy in a file in the same directory as this file.
# Tournament results saved to tournament.txt in this directory.
#
# prisoners_dilemma.py automates competition among different strategies
# for the Iterative Prisoners Dilemma, the canonical game of game-theory.
# Each strategy is pitted against each other strategy for 100 to 200 rounds.
# The results of all previous rounds within the round are known
# to both players. 
#
# play_tournament([team0, team1, team2]) executes a tournament and writes to tournament.txt
#
# Each team's strategy should be coded in their assigned Python file, called a module.
# Each player should have their own .py file containing 
# three strings team_name, strategy_name, and strategy_description
# and a function move(my_history, their_history, my_score, their_score)
# 
# By default, when executing this file, [example0, example1, example2, example3] 
# play a tournament. To run the tournament of [team, team1, team1, example1]:
# scores, moves, reports = main_play([team1]*3+[example1])
# section0, section1, section2, section3 = reports
