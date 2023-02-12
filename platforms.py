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

    def get(self, appid):
        with open(self.cache_file, "r") as f:
            loaded = json.load(f)
        for profile in loaded['profiles']:
            for k, value in profile.items():
                if k == self.profile_id:
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
                    if k == self.profile_id:
                        profile[self.profile_id] = game_list
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


class Steam:

    def __init__(self, steamID, api_key):
        self.steamID = steamID
        self.api_key = api_key
        self.cache = Cache("steamcache.json", steamID)

    def games(self):

        self.cache.configFile()
        gameList = []

        getDataURL = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.api_key}&steamid={self.steamID}&format=json&include_appinfo=true&include_played_free_games=true"

        r = requests.get(getDataURL)
        for i in r.json()["response"]["games"]:
            if self.cache.check_if_data_exists(i['appid'], i['rtime_last_played']):
                game_data = self.cache.get(i['appid'])
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
                percent = self.getPercentCompletion(i['appid'], self.steamID)
                # https://stackoverflow.com/questions/27862725/how-to-get-last-played-on-for-steam-game-using-steam-api

                gameList.append(
                    {"time_last_played": i['rtime_last_played'], "appid": i['appid'], "name": name, "time": time,
                     "img": img,
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
    def __init__(self, xuid, api_key):
        self.xuid = xuid
        self.api_key = api_key
        self.cache = Cache("xboxcache.json", xuid)

    def games(self):
        self.cache.configFile()
        game_list = []
        headers = {"accept": "*/*", 'x-authorization': self.api_key}
        r = requests.get(f"https://xbl.io/api/v2/achievements/player/{self.xuid}", headers=headers)

        for game in r.json()["titles"]:
            if self.cache.check_if_data_exists(game["titleId"], game['titleHistory']['lastTimePlayed']):
                game_data = self.cache.get(game['appid'])
                game_list.append(game_data)
            else:
                game_list.append(
                    {"time_last_played": game['titleHistory']['lastTimePlayed'], "appid": game['titleId'], "name": game['name'], "time": '0',
                    "img": game["displayImage"],
                    "percent": game["achievement"]["progressPercentage"], "alt-percent": str(game["achievement"]["currentAchievements"]) + "/" + str(game["achievement"]["totalAchievements"])}
                )
        self.cache.set(game_list)
        return game_list

