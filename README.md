#

## Install

### Requirements

pip install python-rtmidi mido sounddevice soundfile numpy

## Usage

./midi-ripper.py --sound-dev 7 --midi-dev 0 --lowest-pitch 48 --highest-pitch 62 --chords

./midi-ripper.py --sound-dev 7 --midi-dev 0 --lowest-pitch 24 --highest-pitch 96 && beep

## TODO

- [x] Support for picking among default MIDI notes range
- [ ] Give more feedback about the whole process 
- [ ] Platform agnostic temporary folder management
- [x] Recording test to check input volume
- [ ] Check for silence before the recording
- [ ] Crop silence at the end of the recording
- [ ] Samples name format in config
- [ ] Record out folder in config
