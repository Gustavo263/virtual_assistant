from speech_recognition import exceptions
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import requests
import json
import random
import commands
import contextlib

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)


# Essas 2 funções faram que minha AV fale em voz alta.

def talk(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    command = ""
    with contextlib.suppress(exceptions.UnknownValueError):
        with sr.Microphone() as source:
            print("Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if "ava" or "hey" in command:
                command = command.replace("ava", "")
                command = command.replace("hey", "")
                print(command)
    
            return command


def command_factory() -> commands.CommandRunner:
    return commands.CommandRunner(
        commands=[
            commands.About(take_command),
            commands.Play(take_command),
            commands.Temperature(take_command),
            commands.News(),
            commands.Movie(),
            commands.Joke(),
            commands.Time(),
            commands.Curiosity(),
            commands.Food()
        ],
        take_command=take_command
    )

while True:
    runner = command_factory()
    if not runner.run():
        break