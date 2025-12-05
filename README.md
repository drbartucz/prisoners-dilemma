# prisoners-dilemma
Prisoner's Dilemma Tournament

prisoners_dilemma.py automates competition among different strategies for the Iterative Prisoners Dilemma, the canonical game of game-theory.

Each strategy is pitted against each other strategy for 100 to 200 rounds.
The results of all previous rounds within the round are known to both players. 

individuals can start as team 0 and test their program by running team0.py
when their strategy is ready, run prisoners_dilemma.py with all the examples and team0
play_tournament([team0, team1, team2]) executes a tournament and writes to tournament.txt

When all strategies are ready, each team's strategy should be moved into their assigned Python file, team##.py and play_tournament should be run with just player teams and no examples.

