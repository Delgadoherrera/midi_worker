from music21 import converter, stream, note, chord, scale
import os

# Directorio de archivos MIDI a procesar
midi_files_dir = 'C:/Users/souhAtoms/Documents/MIDIs/'

# Directorio de archivos MIDI procesados
processed_dir = 'C:/Users/souhAtoms/Desktop/Desarrollo WIN 2024/personal/midi_worker/src/assets/processed_midiFiles'

notes_dir = os.path.join(processed_dir, 'notes')
chords_dir = os.path.join(processed_dir, 'chords')

# Crear directorios si no existen
for directory in [notes_dir, chords_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def are_chords_equivalent(chord1, chord2):
    """
    Comprueba si dos acordes son equivalentes, ignorando el orden de las notas
    y permitiendo pequeñas variaciones en las notas.
    """
    # Obtiene las notas (pitches MIDI) de cada acorde, ordenadas
    pitches1 = sorted(p.midi for p in chord1.pitches)
    pitches2 = sorted(p.midi for p in chord2.pitches)

    # Comprueba si los acordes tienen el mismo número de notas
    if len(pitches1) != len(pitches2):
        return False

    # Permite una pequeña variación en las notas para considerarlas iguales
    variation_threshold = 1  # Puedes ajustar este valor si es necesario
    for p1, p2 in zip(pitches1, pitches2):
        if abs(p1 - p2) > variation_threshold:
            return False

    return True

def increment_note(note_str):
    # Función para incrementar la nota en +1
    pitch_class = note_str[:-1]
    octave = int(note_str[-1])
    return f"{pitch_class}{octave + 1}"

def remove_consecutive_duplicates(track):
    cleaned_elements = []
    last_element = None

    for element in track.notesAndRests:
        # Ignorar elementos que no sean notas o acordes
        if not isinstance(element, (note.Note, chord.Chord)):
            continue

        current_repr = element if isinstance(element, chord.Chord) else (element.pitch.midi,)

        if last_element is not None:
            if isinstance(element, chord.Chord) and isinstance(last_element, chord.Chord):
                # Usa la nueva función de comparación para acordes
                if not are_chords_equivalent(element, last_element):
                    cleaned_elements.append(element)
            elif current_repr != last_element:
                cleaned_elements.append(element)
        else:
            cleaned_elements.append(element)

        last_element = element if isinstance(element, chord.Chord) else current_repr

    cleaned_track = stream.Part()
    for element in cleaned_elements:
        cleaned_track.append(element)
    return cleaned_track

def transpose_to_range(note_or_chord, start_pitch, end_pitch):
    """
    Transpone una nota o todas las notas de un acorde al rango especificado.
    """
    if isinstance(note_or_chord, note.Note):
        while note_or_chord.pitch < start_pitch:
            note_or_chord.transpose('P8', inPlace=True)
        while note_or_chord.pitch > end_pitch:
            note_or_chord.transpose('-P8', inPlace=True)
    elif isinstance(note_or_chord, chord.Chord):
        for n in note_or_chord.notes:
            while n.pitch < start_pitch:
                n.transpose('P8', inPlace=True)
            while n.pitch > end_pitch:
                n.transpose('-P8', inPlace=True)



def process_track(track, delete_consecutive, legato_consecutive):
    if delete_consecutive:
        return remove_consecutive_duplicates(track)
    elif legato_consecutive:
        return merge_consecutive_duplicates(track)
    else:
        return track  # No se aplica ninguna modificación

def merge_consecutive_duplicates(track):
    cleaned_track = stream.Part()
    last_element_repr = None
    last_element = None
    for element in track.notesAndRests:
        if isinstance(element, note.Note):
            current_repr = (element.pitch.midi,)
        elif isinstance(element, chord.Chord):
            current_repr = tuple(sorted(p.midi for p in element.pitches))
        else:
            current_repr = None
        
        if current_repr == last_element_repr and last_element is not None:
            # Extiende la duración de la última nota/acorde
            last_element.duration.quarterLength += element.duration.quarterLength
        else:
            if last_element is not None:
                cleaned_track.append(last_element)
            if isinstance(element, (note.Note, chord.Chord)):
                last_element = element
                last_element_repr = current_repr
            else:
                # Directamente añadir elementos que no sean nota o acorde
                cleaned_track.append(element)
                last_element = None
                last_element_repr = None
    # Asegúrate de añadir el último elemento procesado
    if last_element is not None:
        cleaned_track.append(last_element)
    return cleaned_track


def quantize_note_to_scale(note, chosen_scale):
    """
    Ajusta la nota para que encaje en la escala proporcionada.
    """
    pitch_midi = note.pitch.midi
    # Genera los pitches de la escala dentro de un rango cercano al pitch de la nota
    scale_pitches = [p.midi for p in chosen_scale.getPitches(note.pitch.transpose(-12), note.pitch.transpose(12))]
    
    # Encuentra el pitch de la escala más cercano al pitch de la nota
    closest_pitch_midi = min(scale_pitches, key=lambda p: abs(p - pitch_midi))
    
    # Asigna el pitch más cercano a la nota
    note.pitch.midi = closest_pitch_midi
    return note

def process_midi_file(midi_file_path, index, desired_duration=8, key_name=True, notes_export=True, chord_export=True, raw_notes_range="C1,C6"):
    try:
        start_note, end_note = raw_notes_range.split(',')
        start_note = increment_note(start_note.strip())
        end_note = increment_note(end_note.strip())
    except ValueError:
        return {'error': 'El parámetro notesRange no está en el formato correcto. Debe ser "C1,C6".'}

    start_note_obj = note.Note(start_note)
    end_note_obj = note.Note(end_note)
   # end_note_obj.transpose(1, inPlace=True)  # Esto asegura que el rango incluya el extremo superior

    midi_stream = converter.parse(midi_file_path)
    key = midi_stream.analyze('key')

    if key.mode == 'major':
        chosen_scale = scale.MajorScale(key.tonic)
    else:
        chosen_scale = scale.MinorScale(key.tonic)

    notes_track = stream.Part()
    chords_track = stream.Part()

    last_note_or_chord = None

    for element in midi_stream.flatten():
        if isinstance(element, note.Note) or isinstance(element, chord.Chord):
            transpose_to_range(element, start_note_obj.pitch, end_note_obj.pitch)
            # Cuantizar notas y acordes a la escala antes de procesarlas
            if isinstance(element, note.Note):
                element = quantize_note_to_scale(element, chosen_scale)
                current_note_repr = (element.pitch.midi,)
                if last_note_or_chord != current_note_repr:
                    new_note = note.Note()
                    new_note.pitch = element.pitch
                    new_note.duration.quarterLength = desired_duration
                    notes_track.append(new_note)
                    last_note_or_chord = current_note_repr
            elif isinstance(element, chord.Chord):
                new_chord_pitches = [quantize_note_to_scale(n, chosen_scale) for n in element.notes]
                element = chord.Chord(new_chord_pitches)
                if len(element.pitches) > 1:  # Verificar que hay más de una nota
                    current_chord_repr = tuple(sorted(p.midi for p in element.pitches))
                    if last_note_or_chord != current_chord_repr:
                        new_chord = chord.Chord(element.pitches)
                        new_chord.duration.quarterLength = desired_duration
                        chords_track.append(new_chord)
                        last_note_or_chord = current_chord_repr

    generated_files = []

    if notes_export:
        notes_track = process_track(notes_track, delete_consecutive, legato_consecutive)
        notes_output_filename = f'SA_Transformed_Midi_{index}_Notes'
        if key_name:
            key = midi_stream.analyze('key')
            key_name = key.tonic.name + " " + key.mode
            notes_output_filename += f'_{key_name}'
        notes_output_filename += '.mid'
        notes_output_path = os.path.join(notes_dir, notes_output_filename)
        notes_track.write('midi', notes_output_path)
        generated_files.append(notes_output_path)

    if chord_export:
        chords_track = process_track(chords_track, delete_consecutive, legato_consecutive)
        chords_output_filename = f'SA_Transformed_Midi_{index}_Chords'
        if key_name:
            key = midi_stream.analyze('key')
            key_name = key.tonic.name + " " + key.mode
            chords_output_filename += f'_{key_name}'
        chords_output_filename += '.mid'
        chords_output_path = os.path.join(chords_dir, chords_output_filename)
        chords_track.write('midi', chords_output_path)
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
                    desired_duration=desired_duration,
                    key_name=key_name,
                    notes_export=notes_export,
                    chord_export=chord_export,
                    raw_notes_range=raw_notes_range
                )
                all_generated_files.extend(generated_files)

    return {'generated_files': all_generated_files}

if __name__ == '__main__':
    desired_duration = 8
    key_name = True
    notes_export = False
    chord_export = True
    raw_notes_range = "C2,C3"
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