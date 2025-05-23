import speech_recognition as sr
import keyboard

def listar_dispositivos():
    dispositivos = sr.Microphone.list_microphone_names()
    for index, name in enumerate(dispositivos):
        print(f"{index}: {name}")

def speechToText(device_index=None):
    pass