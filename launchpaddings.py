from mididings import *
from launchpad_utils import *

config(
    backend='jack-rt',
    client_name='launchpad',
    in_ports=[
        'Pad Keys',  # Signal from the Launchpad
    ],
    out_ports=[
        'To Pad',
        'To PC',
    ]
)


# FROM PAD TO PC

# First the controls

active = 0
muted = 127

UpperRow = (Filter(CTRL) >> CtrlValueFilter(127) >>
            NoteOn(EVENT_CTRL, EVENT_CTRL) >> Velocity(-FirstCtrl))
# Use controls on upper row, what matters is event VALUE


dMap = {
    0: (green, 0, active),
    1: (red, -16, muted),
    2: (green, -16, active),
    3: (red, -32, muted),
    4: (green, -32, active),
    5: (red, -48, muted),
    6: (green, -48, active),
    7: (red, -64, muted),
}

# The even rows activate (green), the odd rows mute (red) patterns 0-31
# Moreover, the Pad keys light up with the right colors
MapCtrl32 = [RowFilter(k) >> [Velocity(fixed=v[0]) >> Port(1),  # color to Pad
             ~OnlyRight >> Transpose(v[1]) >> Ctrl(EVENT_NOTE, v[2])
             >> Port(2),  # ctrl to PC
             ] for k, v in list(dMap.items())]


# I would like the right keys to activate/mute entire groups (rows) of patterns:

def EntireRow(ro):
    "Sends all notes of given row"
    return [SquareKey(ro, i) for i in longside]

ToEntireRow = [RowFilter(i) % EntireRow(i) for i in side]

FullControl = (OnlyRight % ToEntireRow >> MapCtrl32 >>
              (CtrlFilter(7) % Ctrl(8, EVENT_VALUE)))
# this last thing as ctrl 7 mutes channel!
# This is our final function Pad -> PC.

# KEYBOARD MODE

cVec = [  # row colors for full keyboard (useful also in EQ, mixer...)
    color(0, 2),
    red,
    color(1, 3),
    color(2, 3),
    yellow,
    color(3, 2),
    color(3, 1),
    green,
]

hVec = [  # row colors for half keyboard (useful also in EQ, mixer...)
    red,
    orange,
    yellow,
    green,
    red,
    orange,
    yellow,
    green,
]


def Keyboard(tonic, scale, lower, upper, octaves, coloring):
    return [RowFilter(i) >> [Velocity(fixed=coloring[i]) >> Port(1), ~OnlyRight
            >> Transpose(tonic + (octaves * Octave) - (4 * i))
            >> MakeScale(tonic, scale)
            >> Port(2), ] for i in range(lower, upper)]

HalfHalf = KeySplit(64, FullControl, Keyboard(A, Minor, 4, 8, -2, hVec))

# FROM PC TO PAD

# I send notes from my DAW in a more understandable way, both for velocities
# and notes. This translates them into the right language for the Pad.

PlaceMap = [KeyFilter(C + (i * Octave), C + (i * Octave) + 8)
            >> Transpose(88 - (i * 28)) for i in side]
# This maps octaves 8-1 to rows 0-7, semitones to columns

LightMap = [VelocityFilter(i * 8, (i * 8) + 8)
            >> Velocity(fixed=color(i // 4, i % 4)) for i in range(0, 16)]
# This maps velocity intervals to colors - an 8-range of velocities is
# mapped to a color

PCToPad = Pass() >> LightMap >> PlaceMap
# This is our final function PC -> Pad
# pass is to overcome some kind of bug


# PORT ROUTING (see ports defined above)

PadFilter = PortFilter(1)
ControlFilter = PortFilter(2)
BeatFilter = PortFilter(3)
CandyFilter = PortFilter(4)

# SCENE STRUCTURE

# The control is handled by upper row
control = UpperRow >> SceneSwitch()


CtrlNoCandy = [PadFilter >> FullControl,  # from PAD goes to the PC
               BeatFilter >> Port(1) >> PCToPad,  # The beat goes the other
                                                  # way around
              ]

CtrlCandy = [PadFilter >> FullControl,
             CandyFilter >> Port(1) >> PCToPad,
            ]

HalfNoCandy = [PadFilter >> HalfHalf,
               BeatFilter >> Port(1) >> KeyFilter(lower='c4') >> PCToPad,
              ]

HalfCandy = [PadFilter >> HalfHalf,
             CandyFilter >> Port(1) >> PCToPad,
            ]

KeyNoCandy = PadFilter >> Keyboard(A, Minor, 0, 8, 0, cVec)

KeyCandy = [PadFilter >> Keyboard(A, Minor, 0, 8, 0, cVec),
            CandyFilter >> Port(1) >> PCToPad,
           ]

# The post is dummy, I just make sure everything is sent on Channel 1
post = Channel(1)  # Only channel where Pad receives (receives also on 3,
# but in a different way)

# Scenes I have implemented so far: only beat, both, only candy
# It's important to filter out what you don't use (or it goes
# to a wrong channel)
scenes = {
    #1:  Scene("Control", CtrlNoCandy),
    1: Scene("Control and Keyboard", HalfNoCandy),
    #3:  Scene("Keyboard", KeyNoCandy),
    #4:  Scene("Empty", KeyNoCandy),
    #5:  Scene("Control Candy", CtrlCandy),
    #6:  Scene("Control Keyboard Candy", HalfCandy),
    #7:  Scene("Keyboard Candy", KeyCandy),
    #8:  Scene("Empty", CtrlNoCandy), #Put here what you want!
}

# And...go!
run(
    control=None,
    pre=Pass(),
    post=post,
    scenes=scenes,
)
