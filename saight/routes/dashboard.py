import os
import pathlib

import requests
from saight import app
from flask import Flask, render_template, session, abort, redirect, request, url_for
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import os
import pathlib

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

print("started db script")

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "url_here",
})





client_secrets_file = os.path.join("client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="callback uri")

def login_is_required(func):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            abort(401)
        else:
            return func()
    return wrapper


@app.route('/login', methods=['GET'])
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route('/callback', methods=['GET'])
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get('sub')
    session["name"] = id_info.get('name')
    return redirect("/dashboard")





@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect("/")

global ref 
ref = db.reference("Users")

@app.route('/maps', methods=['GET'])
def maps():
    
    return render_template("maps.html")

@app.route('/dashboard', methods=['GET'])
@login_is_required
def dashboard():

    full_name = str(session["name"])

    global ref
    users = ref.get()

    data = []
    data2 = []


    for user in users:
            data.append((str(users[user]["name"]), int(users[user]["times_seen"])))
            data2.append((str(users[user]["name"]), users[user]["last_seen"]))


    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    labels_last_seen = [row[0] for row in data2]
    values_last_seen = [row[1] for row in data2]



    # render registration page
    return render_template('dashboard.html', maps_key=str(maps_key), full_name=full_name, users=users, labels=labels, values=values, labels_last_seen=labels_last_seen, values_last_seen=values_last_seen)