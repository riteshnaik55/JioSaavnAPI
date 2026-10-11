from flask import Flask, request, redirect, jsonify, json
import time
import jiosaavn
import os
from traceback import print_exc
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET", 'thankyoutonystark#weloveyou3000')
CORS(app)


@app.route('/')
def home():
    return redirect("https://cyberboysumanjay.github.io/JioSaavnAPI/")


@app.route('/song/')
def search():
    query = request.args.get('query')
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=20, type=int)
    lyrics = request.args.get('lyrics', default='false').lower() == 'true'
    songdata = request.args.get('songdata', default='true').lower() == 'true'

    if query:
        return jsonify(jiosaavn.search_for_song(query, lyrics, songdata, page, limit))
    else:
        return jsonify({"status": False, "error": "Query is required to search songs!"}), 400


@app.route('/song/get/')
def get_song():
    id = request.args.get('id')
    lyrics = request.args.get('lyrics', default='false').lower() == 'true'

    if id:
        resp = jiosaavn.get_song(id, lyrics)
        if not resp:
            return jsonify({
                "status": False,
                "error": 'Invalid Song ID received!'
            }), 404
        return jsonify(resp)
    else:
        return jsonify({
            "status": False,
            "error": 'Song ID is required to get a song!'
        }), 400


@app.route('/playlist/')
def playlist():
    query = request.args.get('query')
    lyrics = request.args.get('lyrics', default='false').lower() == 'true'

    if query:
        id = jiosaavn.get_playlist_id(query)
        songs = jiosaavn.get_playlist(id, lyrics)
        return jsonify(songs)
    else:
        return jsonify({
            "status": False,
            "error": 'Query is required to search playlists!'
        }), 400


@app.route('/album/')
def album():
    query = request.args.get('query')
    lyrics = request.args.get('lyrics', default='false').lower() == 'true'

    if query:
        id = jiosaavn.get_album_id(query)
        songs = jiosaavn.get_album(id, lyrics)
        return jsonify(songs)
    else:
        return jsonify({
            "status": False,
            "error": 'Query is required to search albums!'
        }), 400


@app.route('/lyrics/')
def lyrics():
    query = request.args.get('query')

    if query:
        try:
            if 'http' in query and 'saavn' in query:
                id = jiosaavn.get_song_id(query)
                lyrics_text = jiosaavn.get_lyrics(id)
            else:
                lyrics_text = jiosaavn.get_lyrics(query)
            return jsonify({
                "status": True,
                "lyrics": lyrics_text
            })
        except Exception as e:
            return jsonify({
                "status": False,
                "error": str(e)
            }), 500
    else:
        return jsonify({
            "status": False,
            "error": 'Query containing song link or id is required to fetch lyrics!'
        }), 400


@app.route('/result/')
def result():
    query = request.args.get('query')
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=20, type=int)
    lyrics = request.args.get('lyrics', default='false').lower() == 'true'

    if not query:
        return jsonify({
            "status": False,
            "error": 'Query is required!'
        }), 400

    if 'saavn' not in query:
        return jsonify(jiosaavn.search_for_song(query, lyrics, True, page, limit))

    try:
        if '/song/' in query:
            song_id = jiosaavn.get_song_id(query)
            song = jiosaavn.get_song(song_id, lyrics)
            return jsonify(song)

        elif '/album/' in query:
            id = jiosaavn.get_album_id(query)
            songs = jiosaavn.get_album(id, lyrics)
            return jsonify(songs)

        elif '/playlist/' in query or '/featured/' in query:
            id = jiosaavn.get_playlist_id(query)
            songs = jiosaavn.get_playlist(id, lyrics)
            return jsonify(songs)

    except Exception as e:
        print_exc()
        return jsonify({
            "status": False,
            "error": str(e)
        }), 500

    return jsonify({
        "status": False,
        "error": "Unsupported URL format provided!"
    }), 400


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5100, use_reloader=True, threaded=True)
