# modelo_ia.py
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Activation

def crear_modelo(num_notas):
    modelo = Sequential()
    modelo.add(LSTM(256, input_shape=(None, num_notas), return_sequences=True))
    modelo.add(Dropout(0.3))
    modelo.add(LSTM(256, return_sequences=True))
    modelo.add(Dropout(0.3))
    modelo.add(LSTM(256))
    modelo.add(Dense(256))
    modelo.add(Dropout(0.3))
    modelo.add(Dense(num_notas))
    modelo.add(Activation('softmax'))
    modelo.compile(loss='categorical_crossentropy', optimizer='rmsprop')
    return modelo
