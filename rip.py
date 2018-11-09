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
from pathlib import Path

# Midi Tools
#from midi import midi.DEVICE, midi.DEVICES_LIST, midi.DEVICES_NAMES, ACORDES, NOTAS  # Globals
#from midi import set_mididevice, play_chord
import midi

# Audio Tools
from audio import SOUND_DEVICE, SOUND_DEVICES_LIST
from audio import set_sounddevice, rip_note, EMPTY_WAV
import audio

from IPython import embed

# Logging
import logger

# Config
import config 

# EPILOG
EPILOG = """
-- SOUND DEVICES
%s

-- MIDI DEVICES
%s

""" % ("\n".join(SOUND_DEVICES_LIST), "\n".join(midi.DEVICES_NAMES))

PARSER = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, epilog=EPILOG)
# PARSER.add_argument('--asens', default=False)  # Aftertouch Sensitive
PARSER.add_argument('--config-file', default="config.yaml")
PARSER.add_argument('--pitch-range', default="synth")
PARSER.add_argument('--dry', action='store_true')
PARSER.add_argument('--chord-mode', action='store_true')
PARSER.add_argument('--test-mode', action='store_true')
PARSER.add_argument('--test-volume', action='store_true')
PARSER.add_argument('--fix-audiolink', action='store_true')
PARSER.add_argument('--ignore-clip', action='store_true')
PARSER.add_argument('--continue-rip', action='store_true')

PARSER.add_argument('--instrument', default="unknown")
PARSER.add_argument('--patch-name', default="unknown")

ARGS = PARSER.parse_args()
print(ARGS)

# Load settings from config.CONFIG FILE
if not config.load(ARGS.config_file):
    print("Couldn't load config file [%s]" % ARGS.config_file)
    exit(1)

# Load logger
if not logger.load():
    print("Couldn't create logger file")
    exit(2)

# Set SOUND DEVICE
if set_sounddevice():
    logger.LOGGER.info("SOUND-DEVICE: {}".format(SOUND_DEVICE.default.device))
else:
    logger.LOGGER.error(SOUND_DEVICES_LIST)
    exit(1)

# Set MIDI DEVICE
if midi.load():
    logger.LOGGER.info("MIDI DEVICE: {}".format(midi.DEVICE))
else:
    logger.LOGGER.error(midi.DEVICES_LIST)
    exit(1)

# Send PANIC to MIDI and wait for silence, JIC
logger.LOGGER.debug("Waiting for MIDI silence at %s" % midi.DEVICE)
midi.DEVICE.panic()
midi.DEVICE.reset()
sleep(5)  # Espero

#
MIDI_NOTES = range(
    config.CONFIG['midi-device']['pitch-ranges'][ARGS.pitch_range]['lowest-pitch'],
    config.CONFIG['midi-device']['pitch-ranges'][ARGS.pitch_range]['highest-pitch'],
    config.CONFIG['midi-device']['pitch-step']
)

# TODO, is this really necessary?
RECORD_TIME = config.CONFIG['midi-device']['duration'] * config.CONFIG['sound']['sample-rate']

FAILED = 0

if ARGS.test_volume:
    logger.LOGGER.info("Testing Recording Volume --")
    for MIDI_NOTE in [MIDI_NOTES[i] for i in range(0, len(MIDI_NOTES))]:
        for MIDI_VEL in config.CONFIG['midi-device']['velocities']:
            print("Volume testing: %s (%s)" % (MIDI_NOTE, MIDI_VEL))
            record = rip_note(SOUND_DEVICE, config.CONFIG['sound'],
                              midi.DEVICE, config.CONFIG['midi-device'],
                              MIDI_NOTE, MIDI_VEL)

            # TODO: range should be in config file
            if record.min() < -0.97 or record.max() > 0.97:
                print(Fore.RED + "Recording might have clippins!" + Style.RESET_ALL)
                if not ARGS.ignore_clip:
                    exit(1)

elif ARGS.chord_mode:
    for n in range(ARGS.lowest_pitch, ARGS.highest_pitch):
        for c in ACORDES:
            FILENAME = "/tmp/midi-ripper/%s-%s-%s.wav" % (n, NOTAS[n % len(NOTAS)], c)

            print("Grabando:", FILENAME)
            if not ARGS.dry:
                record = SOUND_DEVICE.rec(RECORD_TIME) # Begin recording
                sleep(0.002)

            play_chord(midi.DEVICE, n, ACORDES[c], ARGS.sustain_time)

            sleep(ARGS.decay_time)
            SOUND_DEVICE.wait()

            if not ARGS.dry:
                sf.write(FILENAME, record, config.CONFIG['sound']['sample-rate'])
else:

    # Por cada nota midi
    for MIDI_NOTE in range(0, 128, 1):

        # Por cada velocidad
        for MIDI_VEL in config.CONFIG['midi-device']['velocities']:

            # TODO: :
            print("Recording: note=%d velocity=%d" % (MIDI_NOTE, MIDI_VEL))

            FILENAME = "{tmp}/n{note:02d}-v{vel:02d}.wav"\
                .format(tmp=config.CONFIG['temp-dir'], note=MIDI_NOTE, vel=MIDI_VEL)

            # Si ya existe el archivo, continuo
            if ARGS.continue_rip and Path(FILENAME).exists():
                logger.LOGGER.debug("{} already ripped.".format(FILENAME))
                continue

            # Las notas que no me pidieron grabar, las reemplazo por un wav vacio
            if MIDI_NOTE not in MIDI_NOTES:
                if not ARGS.dry:
                    copyfile(EMPTY_WAV, FILENAME)
                continue

            record = rip_note(SOUND_DEVICE, config.CONFIG['sound'],
                              midi.DEVICE, config.CONFIG['midi-device'],
                              MIDI_NOTE, MIDI_VEL)

            if ARGS.fix_audiolink:  # Drop left channel
                record = delete(record, 0, axis=1)

            print("Recorded: {}, {}, {}".format(FILENAME, record.min(), record.max()))

            if not ARGS.dry:
                sf.write(FILENAME, record, config.CONFIG['sound']['sample-rate'])
            # sleep(1)

            if not audio.check_volume(record):
                logger.LOGGER.error(Fore.RED + "Recording might have clippins!" + Style.RESET_ALL)
                FAILED+=1

                Path(FILENAME).unlink()

                if not ARGS.ignore_clip:
                    exit(1)



exit()

"""
midi.DEVICE.reset()
sleep(5)

sustain = 5
duration = 7

"""
