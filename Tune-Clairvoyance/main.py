from flask import Flask, render_template, redirect, request, session, make_response,session,url_for, jsonify, flash
import spotipy
import spotipy.util as util
import time
import xlwt
import json
import csv
#from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import re   
import math

  
regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'  
sc = StandardScaler()  


database = pd.read_excel("dataset/Song_dataset.xls")
user_info = pd.read_csv("dataset/user_info.csv")

app = Flask(__name__)
app.secret_key ="Shrijit"
#app.secret_key = SSK


#-------------------------------------------------------------------------
API_BASE = 'https://accounts.spotify.com'

# Make sure you add this to Redirect URIs in the setting of the application dashboard
REDIRECT_URI = "http://127.0.0.1:5000/api_callback"

SCOPE = 'playlist-modify-private,playlist-modify-public,user-top-read'

# Set this to True for testing but you probaly want it set to False in production.
SHOW_DIALOG = True

#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/User_info"
#db = SQLAlchemy(app)
artistName = set(database["Artist"])
songGenre = set(database["Song_Genre"])
#artistTrack = set(database["Tracks"])


@app.route('/')
def home():
    print("Episode: 1", ", Rewards")
    print("Episode: 2", ", Rewards")
    print("Episode: 3", ", Rewards")
    print("Episode: 4", ", Rewards")
    print("Episode: 5", ", Rewards")
    print("Episode: 6", ", Rewards")

    #if 'email' in session:
        #return f'Logged in as {session["Email"]}'
    return render_template("index.html")

@app.route('/index')
def index():
    return render_template("index.html")

@app.route("/logout",methods=["POST","GET"])
def logout():
    if session["email"]:
        session.pop("email", None)
    return redirect(url_for("login"))

@app.route("/login",methods=["POST","GET"])
def login():
    #error = check(request.form["Email"])
    if request.method == "POST":
        email = request.form["Email"]
        error = check(email)
        #password = request.form["password"]
        if user_info["Email"].str.contains(email).any():# & user_info["Password"].str.contains(password).any():
            session["email"] = email
            print("Successful Login")
            return redirect(url_for("profile"))
        elif error == True: 
            print("ASDWSDW")
            session["email"] = email
            return redirect(url_for("info")) 
        else:
            print("ERROR REPORT")
            return render_template("login.html")       
    else:
        return render_template("login.html")

@app.route("/info",methods = ["POST","GET"])
def info():
    if request.method == "POST":
        artist = request.form.getlist("artist")
        genre = request.form.getlist("genre")
        session["artist"] = artist
        session["genre"] = genre
        email = session["email"]
        gender = request.form["gender"]
        session["gender"] = gender
        favourite = []
        #favourite = 
        #session["genre"] = genre
        row = [email,genre,artist,gender,favourite]
        #row = {"name":name,"email":email,"genres":genre,"artist":artist}
        with open("dataset/user_info.csv", "a") as csvFile:
            writer = csv.writer(csvFile)
            #csvFile.write("\n")
            writer.writerow(row)
            # user_info.append(row, ignore_index=True)
            # user_info.to_csv("dataset/user_info.csv", index=False)
        csvFile.close()
        return redirect(url_for("profile"))
    else:
        return render_template("info.html", artistName = artistName, songGenre = songGenre)

@app.route("/mood",methods = ["POST","GET"])
def mood():
    if request.method == "POST":
        mood = request.form.getlist("mood imgbackground")
        for i in mood:
            uri = get_mood(i, database)
        print("MOOOOOOOOOOD",uri)
        returnValue = render_template("mood-search.html", temp = uri)
    else:
        returnValue = render_template("mood.html")
    return returnValue

@app.route("/song-search",methods = ["POST","GET"])
def song_search():
    if request.method == "POST":
        songRequest = request.form["search"]
        songRequest = songRequest.lower()  
        print("SEARCHSOOOONG", songRequest) 
        returnValue = redirect(url_for("content",song = songRequest))
    else:
        #flash("") 
        returnValue = render_template("song-search.html")
    return returnValue
    
@app.route("/favourite")
def favourite():
    if request.method == "POST":
        song = request.form["song"] 
        #session['Song'] = song
        print("FAVOURITECHECK: ", song)
        returnValue =  redirect(url_for("favourite_results"))
    else:
        print("lol123lol123")
        #found = list(database[database["Tracks"] == song]["uri"])[0]
        returnValue = render_template("favourite.html")#, found = found)
    return returnValue

@app.route("/favourite-results")
def favourite_results():
    if request.method == "POST":
        song = request.form["favourite"] 
        song = get_song_from_uri(song)
        #session['Song'] = song
        print("FAVOURITE-RESULT-CHECK: ", song)
        returnValue =  redirect(url_for("favourite",song = song))
    else:
       
        returnValue = render_template("favourite_results.html")
    return returnValue
    
#     print("loaded")
#     #temp2 = session[email]
#     #list_of_str = ['Name', 'Email', 'Genres', 'Artist', 'Gender', 'Favourite']
#     temp = user_info[user_info["Email"] == session["email"]].index.values[0]
#     returnValue = []
#     row = []
#     with open("dataset/user_info.csv", "a") as csvFile:
#         writer = csv.writer(csvFile)
#         writer[temp][5] = URI
#         print(writer)
#         #csvFile.write("\n")
#         writer.writerow(writer)
#         returnValue = True
#         # user_info.append(row, ignore_index=True)
#         # user_info.to_csv("dataset/user_info.csv", index=False)
#     csvFile.close()
    return returnValue

# @app.route("/search",methods=["POST","GET"])
# def search():
#     if request.method == "POST":
#         song = request.form["song"] 
#         #session['Song'] = song
#         print("ERRORONUS: ", song)
#         return redirect(url_for("content",song = song))
#     else:
#         #print("TESTINGTON: ", session['Song'])
#         print("TESTER", session["artist"])
#         return render_template("search.html", temp = get_artist_songs(session["artist"]))
             
@app.route("/profile",methods=["POST","GET"])
def profile():
    if request.method == "POST":
        song = request.form["song"] 
        #session['Song'] = song
        print("PROFILEERRORCHECK: ", song)
        return redirect(url_for("content",song = song))
    else:
        #print("TESTINGTON: ", session['Song'])
        if request.form.get("favourite"):
            uri = request.form.get("favourite")
            set_favourite(uri)
            return render_template("favourite.html", URI = uri)
        return render_template("profile.html", temp = get_artist_songs(session["artist"]), temp1 = get_genres(session["genre"]))

@app.route("/<song>", methods=["POST", "GET"])
def content(song): 
    try:
        if request.method == 'GET':# and Form.validate():
            found = list(database[database["Tracks"] == song]["uri"])[0]
            recommendation = get_recommendations(song) 
            print("THIS IS A GET SONG REQUEST:", found)
            return render_template("content.html",Recommendation = recommendation, found = found)#,Track = track,Artist = artist,Uri = uri,Recommendation = recommendation)    
        else:
            found = request.form['favourite']
            if song == "favourite_results":
                print(song, " ", found)
                set_favourite(found)
                session["favourite"] = found
                return redirect(url_for("favourite_results"))
            return render_template("song-search.html")
    except:
        print("THIS IS A EXCEPTION:", song)
        #requestForm = request.form['favourite']
        #print("THIS IS A EXCEPTION:", requestForm)
        return redirect(url_for("song_search"))

  
content_input = database.drop(["Artist","Tracks","uri","Genres","duration_ms","Song_Genre"],axis = 1)
content_input[content_input.columns[content_input.dtypes == "float64"].values] = sc.fit_transform(content_input[content_input.columns[content_input.dtypes == "float64"].values])   
content_similarity = cosine_similarity(content_input)
content_similarity_df = pd.DataFrame(content_similarity,index = content_input.index,columns = content_input.index)

def get_recommendations(song):
    print("GET_RECOMMENDATOIN",song)
    id = database[database["Tracks"]== song].index.values[0]
    temp = content_similarity_df[id].sort_values(ascending = False).index.values[1:19]
    per = []
    for y in temp:
        x = content_similarity_df.at[y,id]
        per.append(str(math.floor(x*100000000)/1000000))
    link = list(database.iloc[temp]["uri"])
    #recommendation = set([i +" by " + j + " : " +  k for i,j,k in zip(x,y,z)])
    return zip(link, per)

def get_artist_songs(artist):
    link = []
    for name in artist:
        z = (database[(database['Artist'] == name)].sample(n = 3))["uri"]   
        #y = (database[(database['Artist'] == name)].sample(n = 3))["Tracks"]   
        link.append(z)
    return link

# def get_mood_songs(mood):
#     return {""}
#     return returnValue

def set_favourite(URI):
    print("loaded")
    email = user_info[user_info["Email"] == session["email"]].index.values[0]
    artist = user_info["Artist"][user_info["Email"] == session["email"]]
    genre = user_info["Genres"][user_info["Email"] == session["email"]]
    gender = user_info["Gender"][user_info["Email"] == session["email"]]
    favourite = user_info["Favourite"][user_info["Email"] == session["email"]]
    temp = []
    print("Test:", favourite, "Also", temp)
    if favourite == temp:
        favourite.append[URI]
        print("1",artist," ", genre, " ", gender, " ",favourite)
    else:
        favourite = user_info["Favourite"][user_info["Email"] == session["email"]]
        favourite.append[URI]
        print("2",artist," ", genre, " ", gender, " ",favourite)
    #
    row = [email,genre,artist,gender,favourite]
    #row = {"name":name,"email":email,"genres":genre,"artist":artist}
    if email == user_info["Email"].index.values[0]:
        with open("dataset/user_info.csv", "a") as csvFile:
            writer = csv.writer(csvFile)
            #csvFile.write("\n")
            writer.writerow(row)
            print(writer)
            # user_info.append(row, ignore_index=True)
            # user_info.to_csv("dataset/user_info.csv", index=False)
        csvFile.close()
        returnValue = True
        #temp2 = session[email]
        #list_of_str = ['Name', 'Email', 'Genres', 'Artist', 'Gender', 'Favourite']
        #temp = user_info[user_info["Email"] == session["email"]].index.values[0]
    else:
        returnValue = False
    return returnValue

def get_song_from_uri(URI):
    return list((database[(database['uri'] == URI)])["Tracks"])[0]

def get_mood(y,x):
    if y == "calm":
        x = x[(x["instrumentalness"] > (80*x["instrumentalness"].max())/100) & (x["acousticness"] > (80*x["acousticness"].max())/100) & (x["loudness"] < (20*x["loudness"].max())/100) & (x["liveness"] < (20*x["liveness"].max())/100) ].sample(n=9)["uri"]
    elif y == "energetic":
        x = x[(x["energy"] > (80*x["energy"].max())/100) & (x["tempo"] > (80*x["tempo"].max())/100) & (x["acousticness"] < (20*x["acousticness"].max())/100) & (x["liveness"] < (20*x["liveness"].max())/100)].sample(n=9)["uri"]
    elif y == "happy":
        x = x[(x["danceability"] > (80*x["danceability"].max())/100) & (x["valence"] > (80*x["valence"].max())/100) & (x["energy"] > (60*x["energy"].max())/100) & (x["liveness"] < (20*x["liveness"].max())/100)].sample(n=9)["uri"]
    elif y == "sad":
        x = x[(x["danceability"] < (20*x["danceability"].max())/100) & (x["energy"] < (20*x["valence"].max())/100) & (x["tempo"] < (30*x["energy"].max())/100) & (x["liveness"] < (20*x["liveness"].max())/100)].sample(n=9)["uri"]
    elif y == "live":
        x = x[(x["liveness"] > (90*x["liveness"].max())/100)].sample(n=9)["uri"]
    #x = list(x["uri"])
    return x    

def check(email):   
    if(re.search(regex,email)):   
        print("Valid Email")   
        return True
    else:   
        print("Invalid Email")  
        return False

def get_genres(genre):
    link = []
    for name in genre:
        z = (database[(database['Song_Genre'] == name)].sample(n = 3))["uri"]
        link.append(z)
    return link


if __name__ == "__main__":
    app.run(debug = True) 