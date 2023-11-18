# midi_reader.py
import os
from mido import MidiFile

def leer_archivos_midi(carpeta):
    archivos_midi = [f for f in os.listdir(carpeta) if f.endswith('.mid')]
    datos_midi = []
    for archivo in archivos_midi:
        path = os.path.join(carpeta, archivo)
        midi = MidiFile(path)
        datos_midi.append(midi)
    return datos_midi
