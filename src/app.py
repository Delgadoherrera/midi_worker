from music21 import converter, stream, note, chord
import os

# Directorio de archivos MIDI a procesar
midi_files_dir = 'C:/Users/souhAtoms/Desktop/Desarrollo WIN 2024/personal/midi_worker/src/assets/partial_midi_fonts'

# Directorio de archivos MIDI procesados
processed_dir = 'C:/Users/souhAtoms/Desktop/Desarrollo WIN 2024/personal/midi_worker/src/assets/processed_midiFiles'
notes_dir = os.path.join(processed_dir, 'notes')
chords_dir = os.path.join(processed_dir, 'chords')

# Crear directorios si no existen
for directory in [notes_dir, chords_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def adjust_note_to_range(note_obj, start_note_obj, end_note_obj):
    """
    Ajusta una nota al rango especificado, cambiándola a la octava más cercana dentro del rango.
    """
    while note_obj.pitch < start_note_obj.pitch:
        note_obj.octave += 1
    while note_obj.pitch > end_note_obj.pitch:
        note_obj.octave -= 1
    return note_obj

def increment_note(note_str):
    pitch_class = note_str[:-1]
    octave = int(note_str[-1])
    return f"{pitch_class}{octave + 1}"

def remove_consecutive_duplicates(track):
    cleaned_elements = []
    last_element = None
    for element in track.notesAndRests:
        if isinstance(element, note.Note):
            current_repr = (element.pitch.midi,)
        elif isinstance(element, chord.Chord):
            current_repr = tuple(sorted(p.midi for p in element.pitches))
        else:
            continue  # Ignorar elementos que no sean notas o acordes
        
        if current_repr != last_element:
            cleaned_elements.append(element)
            last_element = current_repr

    cleaned_track = stream.Part()
    for element in cleaned_elements:
        cleaned_track.append(element)
    return cleaned_track

def process_track(track, delete_consecutive, legato_consecutive):
    if delete_consecutive:
        track = remove_consecutive_duplicates(track)
    if legato_consecutive:
        track = merge_consecutive_duplicates(track)
    return track

def merge_consecutive_duplicates(track):
    cleaned_track = stream.Part()
    last_element_repr = None
    last_element = None
    for element in track.notesAndRests:
        if isinstance(element, note.Note) or isinstance(element, chord.Chord):
            current_repr = (element.pitch.midi,) if isinstance(element, note.Note) else tuple(sorted(p.midi for p in element.pitches))
            if current_repr == last_element_repr:
                last_element.duration.quarterLength += element.duration.quarterLength
            else:
                if last_element is not None:
                    cleaned_track.append(last_element)
                last_element = element
                last_element_repr = current_repr
        else:
            cleaned_track.append(element)
            last_element = None
            last_element_repr = None
    if last_element is not None:
        cleaned_track.append(last_element)
    return cleaned_track

def process_midi_file(midi_file_path, index, original_rythm_x=False, key_name=True, notes_export=True, chord_export=True, raw_notes_range="C1,C6"):
    try:
        start_note, end_note = raw_notes_range.split(',')
        start_note = increment_note(start_note.strip())
        end_note = increment_note(end_note.strip())
    except ValueError:
        return {'error': 'El parámetro raw_notes_range no está en el formato correcto. Debe ser, por ejemplo, "C1,C6".'}

    start_note_obj = note.Note(start_note)
    end_note_obj = note.Note(end_note)
    end_note_obj.transpose(1, inPlace=True)  # Asegura que el rango incluya el límite superior

    midi_stream = converter.parse(midi_file_path)

    notes_track = stream.Part()
    chords_track = stream.Part()

    for element in midi_stream.flatten():
        if isinstance(element, note.Note):
            # Ajusta la nota si está fuera del rango
            adjusted_note = adjust_note_to_range(element, start_note_obj, end_note_obj)
            # Procesar la nota ajustada aquí (por ejemplo, cambiar la duración si es necesario)
            if original_rythm_x and isinstance(original_rythm_x, int):
                adjusted_note.duration.quarterLength *= original_rythm_x
            else:
                adjusted_note.duration.quarterLength = 4  # O cualquier lógica de duración deseada
            notes_track.append(adjusted_note)
        elif isinstance(element, chord.Chord):
            adjusted_chord = chord.Chord([adjust_note_to_range(n, start_note_obj, end_note_obj) for n in element.notes])
            # Procesar el acorde ajustado aquí (por ejemplo, cambiar la duración si es necesario)
            if original_rythm_x and isinstance(original_rythm_x, int):
                adjusted_chord.duration.quarterLength *= original_rythm_x
            else:
                adjusted_chord.duration.quarterLength = 4  # O cualquier lógica de duración deseada
            chords_track.append(adjusted_chord)

    generated_files = []

    if notes_export:
        notes_track = process_track(notes_track, False, True)
        notes_output_path = os.path.join(notes_dir, f'SA_Transformed_Midi_{index}_Notes.mid')
        notes_track.write('midi', fp=notes_output_path)
        generated_files.append(notes_output_path)

    if chord_export:
        chords_track = process_track(chords_track, False, True)
        chords_output_path = os.path.join(chords_dir, f'SA_Transformed_Midi_{index}_Chords.mid')
        chords_track.write('midi', fp=chords_output_path)
        generated_files.append(chords_output_path)

    return generated_files

def process_all_midi_files(desired_duration=1, key_name=False, notes_export=True, chord_export=True, raw_notes_range="D2,G5"):
    all_generated_files = []

    for root, dirs, files in os.walk(midi_files_dir):
        for midi_file in files:
            if midi_file.endswith('.mid'):
                midi_file_path = os.path.join(root, midi_file)
                generated_files = process_midi_file(
                    midi_file_path,
                    len(all_generated_files),
                    desired_duration,
                    key_name,
                    notes_export,
                    chord_export,
                    raw_notes_range
                )
                all_generated_files.extend(generated_files)

    return {'generated_files': all_generated_files}

if __name__ == '__main__':
    desired_duration = 4
    original_rythm_x = 1  # Cambiar a False o a otro valor numérico según sea necesario
    key_name = True
    notes_export = True
    chord_export = True
    raw_notes_range = "C1,C1"
    delete_consecutive = False
    legato_consecutive = True   


    generated_files_info = process_all_midi_files(
        desired_duration=desired_duration,
        key_name=key_name,
        notes_export=notes_export,
        chord_export=chord_export,
        raw_notes_range=raw_notes_range
    )
    print(generated_files_info)
