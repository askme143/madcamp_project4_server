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

@app.route('/api/sign_up')
def sign_up():
    user_id = request.args.get('user_id')
    password = request.args.get('password')

    if(user_id == '' or password == ''):
        return "fill ID and password"

    collection = db.login_info

    is_already = collection.find({"user_id":user_id})

    if is_already.count():
        return "duplicate ID"

    my_document = {'user_id': user_id, 'password': password}
    print(my_document)

    try:
        collection.insert_one(my_document)
    except:
        return "Failed"

    return "sign up success"

@app.route('/api/login')
def login():
    user_id = request.args.get('user_id')
    password = request.args.get('password')

    collection = db.login_info

    is_user = collection.find_one({'user_id':user_id, 'password': password})

    if not is_user:
        return "login failed"

    response = dict()

    user_info = [user_id, password]

    preset_info = []

    preset_list = db.preset.find({'user_id':user_id})

    for preset in preset_list:
        preset_info.append([preset['preset_num'], preset['preset_info']])

    response['user_info'] = user_info
    response['preset_info'] = preset_info

    return jsonify(response)

@app.route('/api/preset/add', methods=['POST'])
def add_preset():
    user_id = request.form['user_id']
    password = request.form['password']
    preset_num = request.form['preset_num']
    preset_info = request.form['preset_info']
    
    collection_login = db.login_info

    is_user = collection_login.find_one({'user_id':user_id, 'password': password})

    if not is_user:
        return "User info incorrect"

    collection = db.preset

    is_already = collection.find({'user_id':user_id, 'preset_num':preset_num})

    if is_already.count():
        return 'There is already preset'
    
    else:
        my_document = {'user_id': user_id, 'preset_num': preset_num, 'preset_info':preset_info}
        print(my_document)
        collection.insert(my_document)

    return 'upload success'

@app.route('/api/preset/edit', methods=['POST'])
def edit_preset():
    user_id = request.form['user_id']
    password = request.form['password']
    preset_num = request.form['preset_num']
    preset_info = request.form['preset_info']
    
    collection_login = db.login_info

    is_user = collection_login.find_one({'user_id':user_id, 'password': password})

    if not is_user:
        return "User info incorrect"

    collection = db.preset

    is_already = collection.find({'user_id':user_id, 'preset_num':preset_num})

    if not is_already.count():
        return 'There is not preset'
    
    else:
        my_document = {'user_id': user_id, 'preset_num': preset_num}
        print(my_document)
        collection.find_one_and_update(my_document, {'$set': {'preset_info': preset_info}})

    return 'edit success'

@app.route('/api/preset/delete', methods=['POST'])
def del_preset():
    user_id = request.form['user_id']
    password = request.form['password']
    preset_num = request.form['preset_num']
    
    collection_login = db.login_info

    is_user = collection_login.find_one({'user_id':user_id, 'password': password})

    if not is_user:
        return "User info incorrect"

    collection = db.preset

    is_already = collection.find({'user_id':user_id, 'preset_num':preset_num})

    if not is_already.count():
        return 'There is not preset info'
    
    else:
        my_document = {'user_id': user_id, 'preset_num': preset_num}
        print(my_document)
        collection.delete_one(my_document)

    return 'delete success'

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
        my_query['title'] = titles
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