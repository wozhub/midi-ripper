NOTAS = [ 'C', 'Csharp', 'D', 'Dsharp', 'E', 'F', 'Fsharp',
          'G', 'Gsharp', 'A', 'Asharp', 'B' ]
acordes = {
    'maj': [0, 4, 7],
    'maj-inv': [-5, 0, 4],  # una inversion mas "abierta"
    'min': [0, 3, 7],
    'min-inv': [-5, 0, 3],
    'sus2': [0, 2, 7],
    'sus2-inv': [-5, 0, 2],
    'sus4': [0, 5, 7],
    'sus4-inv': [-5, 0, 5],
}

def playChord(midi_out, note, chord, sustain):
    notes = [note+x for x in chord ]

    for n in notes:
        msg = Message('note_on', note=n, velocity=127)
        midi_out.send(msg)

    sleep(sustain)
    midi_out.reset()

    """ # no anda!
    for n in notes:
        Message('note_off', note=n, velocity=127)
        midi_out.send(msg)
    """


