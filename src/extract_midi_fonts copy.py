    from music21 import converter, stream, note, chord
    import os

    # Directorio de archivos MIDI originales
    midi_dir = './assets/midiFont'
    # Directorio de archivos MIDI procesados
    processed_dir = './assets/processed_midiFiles'



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
    def process_midi_files(midi_dir, notes_dir, chords_dir, target_range=('C1', 'C4')):
        # Convertir las notas del rango objetivo a números MIDI para facilitar la comparación
        target_range_midi = [note.Note(note_name).pitch.midi for note_name in target_range]
        # Duración deseada para todas las notas (en cuartos de nota)
        desired_duration = 8   # 0.125  # 1/8 de nota
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

                    for element in midi_file.flatten():
                        if isinstance(element, note.Note):
                            # Ajustar la nota al rango objetivo si está fuera del rango
                            if element.pitch.midi < target_range_midi[0]:
                                element.pitch.transpose(target_range_midi[0] - element.pitch.midi, inPlace=True)
                            elif element.pitch.midi > target_range_midi[1]:
                                element.pitch.transpose(target_range_midi[1] - element.pitch.midi, inPlace=True)
                            # Crear una nueva nota con la duración deseada
                            new_note = note.Note()
                            new_note.pitch = element.pitch
                            new_note.duration.quarterLength = desired_duration
                            notes_track.append(new_note)
                        elif isinstance(element, chord.Chord):
                            # Ajustar los acordes al rango objetivo si alguno de sus tonos está fuera del rango
                            for tone in element.pitches:
                                if tone.midi < target_range_midi[0]:
                                    element.transpose(target_range_midi[0] - tone.midi, inPlace=True)
                                elif tone.midi > target_range_midi[1]:
                                    element.transpose(target_range_midi[1] - tone.midi, inPlace=True)
                            # Crear un nuevo acorde con la duración deseada
                            new_chord = chord.Chord()
                            new_chord.pitches = element.pitches
                            new_chord.duration.quarterLength = desired_duration
                            chords_track.append(new_chord)

                    # Modificar las rutas de salida para incluir la tonalidad
                    base_filename = filename.split(".")[0]
                    notes_output_path = os.path.join(
                        notes_dir, f'{base_filename}_notes_{key_name}.mid')
                    chords_output_path = os.path.join(
                        chords_dir, f'{base_filename}_chords_{key_name}.mid')

                    # Guardar las pistas en archivos MIDI en las carpetas 'chords' y 'notes'
                    notes_track.write('midi', notes_output_path)
                    chords_track.write('midi', chords_output_path)

    # Llamar a la función
    process_midi_files(midi_dir, notes_dir, chords_dir)


    # Llamar a la función
    process_midi_files(midi_dir, notes_dir, chords_dir)