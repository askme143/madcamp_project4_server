import youtube
from pymongo import MongoClient
from flask import Flask, render_template, request, url_for, send_from_directory

app = Flask(__name__)
client = MongoClient('localhost', 27017)

db = client.prj4

# Sample
@app.route('/')
def sample_home():
    return render_template('sample.html')

@app.route('/input')
def sample_input():
    return render_template('sample_input.html')

# Test
@app.route('/test/youtube', methods=['POST'])
def test_youtube():
    print("> Test youtube")
    url = request.form['youtube_url']
    youtube.get_audio(url)
    return "hello world"

@app.route('/test')
def test_():
    return "hello world"

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)