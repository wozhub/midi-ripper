#!/usr/bin/env python3

from os.path import dirname, realpath
from time import sleep

from midi_tools import play_note


EMPTY_WAV = "{}/empty.wav".format(dirname(realpath(__file__)))
WAIT_START = 0.002
WAIT_END = 0.002


def rip_note(sound_device, sound_config, midi_device, midi_config, midi_note, midi_vel):
    """
        Given a midi_note, plays it and saves input audio it to a file
    """

    record_time = midi_config['duration'] * sound_config['sample-rate']
    record = sound_device.rec(record_time) # Begin recording
    sleep(WAIT_START)
    # TODO: quizá play_note podría tomar como argumento MIDI-CONFIG
    play_note(midi_device, midi_config['channel'], midi_note, midi_vel, midi_config['sustain-time'])
    #sleep(m_duration)
    sound_device.wait()
    #sleep(WAIT_END)
    return record
