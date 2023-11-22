import string


class GameSort:
    def __init__(self, game_list):
        self.game_list = game_list

    def search(self, query):
        filteredList = []
        charlist = list(string.punctuation + "™" + "®")
        for game in self.game_list:
            savedNameFiltered = game['name'].lower()
            q = query.lower()
            for i in charlist:
                savedNameFiltered = savedNameFiltered.replace(i, "")
            if (q in game['name'].lower()) or (q in game['name'].lower().replace("-", " ")) or (q in savedNameFiltered):
                filteredList.append(game)
        return filteredList

    def sort(self, method):
        return_list = []
        gl = self.game_list
        key = ''
        if method[0] == "a": #A->Z
            key = 'name'
        elif method[0] == "t": #time
            key = 'time_unformatted'
        elif method[0] == "p":  # precent
            key = 'percent'
        elif method[0] == "d": #default
            return_list = gl

        if method[-2:] == "_a":  # default is ascending (false)
            return_list = sorted(gl, key=lambda x: x[key], reverse=False)
        elif method[-2:] == "_d":
            return_list = sorted(gl, key=lambda x: x[key], reverse=True)

        return return_list
