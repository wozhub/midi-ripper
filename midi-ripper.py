#!/usr/bin/env python3
# coding: utf-8

# Midi
from mido import open_output, get_output_names

# Audio
#import sounddevice as SOUND_DEVICE
import soundfile as sf
from numpy import delete  # audiolink fix

# Utils
from time import sleep
from sys import exit
from colorama import Fore, Style
from shutil import copyfile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter

# Midi Tools
from midi_tools import MIDI_DEVICE, MIDI_DEVICES_LIST, MIDI_DEVICES_NAMES, ACORDES, NOTAS  # Globals
from midi_tools import set_mididevice, play_chord

# Audio Tools
from audio_tools import SOUND_DEVICE, SOUND_DEVICES_LIST
from audio_tools import set_sounddevice, rip_note, EMPTY_WAV

from IPython import embed

# Config
from config import load_config, CONFIG



# EPILOG
EPILOG = """
-- SOUND DEVICES
%s

-- MIDI DEVICES
%s

""" % ("\n".join(SOUND_DEVICES_LIST), "\n".join(MIDI_DEVICES_NAMES))

PARSER = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, epilog=EPILOG)
# PARSER.add_argument('--asens', default=False)  # Aftertouch Sensitive
PARSER.add_argument('--config-file', default="config.yaml")
PARSER.add_argument('--pitch-range', default="synth")
PARSER.add_argument('--dry', action='store_true')
PARSER.add_argument('--chord-mode', action='store_true')
PARSER.add_argument('--test-mode', action='store_true')
PARSER.add_argument('--test-volume', action='store_true')
PARSER.add_argument('--fix-audiolink', action='store_true')
PARSER.add_argument('--continue-on-clip', action='store_true')

ARGS = PARSER.parse_args()
print(ARGS)

# Load settings from CONFIG FILE
if not load_config(ARGS.config_file):
    print("Couldn't load config file [%s]" % ARGS.config_file)
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

# Send PANIC to MIDI and wait for silence, JIC
print("Waiting for MIDI silence at %s" % MIDI_DEVICE)
MIDI_DEVICE.panic()
MIDI_DEVICE.reset()
sleep(5)  # Espero

#
MIDI_NOTES = range(
    CONFIG['midi-device'][ARGS.pitch_range]['lowest-pitch'],
    CONFIG['midi-device'][ARGS.pitch_range]['highest-pitch'],
    CONFIG['midi-device']['pitch-step']
)

# TODO, is this really necessary?
RECORD_TIME = CONFIG['midi-device']['duration'] * CONFIG['sound-device']['sample-rate']

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
                record = SOUND_DEVICE.rec(RECORD_TIME) # Begin recording
                sleep(0.002)

            play_chord(MIDI_DEVICE, n, ACORDES[c], ARGS.sustain_time)

            sleep(ARGS.decay_time)
            SOUND_DEVICE.wait()

            if not ARGS.dry:
                sf.write(FILENAME, record, CONFIG['sound-device']['sample-rate'])
else:

    # Por cada nota midi
    for MIDI_NOTE in range(1, 128, 1):

        # Por cada velocidad
        for MIDI_VEL in CONFIG['midi-device']['velocities']:

            # TODO: :
            print("Recording: note=%d velocity=%d" % (MIDI_NOTE, MIDI_VEL))

            FILENAME = "{tmp}/n{note:02d}-v{vel:02d}.wav"\
                .format(tmp=CONFIG['temp-dir'], note=MIDI_NOTE, vel=MIDI_VEL)

            # Las notas que no me pidieron grabar, las reemplazo por un wav vacio
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
