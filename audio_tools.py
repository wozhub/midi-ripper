#!/usr/bin/env python3

from os.path import dirname, realpath
from time import sleep

# Audio
import sounddevice as SOUND_DEVICE


from midi_tools import play_note

# Config
from config import CONFIG


EMPTY_WAV = "{}/empty.wav".format(dirname(realpath(__file__)))
WAIT_START = 0.002
WAIT_END = 0.002

#print(SOUND_DEVICE.query_devices()[0].get('name'))
SOUND_DEVICES = SOUND_DEVICE.query_devices()
SOUND_DEVICES_NAMES = [x.get('name') for x in SOUND_DEVICES]
SOUND_DEVICES_LIST = ["%d: %s" % (SOUND_DEVICES.index(x), x.get('name')) for x in SOUND_DEVICES]




def set_sounddevice():
    """  See if the requested sound device is available """
    if CONFIG is None:
        # TODO: Should raise error
        print("Must load config first!")
        return False

    if not CONFIG['sound-device']['name'] in SOUND_DEVICES_NAMES:
        print("SOUND DEVICE NOT AVAILABLE (%s)" % CONFIG['sound-device']['name'])
        return False

    SOUND_DEVICE.default.samplerate = CONFIG['sound-device']['sample-rate']
    SOUND_DEVICE.default.device = CONFIG['sound-device']['name']

# Implement through CONFIG
#    if ARGS.fix_audiolink:
#        SOUND_DEVICE.default.channels = 2  # Will save as ARGS.channels afterwards
#    else:
#        SOUND_DEVICE.default.channels = CONFIG['sound-device']['channels']
    # SOUND_DEVICE.default.dtype =

    return True


def rip_note(sound_device, sound_config, midi_device, midi_config, midi_note, midi_vel):
    """ Given a midi_note, plays it and saves input audio it to a file """

    record_time = midi_config['duration'] * sound_config['sample-rate']
    record = sound_device.rec(record_time) # Begin recording
    sleep(WAIT_START)
    # TODO: quizá play_note podría tomar como argumento MIDI-CONFIG
    play_note(midi_device, midi_config['channel'], midi_note, midi_vel, midi_config['sustain-time'])
    #sleep(m_duration)
    sound_device.wait()
    #sleep(WAIT_END)
    return record
