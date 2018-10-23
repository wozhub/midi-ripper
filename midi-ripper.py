#!/usr/bin/env python3
# coding: utf-8

# Midi
from mido import open_output, get_output_names

# Audio
import sounddevice as SOUND_DEVICE
import soundfile as sf
from numpy import delete  # audiolink fix

# Utils
from time import sleep
from sys import exit
from colorama import Fore, Style
from ruamel import yaml
from shutil import copyfile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter

# Tools
from midi_tools import play_note, play_chord, ACORDES, NOTAS
from rip_tools import rip_note, EMPTY_WAV

from IPython import embed

#print(SOUND_DEVICE.query_devices()[0].get('name'))
SOUND_DEVICES = SOUND_DEVICE.query_devices()
SOUND_DEVICES_NAMES = [x.get('name') for x in SOUND_DEVICES]
SOUND_DEVICES_LIST = ["%d: %s" % (SOUND_DEVICES.index(x), x.get('name')) for x in SOUND_DEVICES]

MIDI_DEVICE = None
MIDI_DEVICES_NAMES = get_output_names()
MIDI_DEVICES_LIST = ["%d: %s" % (MIDI_DEVICES_NAMES.index(x), x) for x in MIDI_DEVICES_NAMES]

# EPILOG
EPILOG = """
-- SOUND DEVICES
%s

-- MIDI DEVICES
%s

""" % ("\n".join(SOUND_DEVICES_LIST), "\n".join(MIDI_DEVICES_NAMES))



def set_sounddevice():
    """  See if the requested sound device is available """

    if not CONFIG['sound-device']['name'] in SOUND_DEVICES_NAMES:
        print("SOUND DEVICE NOT AVAILABLE (%s)" % CONFIG['sound-device']['name'])
        return False

    SOUND_DEVICE.default.samplerate = CONFIG['sound-device']['sample-rate']
    SOUND_DEVICE.default.device = CONFIG['sound-device']['name']

    if ARGS.fix_audiolink:
        SOUND_DEVICE.default.channels = 2  # Will save as ARGS.channels afterwards
    else:
        SOUND_DEVICE.default.channels = CONFIG['sound-device']['channels']
    # SOUND_DEVICE.default.dtype =

    return True

def set_mididevice():
    """  See if requested MIDI DEVICE is available """
    global MIDI_DEVICE

    if not CONFIG['midi-device']['name'] in MIDI_DEVICES_NAMES:
        print("MIDI DEVICE NOT AVAILABLE (%s)" % CONFIG['midi-device']['name'])
        return False

    MIDI_DEVICE = open_output(CONFIG['midi-device']['name'])
    return True


parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, epilog=EPILOG)
# parser.add_argument('--asens', default=False)  # Aftertouch Sensitive
parser.add_argument('--config-file', default="config.yaml")
parser.add_argument('--dry', action='store_true')
parser.add_argument('--chord-mode', action='store_true')
parser.add_argument('--test-mode', action='store_true')
parser.add_argument('--test-volume', action='store_true')
parser.add_argument('--fix-audiolink', action='store_true')
parser.add_argument('--continue-on-clip', action='store_true')

ARGS = parser.parse_args()
print(ARGS)

# LOAD CONFIG FILE
with open(ARGS.config_file, 'r') as stream:
    try:
        CONFIG = yaml.safe_load(stream)
    except yaml.YAMLError as yaml_error:
        print("Couldn't load config file [%s]" % ARGS.config_file)
        print(yaml_error)
        exit(1)

# Set SOUND DEVICE
if set_sounddevice():
    print("SOUND-DEVICE: ", SOUND_DEVICE.default.device)
else:
    print(SOUND_DEVICES_LIST)
    exit(1)

# Set MIDI DEVICE
if set_mididevice():
    print("MIDI DEVICE: ", MIDI_DEVICE)
else:
    print(MIDI_DEVICES_LIST)
    exit(1)

print("Waiting for MIDI silence at %s" % MIDI_DEVICE )
MIDI_DEVICE.panic()
MIDI_DEVICE.reset()
sleep(5)  # Espero

#
MIDI_NOTES = range(
    CONFIG['midi-device']['lowest-pitch'],
    CONFIG['midi-device']['highest-pitch'],
    CONFIG['midi-device']['pitch-step']
)

record_time = CONFIG['midi-device']['duration'] * CONFIG['sound-device']['sample-rate']

if ARGS.test_volume:
    print("Testing Recording Volume --")
    for MIDI_NOTE in [MIDI_NOTES[i] for i in range(0, len(MIDI_NOTES))]:
        for MIDI_VEL in CONFIG['midi-device']['velocities']:
            print("Volume testing: %s (%s)" % (MIDI_NOTE, MIDI_VEL))
            record = rip_note(SOUND_DEVICE, CONFIG['sound-device'],
                              MIDI_DEVICE, CONFIG['midi-device'],
                              MIDI_NOTE, MIDI_VEL)

            if record.min() < -0.95 or record.max() > 0.95:
                print(Fore.RED + "Recording might have clippins!" + Style.RESET_ALL)
                if not ARGS.continue_on_clip:
                    exit(1)

elif ARGS.chord_mode:
    for n in range(ARGS.lowest_pitch, ARGS.highest_pitch):
        for c in ACORDES:
            FILENAME = "/tmp/midi-ripper/%s-%s-%s.wav" % (n, NOTAS[n % len(NOTAS)], c)

            print("Grabando:", FILENAME)
            if not ARGS.dry:
                record = SOUND_DEVICE.rec(record_time) # Begin recording
                sleep(0.002)

            play_chord(MIDI_DEVICE, n, ACORDES[c], ARGS.sustain_time)

            sleep(ARGS.decay_time)
            SOUND_DEVICE.wait()

            if not ARGS.dry:
                sf.write(FILENAME, record, CONFIG['sound-device']['sample-rate'])
else:
    #
    # Por cada nota midi
    for MIDI_NOTE in range(1, 128, 1):
        for MIDI_VEL in CONFIG['midi-device']['velocities']:
            print("Recording: note=%d velocity=%d" % (MIDI_NOTE, MIDI_VEL))

            FILENAME = "/tmp/midi-ripper/n{note:02d}-v{vel:02d}.wav"\
                .format(note=MIDI_NOTE, vel=MIDI_VEL)

            # Las notas que no me pidieron grabar
            if MIDI_NOTE not in MIDI_NOTES:
                if not ARGS.dry:
                    copyfile(EMPTY_WAV, FILENAME)
                continue

            record = rip_note(SOUND_DEVICE, CONFIG['sound-device'],
                              MIDI_DEVICE, CONFIG['midi-device'],
                              MIDI_NOTE, MIDI_VEL)

            if ARGS.fix_audiolink:  # Drop left channel
                record = delete(record, 0, axis=1)

            print("Recorded: {}, {}, {}".format(FILENAME, record.min(), record.max()))

            if not ARGS.dry:
                sf.write(FILENAME, record, CONFIG['sound-device']['sample-rate'])
            # sleep(1)

            if record.min() < -0.95 or record.max() > 0.95:
                print(Fore.RED + "Recording might have clippins!" + Style.RESET_ALL)
                if not ARGS.continue_on_clip:
                    exit(1)



exit()

"""
MIDI_DEVICE.reset()
sleep(5)

sustain = 5
duration = 7

"""
