# Prisoner's Dilemma Tournament

You are going to write a small Python strategy for a famous game, and then every
strategy in the class plays every other strategy. Whoever spends the least time
in prison wins.

## The game

Someone has stolen Mr. Bartucz's chocolate chip cookies. You and your partner
have been caught with crumbs on your shirts. You are questioned in separate
rooms and cannot talk to each other. Each of you has two choices:

- **Collude** (`'c'`) – stay quiet and stick with your partner.
- **Betray** (`'b'`) – tell on your partner to get a better deal for yourself.

How many years in prison you get depends on what you *both* chose:

|                    | They collude                          | They betray                           |
|--------------------|---------------------------------------|---------------------------------------|
| **You collude**    | You both get **1 year**               | You get **5 years**, they get 0       |
| **You betray**     | You get **0 years**, they get 5       | You both get **3 years**              |

Fewer years is better. (Yes, it is a harsh sentence. They were very good cookies.)

That is the dilemma: whatever your partner does, you personally do better by
betraying (0 years instead of 1, or 3 years instead of 5). But if you both
think that way you both get 3 years, when you could both have had 1.

## The tournament

One round would be a pure guess. So instead you play the same opponent
**100 to 200 rounds in a row**, and before each round you can see everything
that has happened so far in that game. Now your opponent can punish you for
betraying or reward you for colluding, and you can do the same to them.

- You play three games against every other strategy.
- Nobody knows exactly how many rounds a game will last.
- Your score is your average years in prison per round, over all your games.
  **The lowest score wins.**
- You are **not** trying to beat each opponent. You are trying to get the
  fewest years for yourself across the whole tournament. Those are not the
  same thing!

## How to enter

1. Download this project: on GitHub click the green **Code** button, then
   **Download ZIP**, and unzip it.
2. Open `strategies/demo_strategy.py`. Everything you need is in that one file.
3. Change `team_name = 'Demo Strategy'` to your name or team name.
4. Replace the code inside `move()` with your own idea.
5. Rename the file to something else ending in `.py`, such as `maria_and_sam.py`.
6. Upload that one file to the assignment.

You must change **both** the name inside the file and the name of the file.
A renamed file that still says `'Demo Strategy'`, or a file still called
`demo_strategy.py` with a new name inside, will not be allowed to play. Two
entries with the same `team_name` will not be allowed to play either.

## Writing your strategy

Your file needs a function called `move`. It is called once every round and it
must return `'c'` or `'b'`:

```python
def move(my_history, their_history, my_score, their_score):
    if 'b' in their_history:     # have they ever betrayed me?
        return 'b'
    return 'c'
```

| You are given   | What it is                                                     |
|-----------------|----------------------------------------------------------------|
| `my_history`    | Your moves so far in this game, as a string such as `'ccbc'`   |
| `their_history` | The other player's moves so far, such as `'cbbc'`              |
| `my_score`      | Your total years in prison so far in this game                 |
| `their_score`   | Their total years in prison so far in this game                |

In the first round both histories are the empty string `''`. This is the most
common mistake: `their_history[-1]` (their last move) crashes in round one
because there is no last move yet. Check `len(their_history) == 0` first.

If your code crashes, or returns anything other than `'c'` or `'b'`, that round
counts as colluding **and** you get 5 years for it.

The `examples` folder has nine small strategies you can read for ideas.

## Testing your strategy

Run your own file to see what it does in a few made-up situations:

```
python strategies/maria_and_sam.py
```

Then run a practice tournament against the demo and all the examples:

```
python run_tournament.py
```

The standings update on screen after every game. Afterwards open `results.txt`
and search for your name: it shows every game you played, round by round, so
you can see exactly where things went well or badly. If something is wrong with
your file, the tournament tells you what before it starts.

Doing well against the examples does not guarantee doing well against your
classmates, who may have very different ideas.

## Rules

- Your strategy may only use the four things `move()` is given. It may not read
  or change other files, other strategies, or the tournament program.
- `import random` is fine. Don't use anything that needs to be installed.
- Keep it quick: no waiting, no asking for input, no loops that never end.
  A file that runs for more than five seconds in the pre-start check is left out.

## Things to think about

- What should you do in the very first round, when you know nothing?
- If someone betrays you once, do you punish them forever, once, or not at all?
- What does your strategy do against someone who always betrays? Always colludes?
  Chooses at random? A copy of itself?
- Is it better to be nice or nasty? Predictable or unpredictable?

---

## For the teacher

Download the students' files from the LMS and drop them all into the
`strategies` folder. The file names don't matter, so whatever the LMS renames
them to is fine. Then:

| Command                                    | What it does                                             |
|--------------------------------------------|----------------------------------------------------------|
| `python run_tournament.py --check --no-examples` | Checks every file and lists problems, without playing |
| `python run_tournament.py --no-examples`   | The real tournament: only `strategies`, without the demo |
| `python run_tournament.py --no-examples --seconds 120` | Same, stretched to about two minutes for suspense |
| `python run_tournament.py`                 | Practice: `strategies` plus `examples`                   |
| `python run_tournament.py some_folder`     | Plays the strategies in any other folder                 |

- Files with problems (syntax errors, endless loops, missing or duplicate
  `team_name`, the demo name/filename rule) are listed before the start and left out. Fix them
  and run again, or press Enter to play without them.
- `results.txt` is rewritten as the tournament runs and holds the leaderboard,
  a head-to-head table and every game round by round. It is overwritten each
  run, so rename it if you want to keep one.
- Endless loops are normally caught before the start. If the tournament hangs
  anyway, press Ctrl+C: it reports which two files were playing and saves the
  results so far.
- `demo_strategy.py` plays in practice runs but sits out when you use
  `--no-examples`, so you can leave it in the folder.
- The years for each outcome, the number of rounds and the number of games per
  pair are at the top of `run_tournament.py`.
