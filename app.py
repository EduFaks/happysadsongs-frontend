from flask import Flask, redirect, url_for, session, request, render_template
import urllib.parse
from datetime import timedelta

import requests

from api.keys import spotify_id, return_url
from api.spotify_api import GenToken, GetCustomList, GetTracksSpecs
from api.xmatch_api import GetLyricsFromCustom, GetLyricsFromName

app = Flask(__name__)
app.secret_key = 'spotify_secret'
app.permanent_session_lifetime = timedelta(minutes=5)

spotify_scope = "user-read-recently-played"

@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    parms = {'client_id':spotify_id, 'redirect_uri':return_url, 'response_type':'code', 'scope':spotify_scope}
    parm = urllib.parse.urlencode(parms)
    return redirect(
        f'https://accounts.spotify.com/authorize?{parm}'
    )


@app.route('/login/authorized')
def spotify_authorized():
    session['token'] = GenToken(request.args.get('code')).json()
    return redirect(url_for('home'))


@app.route('/listplayed')
def listplayed():
    if len(session['token']) < 20:
        return redirect(url_for('home'))
    session.permanent = True
    return GetCustomList(session['token'])


@app.route('/listplayedlyrical')
def listplayedlyrical():
    if len(session['token']) < 20:
        return redirect(url_for('home'))
    session.permanent = True
    custom = GetCustomList(session['token'])
    return GetLyricsFromCustom(custom)


@app.route('/listplayedfeatures')
def listplayedfeatures():
    if len(session['token']) < 20:
        return redirect(url_for('home'))
    session.permanent = True
    custom = GetCustomList(session['token'])
    return GetTracksSpecs(session['token'], custom)


@app.route('/listplayedfull')
def listplayedfull():
    if len(session['token']) < 20:
        return redirect(url_for('home'))
    session.permanent = True
    custom = GetCustomList(session['token'])
    custom = GetTracksSpecs(session['token'], custom)
    return GetLyricsFromCustom(custom)


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/lyrics')
def lyrics():
    if len(session['token']) < 20:
        return redirect(url_for('home'))
    return GetLyricsFromName(request.args.get('name'))


if __name__ == "__main__":
    app.run()
