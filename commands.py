from typing import Protocol, Optional
import pyjokes
import datetime
import pyttsx3
import wikipedia
import requests
import json



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


class GetMovie(Protocol):

    def __call__(self) -> tuple[str, str, str]:...


class GetNews(Protocol):

    def __call__(self) -> tuple[str, str]:...


class Joke(BaseTalk):

    def __init__(self) -> None:
        self._pyjoke = pyjokes
        super().__init__()

    def talk(self) -> None:
        joke = self._pyjoke.get_joke()
        print(joke)
        super().speak(joke)


class Movie(BaseTalk):

    def __init__(self, get_movie: GetMovie) -> None:
        self._get_movie = get_movie
        super().__init__()

    def talk(self) -> None:
        title, release_date, overview = self._get_movie()
        print(f"Depois de uma busca na web {title}, é uma boa opção para você.")
        super().speak(f"After a web search {title} is a good choice for you.")

        print(f"{title} foi lançado em {release_date}")
        super().speak(f"{title} was released in {release_date}")

        print(f"Ao lado está a sinopse: {overview}")
        super().speak(f"Next is the synopsis: {overview}")


class News(BaseTalk):

    def __init__(self, get_news: GetNews) -> None:
        self._get_news = get_news
        super().__init__()
    
    def talk(self) -> None:
        title, description = self._get_news()
        print(f"{title}\n {description}")
        super().speak(f"{title} {description}")


class Play(BaseTalk):...

class Temperature(BaseTalk):

    def __init__(self, city) -> None:
        self._api_key = "9acf2c1ebc77ae0343bd7aee42e44304"
        self._url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self._api_key}&units=metric"
        super().__init__()

    def get_temperature(self, city):
        response = requests.get(self._url)
        data = json.loads(response.text)

        # Extract temperature from API response
        temperature = data["main"]["temp"]
        return temperature

    def talk(self) -> None:
        temperature = self.get_temperature("London")
        print(f"Londres está com {temperature}° Celsius")
        print(f"Londres: {temperature}")


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







