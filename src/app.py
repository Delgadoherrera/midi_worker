from flask import Flask, request, jsonify
import base64
import os
from werkzeug.utils import secure_filename
from music21 import converter, stream, note, chord, pitch, midi
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max size

processed_dir = './assets/processed_midiFiles'
notes_dir = os.path.join(processed_dir, 'notes')
chords_dir = os.path.join(processed_dir, 'chords')

for directory in [app.config['UPLOAD_FOLDER'], processed_dir, notes_dir, chords_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_base64_midi(midi_base64, filename):
    # Eliminar el prefijo de datos Base64 si está presente
    if midi_base64.startswith('data:'):
        # Encuentra la coma y extrae solo la parte Base64 de la cadena
        midi_base64 = midi_base64.split(',', 1)[1]
    
    try:
        midi_data = base64.b64decode(midi_base64)
    except ValueError as e:
        print(f"Error decoding base64 MIDI data: {e}")
        return None
    
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(path, 'wb') as midi_file:
        midi_file.write(midi_data)
    
    return path

def adjust_note_octave(note_obj, lower_bound, upper_bound):
    while note_obj.pitch < lower_bound or note_obj.pitch > upper_bound:
        if note_obj.pitch < lower_bound:
            note_obj.octave += 1
        elif note_obj.pitch > upper_bound:
            note_obj.octave -= 1
    return note_obj

def process_single_midi_file(midi_path, x_bar, key_name, notes_export, chord_export, notes_range):
    lower_bound_str, upper_bound_str = notes_range.split(',')
    lower_bound = pitch.Pitch(lower_bound_str)
    upper_bound = pitch.Pitch(upper_bound_str)

    midi_file = converter.parse(midi_path)
    notes_track = stream.Part()
    chords_track = stream.Part()
    key = midi_file.analyze('key')
    key_str = f"_{key.tonic.name} {key.mode}" if key_name else ""

    for element in midi_file.flatten():
        if isinstance(element, note.Note) and notes_export:
            adjusted_note = adjust_note_octave(element, lower_bound, upper_bound)
            notes_track.append(adjusted_note)
        elif isinstance(element, chord.Chord) and chord_export:
            adjusted_notes = [adjust_note_octave(n, lower_bound, upper_bound) for n in element.notes]
            adjusted_chord = chord.Chord(adjusted_notes)
            chords_track.append(adjusted_chord)

    base_filename = os.path.splitext(os.path.basename(midi_path))[0]
    if notes_export:
        notes_output_path = os.path.join(notes_dir, f'{base_filename}_notes{key_str}.mid')
        notes_track.write('midi', notes_output_path)
    if chord_export:
        chords_output_path = os.path.join(chords_dir, f'{base_filename}_chords{key_str}.mid')
        chords_track.write('midi', chords_output_path)

@app.route('/process_midi', methods=['POST'])
def process_midi():
    data = request.json
    
    if not data or 'midiFiles' not in data:
        return jsonify({'error': 'No midiFiles part'}), 400

    midi_files_base64 = data['midiFiles']
    if len(midi_files_base64) > 3:
        return jsonify({'error': 'Too many files, maximum is 3'}), 400

    x_bar = data.get('multiplier', 8)
    key_name = data.get('keyName', False)
    notes_export = data.get('notes', True)
    chord_export = data.get('chords', True)
    notes_range = data.get('notesRange', "C1,C6")

    processed_files = []
    errors = []

    for index, midi_base64 in enumerate(midi_files_base64):
        filename = f"midi_file_{index}.mid"
        file_path = save_base64_midi(midi_base64, filename)
        try:
            process_single_midi_file(file_path, x_bar, key_name, notes_export, chord_export, notes_range)
            processed_files.append(filename)
        except midi.MidiException as e:
            errors.append(f"Error processing file {filename}: {str(e)}")
            os.remove(file_path)  # Cleanup the saved file if it's invalid

    if errors:
        # If there are any errors, include them in the response
        return jsonify({'message': 'Some files could not be processed', 'errors': errors, 'processed_files': processed_files}), 400
    return jsonify({'message': 'Files processed successfully', 'processed_files': processed_files}), 200

if __name__ == '__main__':
    app.run(debug=True)
