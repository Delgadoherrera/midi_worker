from music21 import converter, stream
from music21.note import Note
from music21.chord import Chord
import os

# Directorio de archivos MIDI originales
midi_dir = '/home/southatoms/Desktop/developLinux/ia_midi/src/assets/midiFont'
# Directorio de archivos MIDI procesados
processed_dir = '/home/southatoms/Desktop/developLinux/ia_midi/src/assets/processed_midiFiles'


# Crear directorio de archivos procesados si no existe
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)

# Función para procesar archivos MIDI
def process_midi_files(midi_dir, processed_dir):
    for filename in os.listdir(midi_dir):
        if filename.endswith('.mid'):
            # Cargar archivo MIDI
            midi_path = os.path.join(midi_dir, filename)
            midi_file = converter.parse(midi_path)

            # Crear dos nuevas pistas: una para notas y otra para acordes
            notes_track = stream.Part()
            chords_track = stream.Part()

            # Iterar a través de todas las notas y acordes del archivo MIDI
            for element in midi_file.flat:
                if isinstance(element, Note):
                    # Añadir nota a la pista de notas
                    notes_track.append(element)
                elif isinstance(element, Chord):
                    # Añadir acorde a la pista de acordes
                    chords_track.append(element)

            # Guardar las pistas en archivos MIDI separados
            notes_track.write('midi', os.path.join(processed_dir, f'{filename}_notes.mid'))
            chords_track.write('midi', os.path.join(processed_dir, f'{filename}_chords.mid'))

# Llamar a la función para procesar los archivos
process_midi_files(midi_dir, processed_dir)