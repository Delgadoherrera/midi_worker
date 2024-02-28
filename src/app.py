from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from music21 import converter, stream, note, chord, pitch
import os

app = Flask(__name__)

# Configuraciones y directorios
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max size
processed_dir = './assets/processed_midiFiles'
notes_dir = os.path.join(processed_dir, 'notes')
chords_dir = os.path.join(processed_dir, 'chords')

# Asegurar existencia de directorios
for directory in [app.config['UPLOAD_FOLDER'], processed_dir, notes_dir, chords_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Ruta de la API para procesar archivos MIDI
@app.route('/process_midi', methods=['POST'])
def process_midi():
    if 'midi_files' not in request.files:
        return jsonify({'error': 'No midi_files part'}), 400

    midi_files = request.files.getlist('midi_files')
    if len(midi_files) > 3:
        return jsonify({'error': 'Too many files, maximum is 3'}), 400

    # Obtener parámetros
    x_bar = request.form.get('x_bar', default=8, type=int)
    key_name = request.form.get('key_name', default=False, type=lambda v: v.lower() == 'true')
    notes_export = request.form.get('notes', default=True, type=lambda v: v.lower() == 'true')
    chord_export = request.form.get('chord', default=True, type=lambda v: v.lower() == 'true')
    notes_range = request.form.get('notes_range', default="C1,C6")

    # Procesar archivos
    for file in midi_files:
        if file and file.filename.endswith('.mid'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            process_single_midi_file(file_path, x_bar, key_name, notes_export, chord_export, notes_range)

    return jsonify({'message': 'Files processed successfully'}), 200

def adjust_note_octave(note_obj, lower_bound, upper_bound):
    while note_obj.pitch < lower_bound or note_obj.pitch > upper_bound:
        if note_obj.pitch < lower_bound:
            note_obj.octave += 1
        elif note_obj.pitch > upper_bound:
            note_obj.octave -= 1
    return note_obj



def process_single_midi_file(midi_path, desired_duration, export_key_name, export_notes, export_chords, notes_range):
    lower_bound_str, upper_bound_str = notes_range.split(',')
    
    # Incrementar la octava especificada por parámetro
    lower_bound = pitch.Pitch(lower_bound_str)
    upper_bound = pitch.Pitch(upper_bound_str)
    lower_bound.octave += 1
    upper_bound.octave += 1

    midi_file = converter.parse(midi_path)
    notes_track = stream.Part()
    chords_track = stream.Part()
    key = midi_file.analyze('key')
    key_str = f"_{key.tonic.name} {key.mode}" if export_key_name else ""

    for element in midi_file.flatten():
        if isinstance(element, note.Note) and export_notes:
            adjusted_note = adjust_note_octave(element, lower_bound, upper_bound)
            notes_track.append(adjusted_note)
        elif isinstance(element, chord.Chord) and export_chords:
            # Asegurarse de que todas las notas del acorde estén dentro del rango ajustado
            adjusted_notes = [adjust_note_octave(n, lower_bound, upper_bound) for n in element.notes]
            adjusted_chord = chord.Chord(adjusted_notes)
            chords_track.append(adjusted_chord)

    base_filename = os.path.splitext(os.path.basename(midi_path))[0]
    if export_notes:
        notes_output_path = os.path.join(notes_dir, f'{base_filename}_notes{key_str}.mid')
        notes_track.write('midi', notes_output_path)
    if export_chords:
        chords_output_path = os.path.join(chords_dir, f'{base_filename}_chords{key_str}.mid')
        chords_track.write('midi', chords_output_path)


if __name__ == '__main__':
    app.run(debug=True)
