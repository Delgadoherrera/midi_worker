from music21 import converter, stream
from music21.note import Note
from music21.chord import Chord
import os

# Directorio de archivos MIDI originales
midi_dir = '/home/southatoms/Desktop/developLinux/ia_midi/src/assets/midiFont'
# Directorio de archivos MIDI procesados
processed_dir = '/home/southatoms/Desktop/developLinux/ia_midi/src/assets/processed_midiFiles'

# Crear directorios de archivos procesados si no existen
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)

# Subdirectorios para notas y acordes
notes_dir = os.path.join(processed_dir, 'notes')
chords_dir = os.path.join(processed_dir, 'chords')

# Crear subdirectorios si no existen
if not os.path.exists(notes_dir):
    os.makedirs(notes_dir)
if not os.path.exists(chords_dir):
    os.makedirs(chords_dir)

# Función para procesar archivos MIDI


def process_midi_files(midi_dir, notes_dir, chords_dir, duration_multiplier=1.0):
    for root, dirs, files in os.walk(midi_dir):
        for filename in files:
            if filename.endswith('.mid'):
                midi_path = os.path.join(root, filename)
                midi_file = converter.parse(midi_path)

                # Crear nuevas pistas para notas y acordes
                notes_track = stream.Part()
                chords_track = stream.Part()

                # Analizar la tonalidad del archivo MIDI
                key = midi_file.analyze('key')
                key_name = key.tonic.name + " " + key.mode

                for element in midi_file.flat:
                    if isinstance(element, (Note, Chord)):
                        # Ajustar la duración de la nota o acorde
                        element.duration.quarterLength *= duration_multiplier

                    if isinstance(element, Note):
                        notes_track.append(element)
                    elif isinstance(element, Chord):
                        chords_track.append(element)

                        # Modificar las rutas de salida para incluir la tonalidad
                base_filename = filename.split(".")[0]
                notes_output_path = os.path.join(
                    notes_dir, f'{base_filename}_notes_{key_name}.mid')
                chords_output_path = os.path.join(
                    chords_dir, f'{base_filename}_chords_{key_name}.mid')

                # Guardar las pistas en archivos MIDI en las carpetas 'chords' y 'notes'

                notes_track.write('midi', notes_output_path)
                chords_track.write('midi', chords_output_path)


# Llamar a la función con un multiplicador de duración
process_midi_files(midi_dir, notes_dir, chords_dir, duration_multiplier=8.0)
