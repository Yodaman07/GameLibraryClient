from flask import Flask, render_template, session, request, escape, jsonify
from dotenv import load_dotenv
import platforms
from userdata import UserData
import os

load_dotenv()

# Xbox cache and load speeds

steam_key = os.getenv("STEAM_API_KEY")

xbl_key = os.getenv("XBL_API_KEY")

secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = secret_key

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
    if not session.get("loggedin"):
        session['loggedin'] = {"state": False, "username": None}

    ud = UserData(username=session['loggedin']['username'])
    service_key = ud.service("get", session['theme'])
    print(service_key)
    if session['loggedin']['state'] and service_key['code'] != 404:
        if session["theme"] == "steam":
            data = platforms.Steam(service_key['msg'], steam_key).games()
            # ['msg'] is used as data in this case. Msg is used for consistency
        elif session["theme"] == "xbox":
            data = platforms.Xbox(service_key['msg'], False).games()
    else:
        data = {}

    return render_template("index.html", gameData=data, themes=themes, currentTheme=session['theme'], loggedin=session['loggedin']['state'])


@app.route('/settings')
def settings():
    if not session.get('item'):
        session['item'] = "profile"
    if not session.get("loggedin"):
        session['loggedin'] = {"state": False, "username": None}
    return render_template("settings.html", sidebar_items=settings_items, currentItem=session['item'],
                           loggedin=session['loggedin']['state'], username=session['loggedin']['username'],
                           themes=themes)


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
    response = {'code': 400, "msg": "REQUEST ERROR"}
    print(f'Account Request Received: {action} ; Method: {request.method}')
    if request.method == "POST":
        if action == "signup":
            ud = UserData(email=request.json['email'], password=request.json['password'])
            response = ud.create_account(request.json['username'])
        elif action == "login":
            ud = UserData(email=request.json['email'], password=request.json['password'])
            response = ud.login()
        elif action == "add_service":
            if session['loggedin']['state']:
                ud = UserData(username=session['loggedin']['username'])
                response = ud.service("add", request.json)
    elif request.method == "GET":
        if "get_service_" in action:
            if session['loggedin']['state']:
                a = action
                serviceName = a.replace("get_service_", "")
                ud = UserData(username=session['loggedin']['username'])
                response = ud.service("get", serviceName)

    if response['code'] == 200 or response['code'] == 201:  # Successful log in
        session['loggedin'] = {"state": True, "username": response['user']}
    return jsonify(escape(response))


if __name__ == '__main__':
    app.run(debug=True)

# host='0.0.0.0', port=2000
