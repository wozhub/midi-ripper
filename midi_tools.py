#!/usr/bin/env python3
# coding: utf-8

# Midi
from mido import Message, open_output, get_output_names
from time import sleep

#from IPython import embed

# Config
from config import CONFIG

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

MIDI_DEVICE = None
MIDI_DEVICES_NAMES = get_output_names()
MIDI_DEVICES_LIST = ["%d: %s" % (MIDI_DEVICES_NAMES.index(x), x) for x in MIDI_DEVICES_NAMES]


def set_mididevice():
    """  See if requested MIDI DEVICE is available """
    global MIDI_DEVICE

    if not CONFIG['midi-device']['name'] in MIDI_DEVICES_NAMES:
        print("MIDI DEVICE NOT AVAILABLE (%s)" % CONFIG['midi-device']['name'])
        return False

    MIDI_DEVICE = open_output(CONFIG['midi-device']['name'])
    return True


def play_chord(midi_out, root_note, chord, sustain):
    """ Plays chords (multiple notes) """
    notes = [root_note+x for x in chord]

    for note in notes:
        msg = Message('note_on', note=note, velocity=127)
        midi_out.send(msg)

    sleep(sustain)
    midi_out.reset()

    """ # no anda!
    for n in notes:
        Message('note_off', note=n, velocity=127)
        midi_out.send(msg)
    """


def play_note(midi_out, channel, note, velocity, sustain):
    """ Plays notes """
    msg_on = Message('note_on', channel=channel, note=note, velocity=velocity)
    msg_off = Message('note_off', channel=channel, note=note, velocity=velocity)
    #msg_on = Message('note_on', note=note, velocity=velocity)
    #msg_off = Message('note_off', note=note, velocity=velocity)
    #embed()
    midi_out.send(msg_on)
    sleep(sustain)
    midi_out.send(msg_off)
