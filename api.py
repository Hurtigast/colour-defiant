import requests # type: ignore
import json
from os import environ
from bs4 import BeautifulSoup # type: ignore
from dotenv import load_dotenv
from urllib.parse import quote


load_dotenv()

api_key = environ.get('api_key')

url = "https://euw1.api.riotgames.com"

user = environ.get('user')


class Player:
    def __init__(self, puuid, teamId, spell1Id, spell2Id, championId, profileIconId,
                 riotId, bot, summonerId, gameCustomizationObjects, perks):
        self.puuid = puuid
        self.teamId = teamId
        self.spell1Id = spell1Id
        self.spell2Id = spell2Id
        self.championId = championId
        self.profileIconId = profileIconId
        self.riotId = riotId
        self.bot = bot
        self.summonerId = summonerId
        self.gameCustomizationObjects = gameCustomizationObjects
        self.perks = perks

    def __str__(self):
        return f'"{self.riotId}"'

class GameData:
    class Observer:
        def __init__(self, encryptionKey):
            self.encryptionKey = encryptionKey

    class BannedChampion:
        def __init__(self, championId, teamId, pickTurn):
            self.championId = championId
            self.teamId = teamId
            self.pickTurn = pickTurn

    def __init__(self, gameId, mapId, gameMode, gameType, gameQueueConfigId, observer, platformId, bannedChampions, gameStartTime, gameLength):
        self.gameId = gameId
        self.mapId = mapId
        self.gameMode = gameMode
        self.gameType = gameType
        self.gameQueueConfigId = gameQueueConfigId
        self.observer = observer
        self.platformId = platformId
        self.bannedChampions = bannedChampions
        self.gameStartTime = gameStartTime
        self.gameLength = gameLength

    def __str__(self):
        return f'"{self.gameId}"'

#Convert username to puuid
def get_puiid(name,tag):
    region = "europe"
    url = "https://" + region + ".api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + quote(name) + "/" + quote(tag) + "?api_key=" + api_key

    response = requests.get(url)
    if response.status_code == 200:
        data_json = response.json()
        puuid = data_json.get("puuid")
        return puuid
    
    else:
        return False

#Get match and populate classes
def get_match(user):
    #Gets match details and players
    endpoint = "/lol/spectator/v5/active-games/by-summoner/" + user

    response = requests.get(url + endpoint + "?api_key=" + api_key)

    print(url + endpoint + "?api_key=" + api_key)

    #Extract players and match data
    if response.status_code == 200:
        data_json = response.json()
        match_data = data_json.get("participants", [])
        players = []

        #Extract players
        for participant_data in match_data:
            player = Player(
                puuid=participant_data.get("puuid"),
                teamId=participant_data.get("teamId"),
                spell1Id=participant_data.get("spell1Id"),
                spell2Id=participant_data.get("spell2Id"),
                championId=participant_data.get("championId"),
                profileIconId=participant_data.get("profileIconId"),
                riotId=participant_data.get("riotId"),
                bot=participant_data.get("bot"),
                summonerId=participant_data.get("summonerId"),
                gameCustomizationObjects=participant_data.get("gameCustomizationObjects", []),
                perks=participant_data.get("perks", {})
            )
            players.append(player)

        #Add players into a dictionary
        players_dic = {f'var{i+1}': players[i] for i in range(len(players))}

        #Delete participants
        del data_json["participants"]

        #Extract observers
        observer = GameData.Observer(encryptionKey=data_json['observers']['encryptionKey'])

        #Extract banned champions
        banned_champions = []
        for ban in data_json['bannedChampions']:
            banned_champion = GameData.BannedChampion(championId=ban['championId'], teamId=ban['teamId'], pickTurn=ban['pickTurn'])
            banned_champions.append(banned_champion)
        
        #Extract match data
        game_data = GameData(
            gameId=data_json['gameId'],
            mapId=data_json['mapId'],
            gameMode=data_json['gameMode'],
            gameType=data_json['gameType'],
            gameQueueConfigId=data_json['gameQueueConfigId'],
            observer=observer,
            platformId=data_json['platformId'],
            bannedChampions=banned_champions,
            gameStartTime=data_json['gameStartTime'],
            gameLength=data_json['gameLength']
        )
        print(players[0].puuid)
        return(players)

    else:
        return(f"No active match for that player")

#Get all champions from current patch
def get_champs():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json() 
    
    if isinstance(data, list) and len(data) > 0:
        lol_version = data[0] 

    else:
        print("The data is either not a list or is an empty list.")

    url = "https://ddragon.leagueoflegends.com/cdn/" + lol_version + "/data/en_US/champion.json"
    response = requests.get(url)
    if response.status_code == 200:
        champions_json = response.json()
        #champions_data_json = json.dumps(data_json, indent=4)
        return champions_json

#Match champ key to champ name
def find_champ(data, search_value):
    for key, value in data.items():
        # If the current value is a dictionary, check if it has the desired key-value pair
        if isinstance(value, dict) and value.get("key") == search_value:
            return value.get('name')  # Return the 'name' value
        # Recursively search within the dictionary
        if isinstance(value, dict):
            result = find_champ(value, search_value)
            if result:
                return result

def convert_gameid(gameid):
    endpoint = "/lol/spectator/v5/featured-games"
    response = requests.get(url + endpoint + "?api_key=" + api_key)
    data_json = response.json()

#Get featured match
def featured_match():
    endpoint = "/lol/spectator/v5/featured-games"
    response = requests.get(url + endpoint + "?api_key=" + api_key)
    data_json = response.json()
    print(json.dumps(data_json, indent=4))
    

#print(find_champ(get_champs(), "266"))
#get_match(user)
#featured_match()
