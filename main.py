from flask import Flask, render_template, session, request
from dotenv import load_dotenv
# from datetime import datetime
import requests
import json
import os


class SteamCache:
    def __init__(self, steamid):
        self.steamid = steamid
        self.cache_file = "steamcache.json"

    def configFile(self):
        isCached = False
        data = {
            "profiles": [
                {self.steamid: []}
            ]
        }

        with open(self.cache_file, "r+") as f:
            if str(f.read()) == "":
                json.dump(data, f)

        # Checks if the id is already saved
        # We can't use "w+" as that resets the file
        # We can't combine the 2 "r+" parts as you need to close the file after the dump
        with open(self.cache_file, "r+") as f:
            loaded = json.load(f)

        for profile in loaded["profiles"]:
            for k, value in profile.items():
                print(f"Checking for match with {self.steamid} with {k}")
                if k == self.steamid:
                    isCached = True

        if not isCached:
            print("Adding New Profile...")
            loaded["profiles"].append({self.steamid: []})

        with open(self.cache_file, "w") as f:
            json.dump(loaded, f, indent=True)

    def get(self, appid):
        with open(self.cache_file, "r") as f:
            loaded = json.load(f)
        for profile in loaded['profiles']:
            for k, value in profile.items():
                if k == self.steamid:
                    for game in value:
                        if game['appid'] == int(appid):
                            return game

    def set(self, game_list):
        print("Setting...")
        # data is a dict formatted like {"img":img,"achievement_player":a_player,"achievement_game":a_game}
        with open(self.cache_file, "r+") as f:
            loaded = json.load(f)
        with open(self.cache_file, "w") as f:
            for profile in loaded["profiles"]:
                for k, value in profile.items():
                    if k == self.steamid:
                        profile[self.steamid] = game_list
            json.dump(loaded, f, indent=True)

    def check_if_data_exists(self, appid, time_last_played):
        game = self.get(appid)
        try:
            # game['time_last_played'] is the cached time and the time_last_played is the current val
            if game["time_last_played"] == time_last_played:
                return True
            else:
                return False
        except TypeError:
            pass


load_dotenv()

key = os.getenv("API_KEY")
steam_id = os.getenv("STEAM_ID")
secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = secret_key
# Websocket
# [BG1, BG2, GameBG, SidebarBG, Sel, Highlight color, Text]
themes = {
    "steam": {'colors': ["#6197FF", "#1F407E", "#1E5FDE", "#364561", "#80A9F6", "","#FFFFFF"],
              'icon': '/static/img/steam.svg'},
    "xbox": {'colors': ["#48BD4C", "#18641B", "#2ebf34", "#386D3A", "#82C985", "#FFFFFF"],
             'icon': '/static/img/xbox.svg'},
    "playstation": {'colors': ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
                    'icon': '/static/img/playstation.svg'},
    "switch": {'colors': ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
               'icon': '/static/img/switch.svg'}
}


@app.route('/')
def home():
    if not session.get('theme'):
        session['theme'] = "steam"
    return render_template("index.html", gameData=getSteamGames(steam_id), themes=themes, currentTheme=session['theme'])


@app.route('/settings')
def settings():
    return render_template("settings.html")


@app.route('/data/current_theme', methods=["GET", "POST"])
def currentTheme():
    if request.method == "POST":
        for i in themes:
            if themes[i]['icon'] == request.json['theme_icon']:
                session['theme'] = i
        print(f"Redirecting to {session['theme']}")
    return request.json


def getSteamGames(steamID):
    sc = SteamCache(steamID)
    sc.configFile()
    gameList = []

    getDataURL = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamID}&format=json&include_appinfo=true&include_played_free_games=true"

    r = requests.get(getDataURL)
    for i in r.json()["response"]["games"]:
        if sc.check_if_data_exists(i['appid'], i['rtime_last_played']):
            game_data = sc.get(i['appid'])
            gameList.append(game_data)
        else:
            name = i["name"]
            img = f"https://steamcdn-a.akamaihd.net/steam/apps/{i['appid']}/library_600x900.jpg"
            if requests.get(img).status_code == 404:
                img = f"https://steamcdn-a.akamaihd.net/steam/apps/{i['appid']}/header.jpg"

            timeM = i["playtime_forever"] % 60
            timeH = i["playtime_forever"] // 60

            if timeH > 1:
                h = f"{timeH} hrs"
            elif timeH == 1:
                h = f"{timeH} hr"
            else:
                h = f"0 hr"
            m = f"{timeM} mins" if timeM > 1 else f"{timeM} min"
            time = [h, m]
            percent = getPercentCompletion(i['appid'], steamID)
            # https://stackoverflow.com/questions/27862725/how-to-get-last-played-on-for-steam-game-using-steam-api

            gameList.append(
                {"time_last_played": i['rtime_last_played'], "appid": i['appid'], "name": name, "time": time,
                 "img": img,
                 "percent": percent[0], "alt-percent": percent[1]}
            )

    sc.set(gameList)
    return gameList


def getPercentCompletion(appId, steamID):
    totalAchievementsPlayer = 0
    url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appId}&key={key}&steamid={steamID}"

    r = requests.get(url).json()

    try:
        totalAchievementsGame = len(r["playerstats"]["achievements"])
        for i in r["playerstats"]["achievements"]:
            if i["achieved"] == 1:
                totalAchievementsPlayer += 1

        decimal = (totalAchievementsPlayer / totalAchievementsGame)
        return [round(decimal * 100, 2), f"{totalAchievementsPlayer}/{totalAchievementsGame}"]
    except KeyError:
        return [0.00, '0/0']


if __name__ == '__main__':
    app.run(debug=True)
