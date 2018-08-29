#!/usr/bin/env python3
# coding: utf-8

# Midi
from mido import Message
from time import sleep

NOTAS = ['C', 'Csharp', 'D', 'Dsharp', 'E', 'F', 'Fsharp', 'G', 'Gsharp', 'A', 'Asharp', 'B']

ACORDES = {
    'maj': [0, 4, 7],
    'maj-inv': [-5, 0, 4],  # una inversion mas "abierta"
    'min': [0, 3, 7],
    'min-inv': [-5, 0, 3],
    'sus2': [0, 2, 7],
    'sus2-inv': [-5, 0, 2],
    'sus4': [0, 5, 7],
    'sus4-inv': [-5, 0, 5],
}


def play_chord(midi_out, note, chord, sustain):
    notes = [note+x for x in chord ]

    for n in notes:
        msg = Message('note_on', note=n, velocity=127)
        midi_out.send(msg)

    sleep(sustain)
    midi_out.reset()

    """ # no anda!
    for n in notes:
        Message('note_off', note=n, velocity=127)
        midi_out.send(msg)
    """

def play_note(midi_out, note, velocity, sustain):
    msg_on = Message('note_on', note=note, velocity=velocity)
    msg_off = Message('note_off', note=note, velocity=velocity)
    midi_out.send(msg_on)
    sleep(sustain)
    midi_out.send(msg_off)
