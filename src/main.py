# main.py
from midi_reader import leer_archivos_midi
from ia_model import crear_modelo
from midi_generator import generar_patron, guardar_como_midi

def main():
    carpeta_midi = '/home/southatoms/Desktop/developLinux/ia_midi/src/assets/processed_midiFiles/chords'  # Reemplaza con el nombre de tu carpeta
    datos_midi = leer_archivos_midi(carpeta_midi)
    
    num_notas = 128  # Esto debería ajustarse según tu modelo y datos
    modelo = crear_modelo(num_notas)

    # Aquí añadirías el código para entrenar el modelo con datos_midi
    # Por ejemplo, podrías convertir datos_midi en una secuencia de entrenamiento
    # y luego usar modelo.fit()

    # Una vez que el modelo está entrenado, generas un nuevo patrón musical
    longitud_secuencia = 50  # Define la longitud del patrón que deseas generar
    patron_generado = generar_patron(modelo, longitud_secuencia, num_notas)

    # Guarda el patrón generado como un archivo MIDI
    guardar_como_midi(patron_generado, 'mi_nueva_melodia.mid')

if __name__ == "__main__":
    main()
