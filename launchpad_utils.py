#
# This file contains functions and constants to talk
# to and from a Novation Launchpad via MIDI.
#
# Created by paul for mididings.


from mididings import *


# MEASURES - constants useful for the Pad

side = list(range(0, 8))
longside = list(range(0, 9))
step = 16   # vertical gap on pad
FirstCtrl = 104   # ctrl of first toprow key


# COLORS
# Colors on the Launchpad are determined by event velocity/value.
# Each key can be lit with red or green light (or both),
# with brightness 0 (off) - 3 (max).

# For convenience, define also the constants:

black = 4  # better not to use zero
red = 3
orange = 19
green = 48
yellow = 51  # better not to use 127

# If you want a darker variant of the above, use fractions (thirds).
# For example, green*2/3 is darker green. (Not for orange!)


def color(g, r):
    "This gives the Launchpad color given the amount of green and red."
    if g + r == 0:
        return black  # not zero
    else:
        return (16 * g) + r


# KEYS
# Each key on the Launchpad is activated by a MIDI event.
# The square keys and the right keys are notes,
# the top keys are control events.


# Rows and columns given the keys (starting from 0)

def row(x):
    "This tells the row of the event (square or right)"
    return x // step


def column(x):
    "This tells us the column of event (right = 8)"
    return x % step


def topcol(x):
    "The same as colums, but for the top row"
    return x - FirstCtrl


# Now the inverses: functions that point exactly to a key on the Launchpad

def right(ro):
    "This gives the note of a right key at position ro"
    return (ro * step) + 8


def square(ro, col):
    "This gives the note of a square key at position ro,col"
    return (ro * step) + col


def top(col):
    "This gives the ctrl of a top key at position col"
    return col + FirstCtrl


# KEY FILTERS

# First filters for notes from square, top, and right keys.

OnlySquare = Filter(NOTE) >> KeyFilter(notes=[square(i, j)
             for i in side for j in side])

OnlyRight = KeyFilter(notes=[right(i) for i in side])

OnlyTop = Filter(CTRL) >> CtrlFilter(FirstCtrl + i for i in side)


# Now filters for rows, colums, and single keys.

def RowSqFilter(ro):
    "This selects only notes from specified row"
    return KeyFilter(ro * step, right(ro))  # no right


def RowFilter(ro):
    "This selects only notes from specified row"
    return KeyFilter(ro * step, right(ro) + 1)  # also right


def ColumnFilter(col):
    "This selects only notes from specified column"
    return KeyFilter(notes=[square(i, col) for i in side])


def TopFilter(col):
    "This selects only specified key from top row"
    return CtrlFilter(top(col))


def RightFilter(ro):
    "This selects only specified key from right"
    return KeyFilter(right(ro))


def SquareFilter(ro, col):
    "This selects only specified key from square"
    return KeyFilter(square(ro, col))


# KEY GENERATORS

def SquareKey(ro, col):
    "This creates square note with given row and column"
    return Key(square(ro, col))


def RightKey(ro):
    "This creates right note with given row"
    return Key(right(ro))


def TopKey(col, val):
    "This creates top ctrl with given column"
    return Ctrl(top(col), val)


# NOTES

A = 21
B = 23
C = 24
D = 26
E = 28
F = 29
G = 31

Octave = 12  # semitones

minors = {  # scale
    0: 0,  # interval in semitones
    1: 2,
    2: 3,
    3: 5,
    4: 7,
    5: 8,
    6: 10,
    7: 12,
}

minharms = {  # scale
    0: 0,  # interval in semitones
    1: 2,
    2: 3,
    3: 5,
    4: 7,
    5: 8,
    6: 10,
    7: 11,  # harmonic
}


majors = {
    0: 0,
    1: 2,
    2: 4,
    3: 5,
    4: 7,
    5: 9,
    6: 11,
    7: 12,
}

dorics = {
    0: 0,
    1: 2,
    2: 3,
    3: 5,
    4: 7,
    5: 9,
    6: 10,
    7: 12,
}

phrygians = {
    0: 0,
    1: 1,
    2: 3,
    3: 5,
    4: 7,
    5: 8,
    6: 10,
    7: 12,
}

# I only use these scales - feel free to add your own!

# Now the same thing, but to feed into Transpose:
Minor = [minors[i] - i for i in side]
MinHarm = [minharms[i] - i for i in side]
Major = [majors[i] - i for i in side]
Doric = [dorics[i] - i for i in side]
Phrygian = [phrygians[i] - i for i in side]


# How to use it in practice:
def OctFilter(col, tonic):
    return KeyFilter(notes=[(tonic + col + (i * Octave)) for i in longside])


def MakeScale(tonic, scale):
    return [OctFilter(i, tonic) >> Transpose(scale[i]) for i in side]