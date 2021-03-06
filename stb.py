#!/usr/bin/python3
# Shut The Box analysis
# https://en.wikipedia.org/wiki/Shut_the_Box
# Bart Massey

# Monte Carlo and search-based analysis of Shut The Box.
# Uses digital scoring on the 1..9 board.

import random
import argparse
from math import floor, log10

from choices import *

# Find the digital score for the current digits.
def calc_score(cur):
    # Put the digits in order.
    digits = sorted(list(cur))
    # Do a running sum.
    t = 0
    for d in digits:
        t = t * 10 + d
    return t

# Play out a game using the given chooser function at each
# step.  Return the game score. A chooser function takes the
# current board and a list of choices and returns a specific
# choice.
def play(chooser):
    # Start with all digits available.
    cur = set(range(1, 10))

    # Run until stuck or no digits left.
    while cur:
        # Roll the dice.
        roll = random.randrange(1, 7) + random.randrange(1, 7)
        # Get the available choices.
        moves = choices(cur, roll)
        # If there are no choices, the game is over.
        if not moves:
            break
        # Let the chooser pick.
        move = chooser(cur, moves)
        # Get rid of the chosen digits for next round.
        cur -= move

    # Return the calculated score.
    return calc_score(cur)

# Pick a choice at random.
def choose_random(cur, moves):
    return random.choice(moves)

# Pick a choice which minimizes the number
# of digits removed, then breaks ties by
# maximizing the digits removed.
def choose_heur(cur, moves):
    # Don't know what to return when no choices.
    assert len(moves) > 0

    # Find all the minimum-length choices.
    lens = {len(m) for m in moves}
    minl = min(lens)
    shortmoves = [m for m in moves if len(m) == minl]

    # Select the largest-digits choice.
    cmoves = canon_choices(shortmoves, reverse=True)
    return set(cmoves[0])

# Process arguments.
parser = argparse.ArgumentParser(description='Play Shut The Box.')
parser.add_argument('--ngames', '-n', type=int,
                    default=10000, help='number of games for MC play')
choosers = {
    "heur" : choose_heur,
    "random" : choose_random,
}
# https://stackoverflow.com/a/27529806
parser.add_argument('--chooser', '-c',
                    type=str, choices=choosers.keys(),
                    default="heur", help='chooser for moves')
parser.add_argument('--graph', '-g',
                    action="store_true", help='show histogram')
args = parser.parse_args()
ngames = args.ngames
chooser = choosers[args.chooser]
show_hist = args.graph

# Set up stats.
wins = 0
maxs = 0
# XXX The minimum can never be larger than this.
mins = 123456789
tot = 0
nbins = 20
hist = [0] * nbins

# Play many games and maintain the stats.
for _ in range(ngames):
    score = play(chooser)
    if score == 0:
        wins += 1
    mins = min(mins, score)
    maxs = max(maxs, score)
    tot += score
    bin = floor(nbins * log10(score + 1) / 9)
    hist[bin] += 1

# Display the stats.
print("wins", wins)
print("min", mins)
print("max", maxs)
print("mean", tot / ngames)
    
# Display the histogram.
if show_hist:
    for b in range(1, len(hist)):
        i = 10.0 ** ((b - 1) / nbins)
        n = 10 * hist[b] * nbins // ngames
        print("{:3.2f} {}".format(i, '*' * n))
