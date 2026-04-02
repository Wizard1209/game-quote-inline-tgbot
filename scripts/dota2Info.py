import sys, os
from dataclasses import dataclass
from enum import Enum
from typing import TypedDict
import httpx
from bs4 import BeautifulSoup, Tag
import json

class QuoteInfo(TypedDict):
    hero: str
    url: str
    lang: str
    lyrics: str

class Link(TypedDict):
    name: str
    link: str

class Lang(Enum):
        RU = 'ru'
        EN = 'en'


@dataclass
class Dota2WikiHelper: 

    baseLink = 'https://dota2.fandom.com'

    allHeroLink : str
    replicasLink : str
    lang : Lang

    @classmethod
    def RU(cls):
        allHeroLink = 'https://dota2.fandom.com/ru/wiki/%D0%93%D0%B5%D1%80%D0%BE%D0%B8'
        replicasLink = '/Реплики'
        lang = Lang.RU
        return cls(allHeroLink, replicasLink, lang)
    
    @classmethod
    def EN(cls):
        allHeroLink = 'https://dota2.fandom.com/wiki/Heroes'
        replicasLink = '/Sounds'
        lang = Lang.EN
        return cls(allHeroLink, replicasLink, lang)

class Dota2Wiki:

    helper : Dota2WikiHelper = None
    
    heroes: list[Link] = []

    def __init__(self, helper : Dota2WikiHelper):
        self.helper = helper

    def getAllHeroes(self: "Dota2Wiki") -> list[Link]:
        if len(self.heroes) > 0:
            return self.heroes

        heroes: list[Link] = []
        markup = httpx.get(self.helper.allHeroLink)
        soup = BeautifulSoup(markup, "html.parser")
        content = soup.find("div", {"class": "mw-parser-output"})

        title = content.find(name="tbody")
        trs: list[Tag] = title.find_all(name="tr", recursive=False)
        for tr in trs:
            tds = tr.find_all(name="td", recursive=False)
            for td in tds:
                divs = td.find_all(name="div", recursive=False)
                for div in divs:
                    heroes.append(
                        Link(
                            name=div.a.get("title"), 
                            link=self.helper.baseLink + div.a.get("href")
                        )
                    )

        self.heroes = heroes

        return heroes

    def getSoundsByHero(self: "Dota2Wiki", hero: Link) -> list[Link]:
        sounds: list[Link] = []

        link = hero["link"] + self.helper.replicasLink
        markup = httpx.get(link, timeout = 1000)
        soup = BeautifulSoup(markup, "html.parser")
        content = soup.find("div", {"class": "mw-parser-output"})
        
        uls: list[Tag] = content.find_all(name="ul", recursive=False)
        for ul in uls:
            lis: list[Tag] = ul.find_all(name="li", recursive=False)
            for li in lis:
                spans: list[Tag] = li.find_all(name="span", recursive=False)
                index = 1
                for span in spans:
                    link = span.find("a")
                    if link != None:
                        text = li.text
                        text = text.replace("Link▶️", "")
                        text = text.strip()

                        if len(spans) > 1:
                            text = f"[{index}] {text}"

                        href = link.get("href")
                        sounds.append(Link(name=text, link=href))
                        index = index + 1
        return sounds

def getAllQuotes() -> list[QuoteInfo]:
    quotes : list[QuoteInfo] = []
    dota2Helper = Dota2WikiHelper.RU()
    dota2 = Dota2Wiki(helper=dota2Helper)
    heroes: list[Link] = dota2.getAllHeroes()
    for hero in heroes:
        sounds : list[Link] = dota2.getSoundsByHero(hero)
        for sound in sounds:
            quotes.append(
                QuoteInfo(
                    hero = hero['name'],
                    url = sound['link'],
                    lang = dota2Helper.lang.name,
                    lyrics = sound['name']
                )
            )
    return quotes

quotes = getAllQuotes()

str = json.dumps(quotes, ensure_ascii=False, indent=4).encode("utf8") 

with open("ru_all_data.json", "w", encoding="utf8") as file:
    file.write(str.decode())


