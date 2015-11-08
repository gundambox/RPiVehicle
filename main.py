#coding=utf-8
import copy
import pyaudio
import wave
import threading
import RPi.GPIO as GPIO
from subprocess import Popen
from time import sleep 
from sphinxbase import *
from pocketsphinx import *
from array import array
from struct import pack
from sys import byteorder
from array import array
from Queue import Queue, Full

THRESHOLD = 5000  # audio levels not normalised.
CHUNK_SIZE = 1024
BUF_MAX_SIZE = CHUNK_SIZE * 10
SILENT_CHUNKS = 1 * 16000 / 1024  # about 1sec
FORMAT = pyaudio.paInt16
FRAME_MAX_VALUE = 2 ** 15 - 1
NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
RATE = 16000
CHANNELS = 1
TRIM_APPEND = RATE / 4

GPIO.setmode(GPIO.BOARD)

Motor1A = 16
Motor1B = 18
#Motor1E = 22
 
Motor2A = 23
Motor2B = 21
#Motor2E = 19

def initGPIO():
    GPIO.setup(Motor1A,GPIO.OUT)
    GPIO.setup(Motor1B,GPIO.OUT)
    #GPIO.setup(Motor1E,GPIO.OUT)
 
    GPIO.setup(Motor2A,GPIO.OUT)
    GPIO.setup(Motor2B,GPIO.OUT)
    #GPIO.setup(Motor2E,GPIO.OUT)

def initConfig():

    config = Decoder.default_config()
    config.set_string('-hmm', "tdt_sc_8kadapt")
    config.set_string('-lm', "cmd.lm")
    config.set_string('-dict', "cmd.dic")
    config.set_string('-logfn', "/tmp/log.txt")

    return config

def is_silent(data_chunk):
    """Returns 'True' if below the 'silent' threshold"""
    return max(data_chunk) < THRESHOLD
    
def normalize(data_all):
    """Amplify the volume out to max -1dB"""
    # MAXIMUM = 16384
    normalize_factor = (float(NORMALIZE_MINUS_ONE_dB * FRAME_MAX_VALUE)
                        / max(abs(i) for i in data_all))

    r = array('h')
    for i in data_all:
        r.append(int(i * normalize_factor))
    return r

def trim(data_all):
    _from = 0
    _to = len(data_all) - 1
    for i, b in enumerate(data_all):
        if abs(b) > THRESHOLD:
            _from = max(0, i - TRIM_APPEND)
            break

    for i, b in enumerate(reversed(data_all)):
        if abs(b) > THRESHOLD:
            _to = min(len(data_all) - 1, len(data_all) - 1 - i + TRIM_APPEND)
            break
            
    return copy.deepcopy(data_all[_from:(_to + 1)])

def recordContent(stopped):
    """Record a word or words from the microphone and 
    return the data as an array of signed shorts."""

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK_SIZE)

    silent_chunks = 0
    audio_started = False
    data_all = array('h')

    count=0

    while not stopped.wait(timeout=0):
        # little endian, signed short
        data_chunk = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            data_chunk.byteswap()
        data_all.extend(data_chunk)
        silent = is_silent(data_chunk)
	
        if audio_started:
            if silent:
                silent_chunks += 1
                if silent_chunks > SILENT_CHUNKS:
                    break
            else: 
                silent_chunks = 0
        elif not silent:
            audio_started = True       

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    data_all = trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as is_silent() function)
    data_all = normalize(data_all)
    return sample_width, pack('<' + ('h' * len(data_all)), *data_all)

def driveMotor(cmd):
    if cmd == '前進':
        print '前進'
        GPIO.output(Motor1A,GPIO.LOW)
        GPIO.output(Motor1B,GPIO.HIGH)
        #GPIO.output(Motor1E,GPIO.HIGH)
 
        GPIO.output(Motor2A,GPIO.HIGH)
        GPIO.output(Motor2B,GPIO.LOW)
        #GPIO.output(Motor2E,GPIO.HIGH)
    elif cmd == '後退':
        print '後退'
        GPIO.output(Motor1A,GPIO.HIGH)
        GPIO.output(Motor1B,GPIO.LOW)
        #GPIO.output(Motor1E,GPIO.HIGH)
 
        GPIO.output(Motor2A,GPIO.LOW)
        GPIO.output(Motor2B,GPIO.HIGH)
        #GPIO.output(Motor2E,GPIO.HIGH)
    elif cmd == '右轉':
        print '右轉'
        GPIO.output(Motor1A,GPIO.LOW)
        GPIO.output(Motor1B,GPIO.HIGH)
        #GPIO.output(Motor1E,GPIO.HIGH)
        
        GPIO.output(Motor2A,GPIO.LOW)
        GPIO.output(Motor2B,GPIO.HIGH)
        #GPIO.output(Motor2E,GPIO.HIGH)
    elif cmd == '左轉':
        print '左轉'
        GPIO.output(Motor1A,GPIO.HIGH)
        GPIO.output(Motor1B,GPIO.LOW)
        #GPIO.output(Motor1E,GPIO.HIGH)
        
        GPIO.output(Motor2A,GPIO.HIGH)
        GPIO.output(Motor2B,GPIO.LOW)
        #GPIO.output(Motor2E,GPIO.HIGH)
    elif cmd == '停止':
        print '停止'
        GPIO.output(Motor1A,GPIO.LOW)
        GPIO.output(Motor1B,GPIO.LOW)
        
        GPIO.output(Motor2A,GPIO.LOW)
        GPIO.output(Motor2B,GPIO.LOW)
        
    sleep(1)

def recognize(stopped, q, config):
    while True:
        if stopped.wait(timeout=0):
            break
        content = q.get()
        if content is not None:
            decoder = Decoder(config)
            decoder.start_utt()
            decoder.process_raw(content,False,True)
            decoder.end_utt()
            cmds = decoder.hyp().hypstr.split(' ')
            for cmd in cmds:
                driveMotor(cmd)
        else:
            print "WTF!!"


def listen(stopped, q):
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=2,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
        )

    while True:
        if stopped.wait(timeout=0):
            break
        try:
            sample_width, data = recordContent(stopped)
            q.put(data)
        except Full:
            pass  # discard
            
def main():
    stopped = threading.Event()
    q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))

    config = initConfig()
    initGPIO()
    
    listen_t = threading.Thread(target=listen, args=(stopped, q))
    listen_t.start()
    recognize_t = threading.Thread(target=recognize, args=(stopped, q, config))
    recognize_t.start()
    
    try:
        while True:
            listen_t.join(0.1)
            recognize_t.join(0.1)
    except KeyboardInterrupt:
        stopped.set()

if __name__ == '__main__':
    main()
