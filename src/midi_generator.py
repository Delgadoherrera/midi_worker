# midi_generator.py
from mido import MidiFile, MidiTrack, Message
import numpy as np

def ajustar_rango_nota(nota):
    while nota < 48:
        nota += 12  # Subir una octava
    while nota > 84:
        nota -= 12  # Bajar una octava
    return nota

def muestreo_por_temperatura(probabilidades, temperatura=1.0):
    # Ajustar las probabilidades con la temperatura
    probabilidades = np.asarray(probabilidades).astype('float64')
    probabilidades = np.log(probabilidades) / temperatura
    probabilidades_exp = np.exp(probabilidades)
    probabilidades = probabilidades_exp / np.sum(probabilidades_exp)
    elecciones_probables = np.random.multinomial(1, probabilidades, 1)
    return np.argmax(elecciones_probables)

def generar_patron(modelo, longitud_secuencia, num_notas, temperatura=1.0):
    secuencia_entrada = np.zeros((1, longitud_secuencia, num_notas))
    patron_generado = []

    for _ in range(longitud_secuencia):
        probabilidades = modelo.predict(secuencia_entrada)[0]
        nota_siguiente = muestreo_por_temperatura(probabilidades, temperatura)
        patron_generado.append(nota_siguiente)

        secuencia_entrada = np.roll(secuencia_entrada, -1, 1)
        secuencia_entrada[0, -1, :] = 0
        secuencia_entrada[0, -1, nota_siguiente] = 1

    return patron_generado

def guardar_como_midi(patron, nombre_archivo):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)

    for nota in patron:
        nota_ajustada = ajustar_rango_nota(nota)
        track.append(Message('note_on', note=nota_ajustada, velocity=64, time=0))
        track.append(Message('note_off', note=nota_ajustada, velocity=64, time=480))

    midi.save(nombre_archivo)

# Ejemplo de uso
# patron = generar_patron(modelo, longitud_secuencia, num_notas)
# guardar_como_midi(patron, 'mi_nueva_melodia.mid')
