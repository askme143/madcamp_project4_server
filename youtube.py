import re
import os
import time
from pytube import YouTube
from pydub import AudioSegment
from pydub.utils import which

mp3_path = os.getcwd() + "/static/temp/youtube_mp3"
wav_path = os.getcwd() + "/static/temp/youtube_wav"

def get_audio(url: str):
    return get_wav_from_mp3(get_mp3(url))

def get_mp3(url: str):
    global wav_path, mp3_path

    yt = YouTube(url)
    filename = yt.title
    filename = re.sub('[^0-9a-zA-Zㄱ-힗]', '', filename)

    # Check whether it's already in the directory
    filenames = os.listdir(mp3_path)
    for name in filenames:
        if filename == name.split('.')[0]:
            return filename

    yt.streams.get_audio_only().download(mp3_path, filename)
    os.rename(mp3_path + "/" + filename + ".mp4", mp3_path + "/" + filename + ".mp3")

    return filename

def get_wav_from_mp3(filename: str):
    global wav_path, mp3_path
    
    filenames = os.listdir(wav_path)
    for name in filenames:
        if filename == name.split('.')[0]:
            return filename

    AudioSegment.converter = which("ffmpeg")
    sound = AudioSegment.from_file(mp3_path + "/" + filename + ".mp3", format="mp4")
    sound.export(wav_path + "/" + filename + ".wav", format="wav")

    return filename

if __name__ == '__main__':
    get_audio('https://www.youtube.com/watch?v=MFkJ0EhumYU&list=RDghNci2gUpSk&index=8')