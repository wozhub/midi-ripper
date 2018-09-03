#!/usr/bin/env python3

from os.path import dirname, realpath
from time import sleep

from midi_tools import play_note


EMPTY_WAV = "{}/empty.wav".format(dirname(realpath(__file__)))
WAIT_START = 0.002
WAIT_END = 0.002


def rip_note(sound_device, samplerate, m_port, m_note, m_vel, m_sustain, m_duration):
    """
        Given a midi_note, plays it and saves input audio it to a file
    """

    record = sound_device.rec(m_duration * samplerate) # Begin recording
    sleep(WAIT_START)
    play_note(m_port, m_note, m_vel, m_sustain)
    #sleep(m_duration)
    sound_device.wait()
    #sleep(WAIT_END)
    return record
