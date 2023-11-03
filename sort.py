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
        if method[0] == "a":
            gl = self.game_list
            if method[-2:] == "_a":  # default is ascending (false)
                return_list = sorted(gl, key=lambda x: x['name'], reverse=False)
            elif method[-2:] == "_d":
                return_list = sorted(gl, key=lambda x: x['name'], reverse=True)
        elif method[0] == "d":
            return_list = self.game_list

        return return_list
