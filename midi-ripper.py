#!/usr/bin/env python3
# coding: utf-8

# Midi
from mido import open_output, get_output_names

# Audio
import sounddevice as sd
import soundfile as sf

# Utils
from time import sleep
from sys import exit
from os.path import dirname, realpath
from shutil import copyfile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter

# Tools
from midi_tools import play_note, play_chord, ACORDES, NOTAS

EMPTY_WAV = "{}/empty.wav".format(dirname(realpath(__file__)))

#print(sd.query_devices()[0].get('name'))
SOUND_DEVICES = sd.query_devices()
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

args = parser.parse_args()
# print(args)

print("MIDI DEVICE: ", MIDI_DEVICES_NAMES[args.midi_dev])
print("AUDIO-DEVICE: ", SOUND_DEVICES_NAMES[args.sound_dev])

sd.default.samplerate = args.samplerate
sd.default.device = SOUND_DEVICES[args.sound_dev].get('name')
sd.default.channels = args.channels
outport = open_output(get_output_names()[args.midi_dev])

print("Waiting for MIDI silence")
outport.reset()
sleep(5)  # Espero

#
#
notas = range(args.lowest_pitch, args.highest_pitch, args.pitch_step)
DURATION = args.sustain_time + args.decay_time

if args.chords:
    for n in range(args.lowest_pitch, args.highest_pitch):
        for c in ACORDES:
            FILENAME = "/tmp/midi-ripper/%s-%s-%s.wav" % (n, NOTAS[n % len(NOTAS)], c)

            print("Grabando:", FILENAME)
            if not args.dry:
                record = sd.rec(DURATION * args.samplerate) # Begin recording
                sleep(0.002)

            play_chord(outport, n, ACORDES[c], args.sustain_time)

            sleep(args.decay_time)
            sd.wait()

            if not args.dry:
                sf.write(FILENAME, record, args.samplerate)
else:
    #
    # Por cada nota midi
    for n in range(1, 128, 1):
        if args.vsens:
            vs = [24, 64, 127] # Tres volumenes
        else:
            vs = [127, ]

        for v in vs:
            print("| %s (%s) |" % (n, v))

            FILENAME = "/tmp/midi-ripper/n%s-v%s.wav" % (n, v)

            # Si no me pidieron grabarla, genero un archivo vacío,
            # para que sea más fácil importar los samples en ableton
            if n not in notas:
                if not args.dry:
                    # open(FILENAME, 'w').close()
                    copyfile(EMPTY_WAV, FILENAME)
                continue

            if not args.dry:
                record = sd.rec(DURATION * args.samplerate) # Begin recording
                sleep(0.002)

            play_note(outport, n, v, args.sustain_time)
            sleep(args.decay_time)
            sd.wait()
            sleep(0.002)

            if not args.dry:
                sf.write(FILENAME, record, args.samplerate)
            # sleep(1)

exit()

"""
outport.reset()
sleep(5)

sustain = 5
duration = 7

"""
