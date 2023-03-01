from flask import Flask, render_template, session, request, escape, url_for, redirect
from dotenv import load_dotenv
import platforms
from flask_socketio import SocketIO
from userdata import UserData
import os

load_dotenv()

steam_key = os.getenv("STEAM_API_KEY")
steam_id = os.getenv("STEAM_ID")

xbl_key = os.getenv("XBL_API_KEY")
xuid = os.getenv("XUID")

secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = secret_key
socketio = SocketIO(app)

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

settings_items = {
    "profile": {'icon': 'static/img/profile.svg'},
    "cache": {'icon': 'static/img/cache.svg'},
    "credits": {'icon': 'static/img/credits.svg'},
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
    if not session.get('item'):
        session['item'] = "profile"
    return render_template("settings.html", sidebar_items=settings_items, currentItem=session['item'], loggedin=False)


@app.route('/data/get_current', methods=["GET", "POST"])
def currentTheme():
    if request.method == "POST":
        if request.json['from'] == "/":
            for i in themes:
                if themes[i]['icon'] == request.json['icon']:
                    session['theme'] = i
            print(f"Redirecting to {session['theme']}")
        elif request.json['from'] == "/settings":
            for i in settings_items:
                if settings_items[i]['icon'] == request.json['icon']:
                    session['item'] = i
            print(f"Redirecting to {session['item']}")
    return escape(request.json)


@app.route('/data/accounts/<action>', methods=['GET', 'POST'])
def accountData(action):
    if action == "signup" and request.method == "POST":
        ud = UserData(request.form['email'], request.form['pswrd'])
        ud.configure_file()
        ca = ud.create_account()

    return redirect(url_for("settings"))


if __name__ == '__main__':
    socketio.run(app, debug=True)

# host='0.0.0.0', port=2000
