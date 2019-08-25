import pyaudio
import wave
import requests
import json
from dict import dict
from dict import data_list
import spacy

API_ENDPOINT = 'https://api.wit.ai/speech'
ACCESS_TOKEN = 'UHN2S72EQSOASNMGRO7MHVXJAM2WT235'
test_file = open("speech_parts.csv", "a+")
string = ""

def record_audio(RECORD_SECONDS, WAVE_OUTPUT_FILENAME):
    #--------- SETTING PARAMS FOR OUR AUDIO FILE ------------#
    FORMAT = pyaudio.paInt16    # format of wave
    CHANNELS = 1                # no. of audio channels
    RATE = 44100                # frame rate
    CHUNK = 1024                # frames per audio sample
    #--------------------------------------------------------#

    # creating PyAudio object
    audio = pyaudio.PyAudio()

    # open a new stream for microphone
    # It creates a PortAudio Stream Wrapper class object
    stream = audio.open(format=FORMAT,channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    #----------------- start of recording -------------------#
    print("Listening...")

    # list to save all audio frames
    frames = []

    for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
        # read audio stream from microphone
        data = stream.read(CHUNK)
        # append audio data to frames list
        frames.append(data)

    #------------------ end of recording --------------------#   
    print("Finished recording.")

    stream.stop_stream()    # stop the stream object
    stream.close()          # close the stream object
    audio.terminate()       # terminate PortAudio

    #------------------ saving audio ------------------------#

    # create wave file object
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')

    # settings for wave file object
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))

    # closing the wave file object
    waveFile.close()

def read_audio(WAVE_FILENAME):
    # function to read audio(wav) file
    with open(WAVE_FILENAME, 'rb') as f:
        audio = f.read()
    return audio

def RecognizeSpeech(AUDIO_FILENAME, string, num_seconds = 5):

    # record audio of specified length in specified audio file
    record_audio(num_seconds, AUDIO_FILENAME)

    # reading audio
    audio = read_audio(AUDIO_FILENAME)
    string = printSpeech(audio, string)
    return string


def printSpeech(audio, string):
    headers = {'authorization': 'Bearer ' + ACCESS_TOKEN,
           'Content-Type': 'audio/wav'}

    #Send the request as post request and the audio as data
    resp = requests.post(API_ENDPOINT, headers = headers, data = audio)

    #Get the text
    data = resp.json()
    print(data['_text'])
    string = data['_text']
    test_file.write(data['_text'])
    test_file.write("\n")
    #respond(data['_text'])
    return string
"""
def respond(text):
    words = []
    words = text.split()

    info = ''
    for data in words:
        if data in data_list:
            info = data

    for name1, name2 in zip(words[:-1], words[1:]):
        if name1 + ' ' + name2 in dict:
            print(name1 + ' ' + name2)
            if info == 'tension':
                print(dict[name1 + ' ' + name2][1])
            if info == 'age':
                print(dict[name1 + ' ' + name2][0])
"""

def my_component(doc):
	for token in doc:
		print token.text + ": " + token.pos_ 
		test_file.write(token.text + ": " + token.pos_)
		test_file.write("\n")
	return doc


if __name__ == "__main__":
    string = RecognizeSpeech('myspeech.wav', string, 6)
    nlp = spacy.load('en')
    nlp.add_pipe(my_component, name="print_info", last=True)
    doc = nlp(string)
    test_file.write("\n")
