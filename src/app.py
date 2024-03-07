from flask import Flask, request, send_file
from flask_cors import CORS
from music21 import converter, stream, note, chord
import base64
import os
import tempfile
import zipfile

app = Flask(__name__)
CORS(app)

# Directorio de archivos MIDI procesados
processed_dir = './assets/processed_midiFiles'
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)

def increment_note(note_str):
    # Función para incrementar la nota en +1
    pitch_class = note_str[:-1]
    octave = int(note_str[-1])
    return f"{pitch_class}{octave + 1}"

@app.route('/process_midi', methods=['POST'])
def process_midi():
    # Obtener datos de la solicitud
    data = request.json

    # Parámetros
    desired_duration = data.get('multiplier', 8)
    key_name = data.get('keyName', True)
    notes_export = data.get('notes', True)
    chord_export = data.get('chords', True)
    raw_notes_range = data.get('notesRange', "C1,C6")

    # Validar el formato del parámetro notesRange
    try:
        start_note, end_note = raw_notes_range.split(',')
        start_note = increment_note(start_note.strip())
        end_note = increment_note(end_note.strip())
    except ValueError:
        return {'error': 'El parámetro notesRange no está en el formato correcto. Debe ser "C1,C6".'}

    # Convertir las notas a objetos note.Note
    start_note_obj = note.Note(start_note)
    end_note_obj = note.Note(end_note)

    # Incrementar en +1 el valor del final del rango
    end_note_obj.transpose(1, inPlace=True)

    # Lista para almacenar las rutas de los archivos generados
    generated_files = []

    # Decodificar archivos MIDI desde base64 y procesarlos
    for index, midi_base64 in enumerate(data['midiFiles']):
        midi_data = base64.b64decode(midi_base64)
        midi_stream = converter.parseData(midi_data)

        # Crear nuevas pistas para notas y acordes
        notes_track = stream.Part()
        chords_track = stream.Part()

        for element in midi_stream.flatten():
            if isinstance(element, note.Note):
                # Verificar si la nota está fuera del rango
                if element.pitch < start_note_obj.pitch or element.pitch > end_note_obj.pitch:
                    # Ajustar la octava de la nota al rango especificado
                    element.pitch.octave = start_note_obj.pitch.octave
                new_note = note.Note()
                new_note.pitch = element.pitch
                new_note.duration.quarterLength = desired_duration
                notes_track.append(new_note)
            elif isinstance(element, chord.Chord):
                # Verificar si alguna de las notas del acorde está fuera del rango
                for pitch in element.pitches:
                    if pitch < start_note_obj.pitch or pitch > end_note_obj.pitch:
                        # Ajustar la octava de la nota al rango especificado
                        pitch.octave = start_note_obj.pitch.octave
                new_chord = chord.Chord(element.pitches)
                new_chord.duration.quarterLength = desired_duration
                chords_track.append(new_chord)

        # Generar archivos MIDI si es necesario
        if notes_export:
            notes_output_filename = f'midi_{index}_notes'
            if key_name:
                # Obtener la tonalidad del archivo MIDI
                key = midi_stream.analyze('key')
                key_name = key.tonic.name + " " + key.mode
                notes_output_filename += f'_{key_name}'
            notes_output_filename += '.mid'
            notes_output_path = os.path.join(processed_dir, notes_output_filename)
            notes_track.write('midi', notes_output_path)
            generated_files.append(notes_output_path)

        if chord_export:
            chords_output_filename = f'midi_{index}_chords'
            if key_name:
                # Obtener la tonalidad del archivo MIDI
                key = midi_stream.analyze('key')
                key_name = key.tonic.name + " " + key.mode
                chords_output_filename += f'_{key_name}'
            chords_output_filename += '.mid'
            chords_output_path = os.path.join(processed_dir, chords_output_filename)
            chords_track.write('midi', chords_output_path)
            generated_files.append(chords_output_path)

    # Comprimir los archivos generados en un archivo ZIP
    zip_filename = 'processed_files.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file_path in generated_files:
            # Obtenemos el nombre del archivo de la ruta completa
            file_name = os.path.basename(file_path)
            # Escribimos el archivo en el ZIP con su nombre relativo
            zipf.write(file_path, arcname=file_name)

    # Eliminar archivos generados
    for file_path in generated_files:
        os.remove(file_path)

    # Descargar el archivo comprimido
    return send_file(zip_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
