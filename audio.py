#!/usr/bin/env python3

from os.path import dirname, realpath
from time import sleep

# Audio
import sounddevice as SOUND_DEVICE


from midi import play_note

# Config
import config


EMPTY_WAV = "{}/empty.wav".format(dirname(realpath(__file__)))
WAIT_START = 0.002
WAIT_END = 0.002

#print(SOUND_DEVICE.query_devices()[0].get('name'))
SOUND_DEVICES = SOUND_DEVICE.query_devices()
SOUND_DEVICES_NAMES = [x.get('name') for x in SOUND_DEVICES]
SOUND_DEVICES_LIST = ["%d: %s" % (SOUND_DEVICES.index(x), x.get('name')) for x in SOUND_DEVICES]


def set_sounddevice():
    """  See if the requested sound device is available """
    if config.CONFIG is None:
        # TODO: Should raise error
        print("Must load config first!")
        return False

    if not config.CONFIG['sound']['name'] in SOUND_DEVICES_NAMES:
        print("SOUND DEVICE NOT AVAILABLE (%s)" % config.CONFIG['sound']['name'])
        return False

    SOUND_DEVICE.default.samplerate = config.CONFIG['sound']['sample-rate']
    SOUND_DEVICE.default.device = config.CONFIG['sound']['name']
    SOUND_DEVICE.default.channels = 1  # Will save as ARGS.channels afterwards

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
    if peak > config.CONFIG['sound']['volume'] + config.CONFIG['sound']['threshold']:
        return False

    # under-volume
    if peak < config.CONFIG['sound']['volume'] - config.CONFIG['sound']['threshold']:
        return False

    return True



