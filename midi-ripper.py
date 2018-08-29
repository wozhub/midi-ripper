#!/usr/bin/env python3
# coding: utf-8

# Midi
from mido import Message, open_output, get_output_names


# Audio
import sounddevice as sd
import soundfile as sf

# Utils
from time import sleep
from sys import exit
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter

#print(sd.query_devices()[0].get('name'))
SOUND_DEVICES = sd.query_devices()
SOUND_DEVICES_NAMES = [ "%d: %s" % (SOUND_DEVICES.index(x),x.get('name')) for x in SOUND_DEVICES]
print(SOUND_DEVICES_NAMES)

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                        epilog="-- Sound Devices:\n"+"\n".join(SOUND_DEVICES_NAMES)
                        )
parser.add_argument('--sound-dev', required=True, choices=range(len(sd.query_devices())))
parser.add_argument('--samplerate', default=44100)
parser.add_argument('--channels', default=1)   # Volcas son MONO!
parser.add_argument('--midi-dev', required=True, choices=get_output_names())
parser.add_argument('--vsens', default=False)  # Velocity Sensitive
parser.add_argument('--asens', default=False)  # Aftertouch Sensitive
parser.add_argument('--sustain', default=10)
#parser.add_argument('--lowest-pitch', default=12)
#parser.add_argument('--highest-pitch', default=115)

args = parser.parse_args()
print(args)
exit()


sd.default.samplerate = args.samplerate
#sd.default.device = 'USB Audio CODEC'
#outport = open_output("CH345 MIDI 1")
outport.reset()

duration = 7 # Segundos

# notas = range(24, 108, 1)
# notas = range(24, 96, 1)  # bajo
notas = range(args.lowest_pitch, 108, 1)

# Por cada nota
for n in notas:

    if args.vsens:
        vs = [24, 64, 127] # Tres volumenes
    else:
        vs = [127, ]

    for v in vs:
        msg_on = Message('note_on', note=n, velocity=v)
        msg_off = Message('note_off', note=n, velocity=v)

        print(msg_on)
        record = sd.rec(duration * samplerate) # Begin recording
        sleep(0.002)
        outport.send(msg_on)
        sleep(sustain)
        print(msg_off)
        outport.send(msg_off)
        sd.wait()
        #sleep(duration-sustain)
        sleep(0.002)
        sf.write("/tmp/streichfett/piano-n%s-v%s.wav" % (n, v), record, samplerate)
        print("-----")
        # sleep(1)


# In[ ]:


msg_on


# In[ ]:


outport.close()


# In[ ]:


myrecording


# In[24]:



# In[53]:


outport.reset()
sleep(5)

sustain = 5
duration = 7

for n in range(60, 72):
    for c in acordes:
        nombre="%s-%s-%s" % (n, NOTAS[n % len(NOTAS)], c)

        print("Grabando:", nombre)
        record = sd.rec(duration * samplerate) # Begin recording
        playChord(outport, n, acordes[c], sustain)

        #sleep(duration-sustain-0.5)
        sd.wait()
        #
        sf.write("/tmp/streichfett/bass-%s.wav" % nombre, record, samplerate)

