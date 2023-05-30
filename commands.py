from typing import Protocol, Optional
import pyjokes
import datetime
import pyttsx3
import wikipedia
import requests
import json
import random
import pywhatkit


class BaseTalk:
    
    def __init__(self) -> None:
        self._engine = pyttsx3.init()
        voices = self._engine.getProperty("voices")
        self._engine.setProperty("voice", voices[1].id)

    def speak(self, text: str):
        self._engine.say(text)
        self._engine.runAndWait()

class TakeCommand(Protocol):

    def __call__(self) -> str:...

class Talk(Protocol):

    def __call__(self, text: str) -> None:...

class Command(Protocol):

    def talk(self) -> None:...


class Joke(BaseTalk):

    def __init__(self) -> None:
        self._pyjoke = pyjokes
        super().__init__()

    def talk(self) -> None:
        joke = self._pyjoke.get_joke()
        print(joke)
        super().speak(joke)


class Movie(BaseTalk):

    def __init__(self) -> None:
        self._api_key = "1280354556295865a15447c357067ad2"
        self._url = "https://api.themoviedb.org/3"
        self._endpoint = "/discover/movie"
        super().__init__()

    def get_movie(self):
        params = {
            "api_key": self._api_key,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "include_video": "false",
            "page": 1
        }

        response = requests.get(self._url + self._endpoint, params=params)
        data = response.json()

        results = data.get("results", [])
        random_item = random.choice(results)
        title = random_item.get("title")
        release_date = random_item.get("release_date")
        overview = random_item.get("overview")

        return title, release_date, overview

    def talk(self) -> None:
        title, release_date, overview = self.get_movie()
        print(f"Depois de uma busca na web {title}, é uma boa opção para você.")
        super().speak(f"After a web search {title} is a good choice for you.")

        print(f"{title} foi lançado em {release_date}")
        super().speak(f"{title} was released in {release_date}")

        print(f"Ao lado está a sinopse: {overview}")
        super().speak(f"Next is the synopsis: {overview}")


class News(BaseTalk):

    def __init__(self) -> None:
        self._api_key = "1a79b9c9c11c43ccac03f1b93099be80"
        self._url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self._api_key}"
        super().__init__()
    
    def get_news(self):
        response = requests.get(self._url)
        if response.status_code == 200:
            data = response.json()
            articles = data["articles"]
            article_count = 0
            for article in articles:
                article_count += 1
                if article == 4:
                    break
                title = article["title"]
                description = article["description"]

                return title, description

    def talk(self) -> None:
        title, description = self.get_news()
        print(f"{title}\n {description}")
        super().speak(f"{title} {description}")


class Food(BaseTalk):

    def __init__(self) -> None:
        self._url = "https://world.openfoodfacts.org/cgi/search.pl"
        super().__init__()

    def get_food(self):
        criterion = {
            "action": "process",
            "tagtype_0": "categories",
            "tag_contains_0": "contains",
            "tag_0": "food",
            "page_size": 50,
            "json": 1
        }

        response = requests.get(self._url, params=criterion)
        data = response.json()

        lista_compras = []
        for produto in data["products"]:
            if "product_name" in produto:
                lista_compras.append(produto["product_name"])
        
        qtd_items = 1
        return random.sample(lista_compras, qtd_items)
    
    def talk(self) -> None:
        food = self.get_food()
        for item in food:
            print(f"""Acho que você irá gostar disso, {item}, é um alimento ótimo para você matar sua fome/sede""")
            super().speak(f"""I think you will like this, {item}, it is a great food for you to quench your hunger/thirst""")


class Temperature(BaseTalk):

    def __init__(self, take_command: TakeCommand) -> None:
        self._take_command = take_command
        self._api_key = "9acf2c1ebc77ae0343bd7aee42e44304"
        self._url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric"
        super().__init__()

    def get_temperature(self, city: str):
        response = requests.get(self._url.format(city, self._api_key))
        data = json.loads(response.text)

        # Extract temperature from API response
        temperature = data["main"]["temp"]
        return temperature

    def talk(self) -> None:
        city = self._take_command()
        temperature = self.get_temperature(city)
        print(f"Atualmente em {city} está fazendo {temperature:.0f}° Celsius.")
        super().speak(f"Currently in {city} it is {temperature:.0f}° Celsius.")


class About(BaseTalk):

    def __init__(self, take_command: TakeCommand) -> None:
        self._take_command = take_command
        super().__init__()

    def talk(self) -> None:
        search = self._take_command()
        wiki = wikipedia.summary(search, 3)
        print(wiki)
        super().speak(wiki)


class Play(BaseTalk):

    def __init__(self, take_command: TakeCommand) -> None:
        self._take_command = take_command
        super().__init__()
    
    def talk(self) -> None:
        song = self._take_command()
        print(f"Dando play em {song}")
        super().speak(f"Playing in {song}")
        pywhatkit.playonyt(song)


class Curiosity(BaseTalk):

    def __init__(self) -> None:
        self._url = "https://uselessfacts.jsph.pl/random.json?language=br"
        super().__init__()

    def get_curiosity(self):
        response = requests.get(self._url)
        data = response.json()
        curiosity = data["text"]
        return curiosity

    def talk(self) -> None:
        curiosity = self.get_curiosity()
        print(curiosity)
        super().speak(curiosity)


class Time(BaseTalk):

    def __init__(self) -> None:
        self._time = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
        super().__init__()
    
    def talk(self) -> None:
        print(f"Atualmente são {self._time}")
        super().speak("Current time is " + self._time)


class CommandRunner:

    def __init__(self, commands: list[Command], take_command: TakeCommand) -> None:
        self._commands = commands
        self._take_command = take_command

    def run(self) -> bool:
        phase = self._take_command()
        print("phase, ", phase)
        if "stop" in phase:
            return False
        for command in self._commands:
            name = command.__class__.__name__.lower()
            if name in phase:
                command.talk()
                return True
        return True







