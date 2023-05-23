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

# Essa função fará com que minha AV conte 3 notícias em tempo real dos EUA.

def get_latest_news():
    api_key = '1a79b9c9c11c43ccac03f1b93099be80' # insira sua chave de API aqui
    url = f"https://newsapi.org/v2/top-headlines?country=br&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data["articles"]
        article_count = 0
        for article in articles:
            article_count += 1
            if article_count == 4:
                break
            title = article["title"]
            description = article["description"]
            
            return title, description
    else:
        print("Não foi possível obter as notícias mais recentes.")
        talk("Unable to get the latest news.")


# Essa função fará com que AV diga como está a temperatura em Celsius em determinada cidade.

def get_temperature(city):
    api_key = "9acf2c1ebc77ae0343bd7aee42e44304"
    # Make API call to OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = json.loads(response.text)

    # Extract temperature from API response
    temperature = data["main"]["temp"]
    return temperature


# Essa função fará com que AV indique um filme aleatorio para você assistir.

def get_random_movie():
    api_key = "1280354556295865a15447c357067ad2"
    base_url = "https://api.themoviedb.org/3"
    endpoint = "/discover/movie"
    
    params = {
        "api_key": api_key,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "page": 1
    }

    response = requests.get(base_url + endpoint, params=params)
    data = response.json()

    results = data.get("results", [])
    random_item = random.choice(results)
    title = random_item.get("title")
    release_date = random_item.get("release_date")
    overview = random_item.get("overview")

    return title, release_date, overview
    


# Essa função faz com que AV execute todos os comandos.

def run_ava():
    command = take_command()
    print(command)
    if "play" in command: # Esse comando faz com que a AV toca música no youtube.
        song = command.replace("play", "")
        talk("playing " + song)
        pywhatkit.playonyt(song)

    elif "time" in command: # Esse comando faz com que a AV fale a hora atual.
        time = datetime.datetime.now().strftime("%H:%M")
        print(f"Atualmente são {time}")
        talk("Current time is " + time)
    
    elif "i want to know more about" in command: # Esse comando traz uma biografia da web de certa pessoa ou coisa.
        person = command.replace("i want to know more about", "")
        info = wikipedia.summary(person, 3)
        print(info)
        talk(info)
    
    elif "joke" in command: # Esse comando faz com que a AV conte uma piada.
        joke = pyjokes.get_joke()
        print(joke)
        talk(joke)

    elif "temperature in" in command: # Esse comando faz com que a AV fale a temperatura de determinada cidade.
        city = command.replace("temperature in", "").strip()
        temperature = get_temperature(city)
        print(f"Currently {city} is {temperature} degrees Celsius")
        talk(f"Currently {city} is {temperature} degrees Celsius")

    elif "news" in command: # Esse comando trás noticias em 1° mão dos EUA.
        get_latest_news()

    elif "movie" in command: # Esse comando indica um filme aleatorio para você assistir
        title, release_date, overview = get_random_movie()
        print(f"Depois de uma busca na web {title}, é uma boa opção para você.")
        talk(f"After a web search {title} is a good choice for you.")

        print(f"{title} foi lançado em {release_date}")
        talk(f"{title} was released in {release_date}")

        print(f"Ao lado está a sinopse: {overview}")
        talk(f"Next is the synopsis: {overview}")

    elif "stop" in command or "sleep" in command: # Esse comando diz para AV dormir/parar.
        print("Ok! Até logo...")
        talk("OK! See you later...")
        exit()

    else: # Esse comando é executado em caso da AV não entender o que você disse.
        print("Please say the command again")
        talk("Please say the command again")



def command_factory() -> commands.CommandRunner:
    return commands.CommandRunner(
        commands=[
            commands.Movie(get_movie=get_random_movie),
            commands.Joke(),
            commands.Time(),
            commands.News(get_news=get_latest_news),
            commands.Temperature("London"),
            commands.Curiosity()
        ],
        take_command=take_command
    )

while True:
    runner = command_factory()
    if not runner.run():
        break
    # print("oi")
    
