from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from music21 import converter, stream, note, chord
import os

app = Flask(__name__)

# Directorio de archivos MIDI procesados
processed_dir = './assets/processed_midiFiles'
# Subdirectorios para notas y acordes
notes_dir = os.path.join(processed_dir, 'notes')
chords_dir = os.path.join(processed_dir, 'chords')

# Configuración para la carga de archivos
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max size

# Asegurarse de que los directorios existen
for directory in [app.config['UPLOAD_FOLDER'], processed_dir, notes_dir, chords_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Ruta de la API para procesar archivos MIDI
@app.route('/process_midi', methods=['POST'])
def process_midi():
    if 'midi_files' not in request.files:
        return jsonify({'error': 'No midi_files part'}), 400

    midi_files = request.files.getlist('midi_files')

    # Validación simple para el número de archivos
    if len(midi_files) > 3:
        return jsonify({'error': 'Too many files, maximum is 3'}), 400

    # Obtener otros parámetros
    x_bar = request.form.get('x_bar', default=8, type=int)
    key_name = request.form.get('key_name', default=False, type=lambda v: v.lower() == 'true')
    notes_export = request.form.get('notes', default=True, type=lambda v: v.lower() == 'true')
    chord_export = request.form.get('chords', default=True, type=lambda v: v.lower() == 'true')

    # Procesar cada archivo MIDI
    for file in midi_files:
        if file and file.filename.endswith('.mid'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Llamada a la función modificada para procesar el archivo
            process_single_midi_file(file_path, x_bar, key_name, notes_export, chord_export)

    return jsonify({'message': 'Files processed successfully'}), 200

# Función para procesar un único archivo MIDI
def process_single_midi_file(midi_path, desired_duration, export_key_name, export_notes, export_chords):
    midi_file = converter.parse(midi_path) 
    notes_track = stream.Part()
    chords_track = stream.Part()
    key = midi_file.analyze('key')
    key_str = f"_{key.tonic.name} {key.mode}" if export_key_name else ""

    for element in midi_file.flatten():
        if isinstance(element, note.Note) and export_notes:
            new_note = note.Note()
            new_note.pitch = element.pitch
            new_note.duration.quarterLength = desired_duration
            notes_track.append(new_note)
        elif isinstance(element, chord.Chord) and export_chords:
            new_chord = chord.Chord()
            new_chord.pitches = element.pitches
            new_chord.duration.quarterLength = desired_duration
            chords_track.append(new_chord)

    base_filename = os.path.splitext(os.path.basename(midi_path))[0]
    if export_notes:
        notes_output_path = os.path.join(notes_dir, f'{base_filename}_notes{key_str}.mid')
        notes_track.write('midi', notes_output_path)
    if export_chords:
        chords_output_path = os.path.join(chords_dir, f'{base_filename}_chords{key_str}.mid')
        chords_track.write('midi', chords_output_path)

if __name__ == '__main__':
    app.run(debug=True)
