import os
import youtube
from pytube import YouTube
from pymongo import MongoClient
from flask import Flask, render_template, request, url_for, send_from_directory, make_response, send_file

app = Flask(__name__)
client = MongoClient('localhost', 27017)

db = client.prj4
wav_path = os.getcwd() + "/static/temp/youtube_wav"

# Sample
@app.route('/')
def sample_home():
    return render_template('sample.html')

@app.route('/input')
def sample_input():
    return render_template('sample_input.html')

# Test
@app.route('/test')
def test_():
    return "hello world"

@app.route('/api/youtube/upload')
def youtube_upload():
    print("> Youtube Upload")
    try:
        url = request.args.get('url')
        title = request.args.get('title')
        email = request.args.get('email')
        filename = youtube.get_audio(url)

        if (title == None):
            title = YouTube(url).title
        if (email == None):
            email = ""
         
        collection = db.audio
        my_document = {'url': url, 'email': email, 'title': title, 'filename': filename}
        try:
            collection.insert_one(my_document)
        except:
            return "duplicated"
        
        return "success"
    except:
        return "fail", 500

@app.route('/api/youtube/download')
def youtube_download():
    print("> Youtube Download")
    global wav_path

    title = request.args.get('title')
    url = request.args.get('url')
    email = request.args.get('email')

    collection = db.audio
    my_query = dict()

    if (title != None):
        my_query['email'] = email
        my_query['title'] = title

        result = collection.find_one(my_query)

        if (result == None):
            return "Invalid request", 500
        else:
            return send_file(wav_path + "/" + result['filename'] + ".wav")
    elif (url != None):
        my_query['url'] = url

        result = collection.find_one(my_query)
        if (result == None):
            try:
                url = request.args.get('url')
                title = YouTube(url).title
                email = ""
                filename = youtube.get_audio(url)
                
                collection = db.audio
                my_document = {'url': url, 'email': email, 'title': title, 'filename': filename}
                try:
                    collection.insert_one(my_document)
                finally:
                    return send_file(wav_path + "/" + filename + ".wav")
            except:
                return "Invalid request", 500
        else:
            return send_file(wav_path + "/" + result['filename'] + ".wav")
    else:
        return "Invalid request", 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)