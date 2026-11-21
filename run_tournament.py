'''Prisoner's Dilemma tournament.

Run this file to play every strategy against every other strategy:

    python run_tournament.py                  strategies + examples (for practice)
    python run_tournament.py --no-examples    only "strategies", without the demo (the real thing)
    python run_tournament.py --check          only check the files, don't play
    python run_tournament.py --seconds 120    stretch the show out to about 2 minutes
    python run_tournament.py --seconds 0      no pauses, finish as fast as possible
    python run_tournament.py some_folder      play the strategies in other folder(s)

Every .py file in the folder is one player, whatever the file is called.
Each file needs:

    team_name = 'Something unique'
    def move(my_history, their_history, my_score, their_score):  # returns 'c' or 'b'

The standings update on screen after every game and are saved to results.txt.
'''
import argparse
import concurrent.futures
import contextlib
import datetime
import importlib.util
import io
import itertools
import os
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ----------------------------------------------------------------------------
# Settings you might want to change
# ----------------------------------------------------------------------------
# Years in prison for one round - FEWER is better.
BOTH_COLLUDE = 1        # 'c' vs 'c'  - you both stay quiet
I_BETRAY = 0            # 'b' vs 'c'  - you betray someone who trusted you
I_AM_BETRAYED = 5       # 'c' vs 'b'  - you trusted someone who betrayed you
BOTH_BETRAY = 3         # 'b' vs 'b'  - you betray each other
# A move that crashes, or isn't 'c' or 'b', counts as 'c' AND costs this:
BAD_MOVE = 5

# Each pair of players meets this many times, so luck matters less.
GAMES_PER_PAIR = 3

# A file whose code runs for longer than this in the pre-start check is left out.
STUCK_AFTER_SECONDS = 5

# Each game lasts a random number of rounds, so nobody knows which is the last.
MIN_ROUNDS = 100
MAX_ROUNDS = 200

DEMO_FILENAME = 'demo_strategy.py'
DEMO_NAME = 'Demo Strategy'
MAX_NAME_LENGTH = 24
RESULTS_FILENAME = 'results.txt'

HERE = Path(__file__).resolve().parent
SCORES = {('c', 'c'): (BOTH_COLLUDE, BOTH_COLLUDE),
          ('c', 'b'): (I_AM_BETRAYED, I_BETRAY),
          ('b', 'c'): (I_BETRAY, I_AM_BETRAYED),
          ('b', 'b'): (BOTH_BETRAY, BOTH_BETRAY)}


class Player:
    def __init__(self, name, file, move, source):
        self.name = name
        self.file = file            # e.g. 'strategies/maria.py'
        self.move = move
        self.source = source
        self.total = 0.0            # sum of years-per-round over games played
        self.games = 0
        self.bad_moves = 0
        self.first_error = ''
        self.versus = {}            # opponent Player -> my years per round in each game

    @property
    def average(self):
        return self.total / self.games if self.games else 0.0


# ----------------------------------------------------------------------------
# Loading and checking the strategy files
# ----------------------------------------------------------------------------
def simplify(name):
    '''"Demo  Strategy", "demo_strategy" and "DEMOSTRATEGY" all count as the same name.'''
    return re.sub(r'[\W_]+', '', name).casefold()


def describe_error(error):
    return '{}: {}'.format(type(error).__name__, error)


def is_stuck(path):
    '''Try the file out in a separate Python, which can be stopped if it never finishes.'''
    try:
        subprocess.run([sys.executable, str(Path(__file__).resolve()), '--probe', str(path)],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=STUCK_AFTER_SECONDS)
    except subprocess.TimeoutExpired:
        return True
    return False


def probe(path):
    '''Runs inside that separate Python: load one file and give it plenty of rounds.'''
    spec = importlib.util.spec_from_file_location('probe', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for opponent in ('c', 'b', 'cb', 'ccb', 'random'):
        mine = theirs = ''
        for i in range(MAX_ROUNDS):
            try:
                answer = module.move(mine, theirs, i, i)
            except Exception:
                answer = 'c'
            mine += answer if answer in ('c', 'b') else 'c'
            theirs += random.choice('cb') if opponent == 'random' else opponent[i % len(opponent)]


def load_strategies(folders, skip_demo=False):
    '''Return (players, problems, warnings). Files with problems do not play.'''
    players, problems, warnings = [], [], []
    paths = []
    for folder in folders:
        if not folder.is_dir():
            problems.append((str(folder), 'this folder does not exist'))
            continue
        paths += [(folder, number, path) for number, path in enumerate(sorted(folder.glob('*.py')))
                  if not path.name.startswith('_')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        stuck = list(pool.map(is_stuck, [path for _, _, path in paths]))

    for (folder, number, path), file_is_stuck in zip(paths, stuck):
        label = folder.name + '/' + path.name
        if file_is_stuck:
            problems.append((label, 'the code ran for more than {} seconds without finishing - '
                             'look for a loop that never ends'.format(STUCK_AFTER_SECONDS)))
            continue
        try:
            source = path.read_text(encoding='utf-8', errors='replace')
            spec = importlib.util.spec_from_file_location(
                'strategy_{}_{}'.format(simplify(folder.name), number), path)
            module = importlib.util.module_from_spec(spec)
            with contextlib.redirect_stdout(io.StringIO()):
                spec.loader.exec_module(module)
        except KeyboardInterrupt:
            raise
        except BaseException as error:     # includes SyntaxError and exit()
            line = getattr(error, 'lineno', None)
            where = ' (line {})'.format(line) if line else ''
            problems.append((label, 'Python could not run this file{} - {}'.format(
                where, describe_error(error))))
            continue

        name = getattr(module, 'team_name', None)
        move = getattr(module, 'move', None)
        if not isinstance(name, str) or not name.strip():
            problems.append((label, "needs a line like  team_name = 'Your Name'"))
            continue
        if not callable(move):
            problems.append((label, 'needs a function called move()'))
            continue
        name = ' '.join(name.split())
        if len(name) > MAX_NAME_LENGTH:
            warnings.append((label, 'team_name is long, so it was cut to "{}"'.format(
                name[:MAX_NAME_LENGTH])))
            name = name[:MAX_NAME_LENGTH].strip()
        players.append(Player(name, label, move, source))

    # The demo file and the demo name belong together, and to nobody else.
    kept = []
    for player in players:
        is_demo_file = Path(player.file).name.casefold() == DEMO_FILENAME
        is_demo_name = simplify(player.name) == simplify(DEMO_NAME)
        if is_demo_file and not is_demo_name:
            problems.append((player.file, 'team_name was changed to "{}" but the file is still '
                             'called {} - rename the file'.format(player.name, DEMO_FILENAME)))
        elif is_demo_file and skip_demo:
            pass                        # the demo sits out the real tournament
        elif is_demo_name and not is_demo_file:
            problems.append((player.file, 'the file was renamed but team_name is still '
                             '"{}" - change team_name'.format(player.name)))
        else:
            kept.append(player)

    # Every name must be unique.
    by_name = {}
    for player in kept:
        by_name.setdefault(simplify(player.name), []).append(player)
    players = []
    for group in by_name.values():
        if len(group) > 1:
            for player in group:
                others = ', '.join(p.file for p in group if p is not player)
                problems.append((player.file, 'team_name "{}" is also used by {} - names must '
                                 'be different'.format(player.name, others)))
        else:
            players.append(group[0])

    # Things worth knowing about, but which don't stop a strategy from playing.
    demo_code = [strip_name_line(p.source) for p in players
                 if Path(p.file).name.casefold() == DEMO_FILENAME]
    for player in players:
        if demo_code and Path(player.file).name.casefold() != DEMO_FILENAME \
                and strip_name_line(player.source) == demo_code[0]:
            warnings.append((player.file, 'the code is still the same as the demo strategy'))
        for mine, theirs in [('', ''), ('c', 'b'), ('b', 'c'), ('cbcbb', 'bbccb')]:
            answer, error = ask(player, mine, theirs, 0, 0)
            if error:
                situation = 'in the first round' if not mine else \
                    'after I played {!r} and they played {!r}'.format(mine, theirs)
                warnings.append((player.file, 'move() gave a bad answer {} - {}'.format(
                    situation, error)))
                break
    return players, problems, warnings


def strip_name_line(source):
    lines = [line.strip() for line in source.splitlines()]
    return [line for line in lines if line and not line.startswith('team_name')]


# ----------------------------------------------------------------------------
# Playing
# ----------------------------------------------------------------------------
def ask(player, my_history, their_history, my_score, their_score):
    '''Ask a player for a move. Return (move, error); error is '' if all is well.'''
    try:
        with contextlib.redirect_stdout(io.StringIO()):     # hide any print()s
            answer = player.move(my_history, their_history, my_score, their_score)
    except Exception as error:
        return 'c', 'crashed with ' + describe_error(error)
    if isinstance(answer, str) and answer.strip().lower() in ('c', 'b'):
        return answer.strip().lower(), ''
    return 'c', "returned {!r} instead of 'c' or 'b'".format(answer)


def play_game(player1, player2):
    '''Play one game of many rounds. Return a dictionary describing it.'''
    rounds = random.randint(MIN_ROUNDS, MAX_ROUNDS)
    history1 = history2 = ''
    score1 = score2 = 0
    for _ in range(rounds):
        move1, error1 = ask(player1, history1, history2, score1, score2)
        move2, error2 = ask(player2, history2, history1, score2, score1)
        points1, points2 = SCORES[move1, move2]
        for player, error in ((player1, error1), (player2, error2)):
            if error:
                player.bad_moves += 1
                player.first_error = player.first_error or error
        score1 += BAD_MOVE if error1 else points1
        score2 += BAD_MOVE if error2 else points2
        history1 += move1
        history2 += move2

    game = {'players': (player1, player2), 'rounds': rounds,
            'per_round': (score1 / rounds, score2 / rounds),
            'histories': (history1, history2)}
    for me, them, mine in ((player1, player2, score1), (player2, player1, score2)):
        me.total += mine / rounds
        me.games += 1
        me.versus.setdefault(them, []).append(mine / rounds)
    return game


def standings(players):
    '''Fewest years first. Anyone who hasn't played yet goes at the bottom.'''
    return sorted(players, key=lambda p: (p.games == 0, p.average, p.name.casefold()))


# ----------------------------------------------------------------------------
# Showing results
# ----------------------------------------------------------------------------
def leaderboard_lines(players, previous_ranks=None, limit=None):
    lines = ['       #  {:<{w}}  {:>11}  {:>5}'.format('Player', 'Years/round', 'Games', w=MAX_NAME_LENGTH),
             '      --  {}  {}  {}'.format('-' * MAX_NAME_LENGTH, '-' * 11, '-' * 5)]
    ranked = standings(players)
    for rank, player in enumerate(ranked[:limit], start=1):
        arrow = ' '
        if previous_ranks and player in previous_ranks:
            arrow = '▲' if rank < previous_ranks[player] else \
                    '▼' if rank > previous_ranks[player] else ' '
        lines.append('   {} {:>3}  {:<{w}}  {:>11.2f}  {:>5}'.format(
            arrow, rank, player.name, player.average, player.games, w=MAX_NAME_LENGTH))
    if limit and len(ranked) > limit:
        lines.append('         ... and {} more (see {})'.format(len(ranked) - limit, RESULTS_FILENAME))
    return lines


def game_summary(game):
    (p1, p2), (s1, s2) = game['players'], game['per_round']
    return '{} ({:.2f})  vs  {} ({:.2f})   {} rounds'.format(p1.name, s1, p2.name, s2, game['rounds'])


def draw_live(players, game, done, total, previous_ranks):
    '''Redraw the whole screen with the current standings.'''
    width, height = shutil.get_terminal_size((100, 40))
    bar_width = 30
    filled = bar_width * done // total
    lines = ['',
             "   PRISONER'S DILEMMA TOURNAMENT  -  fewest years in prison wins",
             '',
             '   Game {} of {}  [{}{}]'.format(done, total, '#' * filled, '.' * (bar_width - filled)),
             '   Last game: ' + game_summary(game),
             '']
    lines += leaderboard_lines(players, previous_ranks, limit=max(3, height - len(lines) - 5))
    text = '\x1b[H' + ''.join(line[:width - 1] + '\x1b[K\n' for line in lines) + '\x1b[J'
    sys.stdout.write(text)
    sys.stdout.flush()


def wrap(text, width=80):
    return [text[i:i + width] for i in range(0, len(text), width)] or ['']


def build_report(players, games, problems, warnings, status, total_games):
    ranked = standings(players)
    out = ["PRISONER'S DILEMMA TOURNAMENT",
           datetime.datetime.now().strftime('%A %d %B %Y, %H:%M'),
           '{} - {} of {} games played'.format(status, len(games), total_games),
           '',
           'FEWEST YEARS IN PRISON WINS.',
           'Years each round:  both collude {}   I betray, they collude {}'.format(BOTH_COLLUDE, I_BETRAY),
           '                   both betray {}    I collude, they betray {}'.format(BOTH_BETRAY, I_AM_BETRAYED),
           "                   crash or anything that isn't 'c' or 'b': {}".format(BAD_MOVE),
           'Every pair plays {} games of {} to {} rounds each.'.format(GAMES_PER_PAIR, MIN_ROUNDS, MAX_ROUNDS),
           "Years/round is the average over all of a player's games.",
           '', '=' * 80, 'LEADERBOARD', '=' * 80]
    out += leaderboard_lines(players)

    if problems:
        out += ['', '=' * 80, 'FILES THAT COULD NOT PLAY', '=' * 80]
        out += ['{}: {}'.format(file, message) for file, message in problems]
    if warnings:
        out += ['', '=' * 80, 'WARNINGS', '=' * 80]
        out += ['{}: {}'.format(file, message) for file, message in warnings]
    sloppy = [p for p in ranked if p.bad_moves]
    if sloppy:
        out += ['', '=' * 80, 'BAD MOVES (each one cost {} years)'.format(BAD_MOVE), '=' * 80]
        out += ['{} ({}): {} bad moves. The first one {}'.format(p.name, p.file, p.bad_moves, p.first_error)
                for p in sloppy]

    out += ['', '=' * 80, 'WHO IS WHO', '=' * 80]
    out += ['{:>3}  {:<{w}}  {}'.format(i, p.name, p.file, w=MAX_NAME_LENGTH) for i, p in enumerate(ranked, 1)]

    out += ['', '=' * 80, 'HEAD TO HEAD', '=' * 80,
            'Each row shows the years per round that player got against each opponent',
            '(the numbers across the top are the ranks from the leaderboard).', '']
    out.append(' ' * (MAX_NAME_LENGTH + 5) + ''.join('{:>7}'.format(i) for i in range(1, len(ranked) + 1)))
    for i, player in enumerate(ranked, 1):
        cells = ''.join('{:>7}'.format('-' if other is player else
                                       '{:.2f}'.format(sum(player.versus[other]) / len(player.versus[other]))
                                       if other in player.versus else '')
                        for other in ranked)
        out.append('{:>3}  {:<{w}}'.format(i, player.name, w=MAX_NAME_LENGTH) + cells)

    out += ['', '=' * 80, 'EVERY GAME, ROUND BY ROUND', '=' * 80,
            "Search for your name. c = collude, b = betray. The top line of each pair is",
            "the first player's moves and the bottom line is the second player's.", '']
    for game in sorted(games, key=lambda g: [p.name.casefold() for p in g['players']]):
        out.append(game_summary(game))
        first, second = (wrap(h) for h in game['histories'])
        for a, b in zip(first, second):
            out += ['  ' + a, '  ' + b, '']
    return '\n'.join(out) + '\n'


def save_report(path, *report_arguments):
    path.write_text(build_report(*report_arguments), encoding='utf-8')


def print_notes(title, notes):
    if notes:
        print('\n' + title)
        for file, message in notes:
            print('  {}: {}'.format(file, message))


# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Run a Prisoner's Dilemma tournament.")
    parser.add_argument('folders', nargs='*', help='folders of strategies (default: strategies and examples)')
    parser.add_argument('--no-examples', action='store_true', help='play only the strategies folder, and leave out the demo')
    parser.add_argument('--check', action='store_true', help="check the files but don't play")
    parser.add_argument('--seconds', type=float, default=10,
                        help='roughly how long the tournament should take on screen (default 10, 0 = no pauses)')
    parser.add_argument('--yes', action='store_true', help="don't wait for Enter before starting")
    parser.add_argument('--seed', type=int, help='make the random numbers repeatable')
    parser.add_argument('--probe', help=argparse.SUPPRESS)      # used by the pre-start check
    args = parser.parse_args()
    if args.probe:
        probe(args.probe)
        return 0

    for stream in (sys.stdout, sys.stderr):     # so names with accents or emoji can be printed
        with contextlib.suppress(Exception):
            stream.reconfigure(encoding='utf-8', errors='replace')
    if args.seed is not None:
        random.seed(args.seed)

    if args.folders:
        folders = [Path(folder).resolve() for folder in args.folders]
    elif args.no_examples:
        folders = [HERE / 'strategies']
    else:
        folders = [HERE / 'strategies', HERE / 'examples']

    print('\nChecking the strategy files...')
    keyboard, sys.stdin = sys.stdin, io.StringIO('')    # a strategy calling input() gets an error, not a wait
    players, problems, warnings = load_strategies(folders, skip_demo=args.no_examples)

    print("\nPRISONER'S DILEMMA TOURNAMENT")
    print('\n{} strategies ready to play:'.format(len(players)))
    for player in sorted(players, key=lambda p: p.name.casefold()):
        print('  {:<{w}}  {}'.format(player.name, player.file, w=MAX_NAME_LENGTH))
    print_notes('WARNINGS (these will still play):', warnings)
    print_notes('PROBLEMS (these will NOT play until they are fixed):', problems)

    if args.check:
        return 1 if problems else 0
    if len(players) < 2:
        print('\nAt least two strategies are needed to play.')
        return 1

    schedule = list(itertools.combinations(players, 2)) * GAMES_PER_PAIR
    random.shuffle(schedule)
    results_path = HERE / RESULTS_FILENAME
    live = sys.stdout.isatty()
    if live and not args.yes:
        try:
            sys.stdin = keyboard
            input('\nPress Enter to play {} games (or Ctrl+C to stop) '.format(len(schedule)))
        except (EOFError, KeyboardInterrupt):
            print()
            return 1
        finally:
            sys.stdin = io.StringIO('')
    if live:
        os.system('')                   # switches on screen control codes in Windows terminals
        sys.stdout.write('\x1b[2J')     # clear the screen
    else:
        print()

    pause = args.seconds / len(schedule)
    games = []
    previous_ranks = None
    last_save = 0
    status = 'FINAL RESULTS'
    try:
        for player1, player2 in schedule:
            current = '{} vs {}'.format(player1.file, player2.file)
            game = play_game(player1, player2)
            games.append(game)
            if live:
                draw_live(players, game, len(games), len(schedule), previous_ranks)
                previous_ranks = {p: rank for rank, p in enumerate(standings(players), 1)}
            else:
                print('Game {} of {}: {}'.format(len(games), len(schedule), game_summary(game)))
            if time.time() - last_save > 1:
                save_report(results_path, players, games, problems, warnings, 'IN PROGRESS', len(schedule))
                last_save = time.time()
            time.sleep(pause)
    except KeyboardInterrupt:
        status = 'STOPPED EARLY'
        print('\n\nStopped during the game {}.'.format(current))
        print('If it was stuck, one of those two strategies probably has a loop that never ends.')

    save_report(results_path, players, games, problems, warnings, status, len(schedule))
    if live and status == 'FINAL RESULTS':
        sys.stdout.write('\x1b[2J\x1b[H')
    print('\n   {} - {} games played\n'.format(status, len(games)))
    print('\n'.join(leaderboard_lines(players)))
    sloppy = [(p.file, '{} bad moves ({} years each). The first one {}'.format(p.bad_moves, BAD_MOVE, p.first_error))
              for p in standings(players) if p.bad_moves]
    print_notes('BAD MOVES:', sloppy)
    print_notes('DID NOT PLAY:', problems)
    print('\nFull details, including every game round by round, are in {}'.format(results_path))
    return 0


if __name__ == '__main__':
    sys.exit(main())
