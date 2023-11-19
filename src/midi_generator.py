# midi_generator.py
from mido import MidiFile, MidiTrack, Message
import numpy as np

def generar_patron(modelo, longitud_secuencia, num_notas):
    # Inicializar la secuencia de entrada con algún valor o secuencia
    secuencia_entrada = np.zeros((1, longitud_secuencia, num_notas))
    patron_generado = []

    for _ in range(longitud_secuencia):
        probabilidades = modelo.predict(secuencia_entrada)[0]
        nota_siguiente = np.argmax(probabilidades)
        patron_generado.append(nota_siguiente)

        # Actualizar secuencia de entrada para la siguiente predicción
        secuencia_entrada = np.roll(secuencia_entrada, -1, 1)
        secuencia_entrada[0, -1, :] = 0
        secuencia_entrada[0, -1, nota_siguiente] = 1

    print('patron generado',patron_generado)

    return patron_generado

def guardar_como_midi(patron, nombre_archivo):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)

    for nota in patron:
        track.append(Message('note_on', note=nota, velocity=64, time=0))
        track.append(Message('note_off', note=nota, velocity=64, time=480))

    midi.save(nombre_archivo)

# Ejemplo de uso
# patron = generar_patron(modelo, longitud_secuencia, num_notas)
# guardar_como_midi(patron, 'mi_nueva_melodia.mid')
