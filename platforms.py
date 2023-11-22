import json
import requests


class Cache:
    def __init__(self, cache_file, profile_id):
        self.cache_file = cache_file
        self.profile_id = profile_id

    def configFile(self):
        isCached = False
        data = {
            "profiles": [
                {self.profile_id: []}
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
                print(f"Checking for match with {self.profile_id} with {k}")
                if k == self.profile_id:
                    isCached = True

        if not isCached:
            print("Adding New Profile...")
            loaded["profiles"].append({self.profile_id: []})

        with open(self.cache_file, "w") as f:
            json.dump(loaded, f, indent=True)

    def get(self, appid=None):  # If appid is left unset, all player data will be returned
        with open(self.cache_file, "r") as f:
            loaded = json.load(f)
        for profile in loaded['profiles']:
            for k, value in profile.items():
                if k == self.profile_id:
                    if appid is not None:
                        for game in value:
                            if int(game['appid']) == int(appid):
                                return game
                    else:
                        return value

    def set(self, game_list):  # Only sets individually
        print("Setting...")
        # data is a dict formatted like {"img":img,"achievement_player":a_player,"achievement_game":a_game}
        with open(self.cache_file, "r+") as f:
            loaded = json.load(f)
        with open(self.cache_file, "w") as f:
            for profile in loaded["profiles"]:
                for k, value in profile.items():
                    if k == self.profile_id:
                        profile[self.profile_id] = game_list
            json.dump(loaded, f, indent=True)

    def check_if_data_exists(self, appid, time_last_played):
        game = self.get(appid)
        # print(f"Checking for {game} and {time_last_played}")
        try:
            # game['time_last_played'] is the cached time and the time_last_played is the current val
            if game["time_last_played"] == time_last_played:
                return True
            else:
                return False
        except TypeError:
            pass


class Steam:

    def __init__(self, steamID, api_key):
        self.steamID = steamID
        self.api_key = api_key
        self.cache = Cache("data/steamcache.json", steamID)

    def games(self):

        self.cache.configFile()
        gameList = []

        getDataURL = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.api_key}&steamid={self.steamID}&format=json&include_appinfo=true&include_played_free_games=true"

        r = requests.get(getDataURL)
        if r.status_code == 200:
            for i in r.json()["response"]["games"]:
                if self.cache.check_if_data_exists(i['appid'], i['rtime_last_played']):
                    # TODO (fix) --> Currently doesn't update data for game names
                    print(f"Steam - data exists... ({i['appid']})")
                    game_data = self.cache.get(i['appid'])
                    gameList.append(game_data)
                else:
                    print(f"Steam - getting data... ({i['appid']})")
                    name = i["name"]
                    img = f"https://steamcdn-a.akamaihd.net/steam/apps/{i['appid']}/library_600x900.jpg"
                    alt_img = False
                    if requests.get(img).status_code == 404:
                        img = f"https://steamcdn-a.akamaihd.net/steam/apps/{i['appid']}/header.jpg"
                        alt_img = True

                    timeM = i["playtime_forever"] % 60
                    timeH = i["playtime_forever"] // 60

                    h = f"{timeH} hrs" if timeH > 1 else f"{timeH} hr"
                    m = f"{timeM} mins" if timeM > 1 else f"{timeM} min"
                    time = h + " " + m
                    percent = self.getPercentCompletion(i['appid'], self.steamID)
                    # https://stackoverflow.com/questions/27862725/how-to-get-last-played-on-for-steam-game-using-steam-api

                    gameList.append(  # time_unformatted is in min
                        {"time_last_played": i['rtime_last_played'], "appid": i['appid'], "name": name, "time": time,
                         "time_unformatted": i['playtime_forever'],
                         "img": img, 'alt_img': alt_img,
                         "percent": percent[0], "alt-percent": percent[1]}
                    )
            self.cache.set(gameList)
        return gameList

    def getPercentCompletion(self, appId, steamID):
        totalAchievementsPlayer = 0
        url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appId}&key={self.api_key}&steamid={steamID}"

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


class Xbox:
    def __init__(self, api_key, includeDemos):
        self.api_key = api_key
        self.cache = Cache("data/xboxcache.json", self.api_key)
        self.includeDemos = includeDemos
        self.gamesResponse = {}

    def games(self):
        self.cache.configFile()
        game_list = []
        headers = {"accept": "*/*", 'x-authorization': self.api_key}
        r = requests.get(f"https://xbl.io/api/v2/achievements", headers=headers)
        self.gamesResponse = r.json()

        if r.status_code == 200:
            for game in self.gamesResponse["titles"]:
                if ("XboxOne" or "XboxSeries" or "Xbox360") in game["devices"]:
                    if self.cache.check_if_data_exists(game["titleId"], game['titleHistory']['lastTimePlayed']):
                        print(f"XBOX - data exists... ({game['titleId']})")

                        game_data = self.cache.get(game['titleId'])
                        game_list.append(game_data)
                    else:
                        print(f"XBOX - getting data... ({game['titleId']})")
                        try:
                            percent = self.getPercent(game['titleId'])
                            time = self.getTimePlayed(game['titleId'], True)
                        except KeyError:
                            self.cache.set(game_list)
                            break

                        game_list.append(
                            {"time_last_played": game['titleHistory']['lastTimePlayed'], "appid": int(game['titleId']),
                             "name": game['name'], "time": time,
                             "time_unformatted": self.getTimePlayed(game['titleId'], False),
                             "img": game["displayImage"], 'alt_img': False,
                             "percent": percent[0],
                             "alt-percent": percent[1]}
                        )

        if game_list is not []:
            self.cache.set(game_list)
        return self.checkDemos(game_list)

    def getPercent(self, appid):
        decimal = 0.00
        # print("Getting Percent")
        # Old xbox (360) games require the achievements from the endpoint that gets the games
        # New xbox (one) games require the achievements from the endpoint below
        totalAchievementsPlayer = 0
        headers = {"accept": "*/*", 'x-authorization': self.api_key}
        r = requests.get(f"https://xbl.io/api/v2/achievements/player/{self.getXUID(self.api_key)}/{appid}",
                         headers=headers)
        try:
            totalAchievementsGame = len(r.json()["achievements"])
            for i in r.json()["achievements"]:
                try:
                    if i["progressState"] == "Achieved":
                        totalAchievementsPlayer += 1
                except KeyError:
                    continue
            try:
                decimal = (totalAchievementsPlayer / totalAchievementsGame)
            except ZeroDivisionError:
                req = self.gamesResponse
                for title in req["titles"]:
                    if int(title["titleId"]) == int(appid):
                        ach = title["achievement"]
                        totalAchievementsPlayer = ach["currentAchievements"]
                        totalAchievementsGame = ach["totalAchievements"]
                        decimal = 0 if totalAchievementsGame == 0 else totalAchievementsPlayer / totalAchievementsGame

            return [round(decimal * 100, 2), f"{totalAchievementsPlayer}/{totalAchievementsGame}"]
        except KeyError:
            return [0.00, '0/0']

    def getTimePlayed(self, appid, formatted):
        headers = {"accept": "*/*", 'x-authorization': self.api_key}
        r = requests.get(f"https://xbl.io/api/v2/achievements/stats/{appid}", headers=headers)
        try:
            stats = r.json()['statlistscollection'][0]['stats']
            s = stats[0]
        except IndexError:
            return "N/A"

        try:
            time = int(s['value'])
            if not formatted:
                if time == "N/A":
                    return -1
                else:
                    return time
            minutes = time % 60
            hr = time // 60
            h = f"{hr} hrs" if hr > 1 else f"{hr} hr"
            m = f"{minutes} mins" if minutes > 1 else f"{minutes} min"
            timePlayed = h + " " + m
        except KeyError:
            timePlayed = "N/A"
        return timePlayed

    def checkDemos(self, game_list):
        newlist = game_list.copy()
        if not self.includeDemos:
            for c, i in enumerate(game_list):
                if "demo" in i['name'].lower():
                    newlist.remove(i)
        return newlist

    # XUID isn't necessary
    def getXUID(self, api_key):
        # api_key is already validated
        headers = {"accept": "*/*", "x-authorization": api_key}
        response = requests.get("https://xbl.io/api/v2/player/summary", headers=headers)
        if response.status_code == 200:
            return response.json()['people'][0]['xuid']


class ValidateCredentials:
    def __init__(self, cred):
        self.cred = cred

    def validateSteam(self, api_key):
        response = requests.get(
            f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={self.cred}")
        if response.json()['response']['players']:  # verify account is public and can be reached
            r = requests.get(
                f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={self.cred}&format=json")
            # print(r.json()['response'])
            try:
                if r.json()['response']['game_count']:
                    return {"code": 202, "msg": "Valid Steam Id"}
            except KeyError:
                return {"code": 401, "msg": "Unable to access Steam Account Data; Your account may be private"}
        else:
            return {"code": 404, "msg": "This Steam Account doesn't exist"}

    def validateXbox(self):
        # validate openxbl api key
        headers = {"accept": "*/*", "x-authorization": self.cred}
        response = requests.get("https://xbl.io/api/v2/account", headers=headers)
        if response.status_code == 200:
            return {"code": 202, "msg": "Valid OpenXBL API Key"}
        elif response.status_code == 401:
            return {"code": 401, "msg": "Invalid OpenXBL API Key"}
        else:
            return {"code": 404, "msg": "Unknown error"}
