import os
import youtube
import base64
import bpm
from pytube import YouTube
from pymongo import MongoClient
from flask import Flask, render_template, request, url_for, send_from_directory, make_response, send_file, jsonify

app = Flask(__name__)
client = MongoClient('localhost', 27017)

db = client.prj4
wav_path = os.getcwd() + "/static/temp/youtube_wav"

def encodeString(string: str) :
    return base64.b64encode(string.encode('utf-8'))

# Sample
@app.route('/')
def sample_home():
    return render_template('sample.html')

@app.route('/input')
def sample_input():
    return render_template('sample_input.html')

@app.route('/test')
def test_():
    return "hello world"

@app.route('/api/youtube/upload')
def youtube_upload():
    print("> Youtube Upload")

    #bpm_yt, sync_info = bpm.bpm_and_sync('./static/temp/youtube_wav/MVZICO지코Anysong아무노래.wav')

    try:
        url = request.args.get('url')
        yt = YouTube(url)

        title = yt.title
        duration = yt.length
        email = request.args.get('email')

        filename = youtube.get_audio(url)

        print("here")
        print('./static/temp/youtube_wav/' + filename + '.wav')

        bpm_yt, sync_info = bpm.bpm_and_sync('./static/temp/youtube_wav/' + filename + '.wav')

        print("here2")

        if (title == None):
            title = YouTube(url).title
        if (email == None):
            email = ""
         
        collection = db.audio
        my_document = {'url': url, 'email': email, 'title': title, 'filename': filename, 'duration': duration, 'bpm':bpm_yt, 'sync_info': sync_info}
        print(my_document)

        try:
            collection.insert_one(my_document)
        except:
            return "duplicated"
        
        return "success"
    except:
        return "fail", 500

########## Youtube Audio Download API ##########
@app.route('/api/youtube/download')
def youtube_download():
    print("> Youtube Download")
    global wav_path

    title = request.args.get('title')
    url = request.args.get('url')
    email = request.args.get('email')
    collection = db.audio
    my_query = dict()

    # Make a query
    if (title != None):
        my_query['email'] = email
        my_query['title'] = title
    elif (url != None):
        my_query['url'] = url
    else:
        return "Invalid request", 500

    result = collection.find_one(my_query)

    # Find a .wav file and send it.
    # If there is no such file, download it from Youtube.
    if (result == None):
        try:
            yt = YouTube(url)

            title = yt.title
            duration = yt.length
            email = ""
            filename = youtube.get_audio(url)

            bpm_yt, sync_info = bpm.bpm_and_sync(wav_path + filename + '.wav')
            
            my_document = {'url': url, 'email': email, 'title': title, 'filename': filename, 'duration': duration, 'bpm':bpm_yt, 'sync_info': sync_info}
            try:
                collection.insert_one(my_document)
            finally:
                return send_file(wav_path + "/" + filename + ".wav")
        except:
            return "Invalid request", 500
    else:
        return send_file(wav_path + "/" + result['filename'] + ".wav")

@app.route('/api/youtube/download/meta')
def youtube_download_meta() :
    print("> Youtube Download Meta")
    global wav_path

    title = request.args.get('title')
    url = request.args.get('url')
    email = request.args.get('email')
    collection = db.audio
    my_query = dict()

    # Make a query
    if (title != None):
        my_query['email'] = email
        my_query['title'] = title
    elif (url != None):
        my_query['url'] = url
    else:
        return "Invalid request", 500

    result = collection.find_one(my_query, { 'duration': 1, 'title': 1, 'bpm':1, 'sync_info':1, '_id': 0 })

    # Get meta data of an audio file from audio DB, and return it.
    # If there is no data in the DB, get them from Youtube.
    if (result == None):
        try:
            yt = YouTube(url)
            title = encodeString(yt.title).decode('UTF-8')
            length = yt.length
        
            my_document = {'title': title, 'length': length}

            return my_document
        except:
            return "Invalid request", 500
    else:
        result['title'] = encodeString(result['title']).decode('UTF-8')
        return jsonify(result)

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)