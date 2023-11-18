import os
import mido

# Función para extraer acordes y notas naturales de un archivo MIDI
def extract_chords_and_notes(input_file_path):
    chords = []
    notes = []

    mid = mido.MidiFile(input_file_path)
    for track in mid.tracks:
        for msg in track:
            if msg.type == "note_on":
                note = msg.note
                velocity = msg.velocity
                if velocity == 0:
                    # Note off event, ignore it
                    continue
                duration = msg.time
                notes.append((note, duration))
            elif msg.type == "control_change":
                # Control change event, interpret it as a chord
                chord = []
                for note in msg.bytes()[1:]:
                    if note != 0:
                        chord.append(note)
                if chord:
                    chords.append(chord)

    return chords, notes

# Función para crear un nuevo archivo MIDI con los acordes extraídos
def create_chords_midi(input_file_path, chords, output_file_path):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    for chord in chords:
        for note in chord:
            track.append(mido.Message("note_on", note=note, velocity=64, time=0))
            track.append(mido.Message("note_off", note=note, velocity=64, time=480))  # Adjust duration as needed

    mid.save(output_file_path)

# Función para crear un nuevo archivo MIDI con las notas naturales extraídas
def create_notes_midi(input_file_path, notes, output_file_path):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    for note, duration in notes:
        track.append(mido.Message("note_on", note=note, velocity=64, time=0))
        track.append(mido.Message("note_off", note=note, velocity=64, time=duration))

    mid.save(output_file_path)

# Directorio de entrada
input_directory = ".src/assets/midiFiles"

# Directorio de salida para acordes
chords_output_directory = ".src/assets/processed_midiFiles/chords"

# Directorio de salida para notas naturales
notes_output_directory = ".src/assets/processed_midiFiles/notes"

# Crea los directorios de salida si no existen
os.makedirs(chords_output_directory, exist_ok=True)
os.makedirs(notes_output_directory, exist_ok=True)

# Procesa cada archivo MIDI en el directorio de entrada
for filename in os.listdir(input_directory):
    if filename.endswith(".mid"):
        input_file_path = os.path.join(input_directory, filename)
        chords, notes = extract_chords_and_notes(input_file_path)

        # Crea un archivo MIDI con los acordes extraídos
        chords_output_file_path = os.path.join(chords_output_directory, filename)
        create_chords_midi(input_file_path, chords, chords_output_file_path)

        # Crea un archivo MIDI con las notas naturales extraídas
        notes_output_file_path = os.path.join(notes_output_directory, filename)
        create_notes_midi(input_file_path, notes, notes_output_file_path)

print("Proceso completado. Archivos MIDI procesados y guardados en los directorios correspondientes.")
