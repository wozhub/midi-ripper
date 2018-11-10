#!/usr/bin/env python3

from os.path import dirname, realpath
from time import sleep

# Audio
import sounddevice as DEVICE


from midi import play_note

# Config
import config


EMPTY_WAV = "{}/empty.wav".format(dirname(realpath(__file__)))
WAIT_START = 0.002
WAIT_END = 0.002

#print(SOUND_DEVICE.query_devices()[0].get('name'))
DEVICES = DEVICE.query_devices()
DEVICES_NAMES = [x.get('name') for x in DEVICES]
DEVICES_LIST = ["%d: %s" % (DEVICES.index(x), x.get('name')) for x in DEVICES]


def load():
    """  See if the requested sound device is available """
    if config.CONFIG is None:
        # TODO: Should raise error
        print("Must load config first!")
        return False

    # TODO: What if soundcard is present but in other port? IE:  (hw:2,0) instead of (hw:1,0)
    if not config.CONFIG['sound']['device-name'] in DEVICES_NAMES:
        print("SOUND DEVICE NOT AVAILABLE (%s)" % config.CONFIG['sound']['device-name'])
        return False

    DEVICE.default.samplerate = config.CONFIG['sound']['sample-rate']
    DEVICE.default.device = config.CONFIG['sound']['device-name']
    DEVICE.default.channels = 1  # Will save as ARGS.channels afterwards

# Implement through config.CONFIG
#    if ARGS.fix_audiolink:
#        SOUND_DEVICE.default.channels = 2  # Will save as ARGS.channels afterwards
#    else:
#        SOUND_DEVICE.default.channels = config.CONFIG['sound']['channels']
    # SOUND_DEVICE.default.dtype =

    return True


def rip_note(sound_device, sound_config, midi_device, midi_config, midi_note, midi_vel):
    """ Given a midi_note, plays it and saves input audio it to a file """

    record_time = midi_config['duration'] * sound_config['sample-rate']
    record = sound_device.rec(record_time) # Begin recording
    sleep(WAIT_START)
    # TODO: quizá play_note podría tomar como argumento MIDI-config.CONFIG
    play_note(midi_device, midi_config['channel'], midi_note, midi_vel, midi_config['sustain-time'])
    #sleep(m_duration)
    sound_device.wait()
    #sleep(WAIT_END)
    return record


def check_volume(record):
    """ Checks for expected volume """
    peak = max(abs(record.min()), record.max())

    # over-volume
    if peak > config.CONFIG['sound']['max-peak-volume']:
        return False

    # under-volume
    if peak < config.CONFIG['sound']['min-peak-volume']:
        return False

    return True



