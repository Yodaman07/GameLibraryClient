from flask import Flask, render_template, session, request, escape
from dotenv import load_dotenv
import platforms
import os

load_dotenv()

steam_key = os.getenv("STEAM_API_KEY")
steam_id = os.getenv("STEAM_ID")

xbl_key = os.getenv("XBL_API_KEY")
xuid = os.getenv("XUID")

secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = secret_key
# Websocket?

# [BG1, BG2, GameBG, SidebarBG, Sel, Highlight color, Text]
themes = {
    "steam": {'colors': ["#6197FF", "#1F407E", "#1E5FDE", "#364561", "#80A9F6", "", "#FFFFFF"],
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
    data = {}
    if not session.get('theme'):
        session['theme'] = "steam"
    if session["theme"] == "steam":
        data = platforms.Steam(steam_id, steam_key).games()
    elif session["theme"] == "xbox":
        data = platforms.Xbox(xuid, xbl_key, False).games()

    return render_template("index.html", gameData=data, themes=themes, currentTheme=session['theme'])


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
    return escape(request.json)


if __name__ == '__main__':
    app.run(debug=True)
