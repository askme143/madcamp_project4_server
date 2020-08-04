import librosa
import librosa.display
import numpy as np
import wave
from pydub import AudioSegment
import pydub
import sounddevice as sd
import statistics

import pyrubberband as pyrb
import soundfile as sf

def speed_change(sound, playback_speed= 0.5):
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * playback_speed)
      })
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

def change_audioseg_tempo(audiosegment, tempo_ratio):
    y = np.array(audiosegment.get_array_of_samples())
    if audiosegment.channels == 2:
        y = y.reshape((-1, 2))

    sample_rate = audiosegment.frame_rate

    print(tempo_ratio)
    y_fast = pyrb.time_stretch(y, sample_rate, tempo_ratio)

    channels = 2 if (y_fast.ndim == 2 and y_fast.shape[1] == 2) else 1
    y = np.int16(y_fast * 2 ** 15)

    new_seg = pydub.AudioSegment(y.tobytes(), frame_rate=sample_rate, sample_width=2, channels=channels)

    return new_seg


file_name = '쇼미더머니4Episode5송민호MINO겁FearFeatTaeyangofBIGBANG'
wav_path = './static/temp/youtube_wav'
# change_file_path = 'audio_change/' + file_name + '_changed.wav'

#check bpm of song
x, sr = librosa.load(wav_path + '/' + file_name + '.wav')
bpm, beat_times = librosa.beat.beat_track(x, sr=sr, start_bpm=120, units='time')
print(bpm)
#print(beat_times)

# #Correct bpm with the term list
# term = []

# for i in range(len(beat_times) - 1):
#     term.append(beat_times[i+1] - beat_times[i])

# average = sum(term, 0.0)/len(term)
# mid = statistics.median(term)

# print(60/average)
# print(60/mid)

# #print(term)
# #print(average)

# term_fixed_a = []

# for t in term:
#     is_ok_a = t / average
#     if is_ok_a > 0.9 and is_ok_a < 1.1:
#         term_fixed_a.append(t)

# average_fixed_a = sum(term_fixed_a, 0.0)/len(term_fixed_a)
# bpm_fixed_a = round(60/average_fixed_a)



# term_fixed_m = []

# for t in term:
#     is_ok_m = t / mid
#     if is_ok_m > 0.9 and is_ok_m < 1.1:
#         term_fixed_m.append(t)

# average_fixed_m = sum(term_fixed_m, 0.0)/len(term_fixed_m)
# #average_fixed_m = statistics.median(term_fixed_m)
# bpm_fixed_m = round(60/average_fixed_m)

# print(file_name)
# print("fixed bpm(average): " + str(bpm_fixed_a))
# print("fixed bpm(median) : " + str(bpm_fixed_m))


# '''
# if bpm_fixed_a != bpm_fixed_m:
#     print("hard to check bpm")
#     exit()
# '''

# #to_bpm_120 = 120 / bpm
# #to_bpm_60 = 60 / bpm

# to_what_bpm = 95
# to_change = to_what_bpm / bpm_fixed_a


# #change speed of the song

# sound = AudioSegment.from_wav(file_path)

# song_change = change_audioseg_tempo(sound, to_change)
# song_change.export("audio_change/" + file_name + "_" + str(to_what_bpm) + ".wav", format = "wav")




# beat_times_pcd = [beat / to_change for beat in beat_times]
# term_pcd = [t / to_change for t in term]
# one_term_length = 60 / to_what_bpm

# term_error = []
# for t in term_pcd:
#     term_error.append(abs(t - one_term_length))

# most_exact_beat = term_error.index(min(term_error))
# #print(most_exact_beat)
# #print(term_error)

# start_beat = beat_times[most_exact_beat]

# while(1):
#     if start_beat - one_term_length < 0:
#         break
#     start_beat -= one_term_length

# sync_time_1 = []

# beat_time_sync = start_beat

# while(1):
#     if beat_time_sync > beat_times[-1]:
#         break
#     sync_time_1.append(beat_time_sync)
#     beat_time_sync += one_term_length * 4

# print(sync_time_1)