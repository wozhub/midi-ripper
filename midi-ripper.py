#!/usr/bin/env python3
# coding: utf-8

# Midi
from mido import open_output, get_output_names

# Audio
import sounddevice as SOUND_DEVICE
import soundfile as sf

# Utils
from time import sleep
from sys import exit
from colorama import Fore, Style

from shutil import copyfile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter

# Tools
from midi_tools import play_note, play_chord, ACORDES, NOTAS
from rip_tools import rip_note, EMPTY_WAV


#print(SOUND_DEVICE.query_devices()[0].get('name'))
SOUND_DEVICES = SOUND_DEVICE.query_devices()
SOUND_DEVICES_NAMES = ["%d: %s" % (SOUND_DEVICES.index(x), x.get('name')) for x in SOUND_DEVICES]

MIDI_DEVICES_NAMES = get_output_names()
MIDI_DEVICES_NAMES = ["%d: %s" % (MIDI_DEVICES_NAMES.index(x), x) for x in MIDI_DEVICES_NAMES]

# EPILOG
EPILOG = """
-- SOUND DEVICES
%s

-- MIDI DEVICES
%s

""" % ("\n".join(SOUND_DEVICES_NAMES), "\n".join(MIDI_DEVICES_NAMES))

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, epilog=EPILOG)
parser.add_argument('--sound-dev', required=True, type=int, choices=range(len(SOUND_DEVICES_NAMES)))
#parser.add_argument('--samplerate', default=44100)
parser.add_argument('--samplerate', default=48000)
parser.add_argument('--channels', type=int, default=1)   # Volcas son MONO!
parser.add_argument('--midi-dev', required=True, type=int, choices=range(len(MIDI_DEVICES_NAMES)))
parser.add_argument('--vsens', action='store_true')  # Velocity Sensitive
parser.add_argument('--asens', default=False)  # Aftertouch Sensitive
parser.add_argument('--sustain-time', type=int, default=10)
parser.add_argument('--decay-time', type=int, default=3)
parser.add_argument('--lowest-pitch', type=int, default=24)
parser.add_argument('--highest-pitch', type=int, default=96)
parser.add_argument('--pitch-step', default=1)
parser.add_argument('--chords', action='store_true')
parser.add_argument('--dry', action='store_true')
parser.add_argument('--continue-on-clip', action='store_true')

args = parser.parse_args()
print(args)

print("MIDI DEVICE: ", MIDI_DEVICES_NAMES[args.midi_dev])
print("AUDIO-DEVICE: ", SOUND_DEVICES_NAMES[args.sound_dev])

SOUND_DEVICE.default.samplerate = args.samplerate
SOUND_DEVICE.default.device = SOUND_DEVICES[args.sound_dev].get('name')
SOUND_DEVICE.default.channels = args.channels
# SOUND_DEVICE.default.dtype =

MIDI_OUT = open_output(get_output_names()[args.midi_dev])

print("Waiting for MIDI silence")
MIDI_OUT.reset()
sleep(5)  # Espero

#
MIDI_NOTES = range(args.lowest_pitch, args.highest_pitch, args.pitch_step)
if args.vsens:
    MIDI_VELOCITIES = [24, 64, 127] # Tres volumenes
else:
    MIDI_VELOCITIES = [127, ]
DURATION = args.sustain_time + args.decay_time

if args.chords:
    for n in range(args.lowest_pitch, args.highest_pitch):
        for c in ACORDES:
            FILENAME = "/tmp/midi-ripper/%s-%s-%s.wav" % (n, NOTAS[n % len(NOTAS)], c)

            print("Grabando:", FILENAME)
            if not args.dry:
                record = SOUND_DEVICE.rec(DURATION * args.samplerate) # Begin recording
                sleep(0.002)

            play_chord(MIDI_OUT, n, ACORDES[c], args.sustain_time)

            sleep(args.decay_time)
            SOUND_DEVICE.wait()

            if not args.dry:
                sf.write(FILENAME, record, args.samplerate)
else:
    #
    # Por cada nota midi
    for MIDI_NOTE in range(1, 128, 1):
        for MIDI_VEL in MIDI_VELOCITIES:
            print("Recording: %s (%s)" % (MIDI_NOTE, MIDI_VEL))

            FILENAME = "/tmp/midi-ripper/n{note:02d}-v{vel:02d}.wav"\
                .format(note=MIDI_NOTE, vel=MIDI_VEL)

            # Las notas que no me pidieron grabar
            if MIDI_NOTE not in MIDI_NOTES and not args.dry:
                copyfile(EMPTY_WAV, FILENAME)
                continue

            record = rip_note(SOUND_DEVICE, args.samplerate, \
                              MIDI_OUT, MIDI_NOTE, MIDI_VEL, \
                              args.sustain_time, args.decay_time)

            if record.min() < -0.9 or record.max() > 0.9:
                print(Fore.RED + "Recording might have clippins!" + Style.RESET_ALL)
                if not args.continue_on_clip:
                    exit(1)

            print("Recorded: {}, {}, {}".format(FILENAME, record.min(), record.max()))

            if not args.dry:
                sf.write(FILENAME, record, args.samplerate)
            # sleep(1)

exit()

"""
MIDI_OUT.reset()
sleep(5)

sustain = 5
duration = 7

"""
