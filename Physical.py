import pyaudio
import audioop
from threading import Thread
import time
from datetime import datetime
import Util as Util
from Constants import *
import sys
import multiprocessing
from DataLink import *
 
class Physical(object): # OSI Model Physical Layer: Responsible for transmitting raw bit stream over the physical medium
    
    def __init__(self):
        # Global variables to be manipulated in the loop for messages
        Util.log(self,"Physical layer has started", WARNING)
        self.buffer = []
        self.is_transmitting = False
        self.datalink_layer = DataLink() # To be directed to the next layer
    
    def manager(self, seconds):
        #print("Timer has started")
        time.sleep(seconds)
        #print("Timer has ended")
        copy_of_buffer = self.buffer.copy()
        #print("COPY OF BUFFER: ", copy_of_buffer)
        #print("copy lenght",len(copy_of_buffer))
        self.is_transmitting = False
        message = []

        # Task 1: Group by seconds
        i = 0
        while i in range(len(copy_of_buffer)):
            #print(i)
            #print("len", len(copy_of_buffer))
            if i == len(copy_of_buffer): 
                break

            if i is not 0:
                (data, miliseconds) = copy_of_buffer[i] 
                # print("copy_of_buffer[i]: ", copy_of_buffer[i])
                # print("DATA: ", data)
                
                diff = miliseconds - (copy_of_buffer[i-1][TIME_ATT])
                #print(diff)
                if diff < 1000:
                    del copy_of_buffer[i] 
                    i = i - 1  
            i += 1
            #print("copy", copy_of_buffer)

        # Task 2: Include zeros in the message -> [10]
        
        for i in range(len(copy_of_buffer)):
            # At the second
            if i is not 0:
                (data, miliseconds) = copy_of_buffer[i]
                diff = miliseconds - (copy_of_buffer[i-1][TIME_ATT])
                print('diff', diff)
                # Adding zeroes between the noises
                
                message.extend([SILENCE]*(int)((diff / 1000) - 1))
                # Adding the noise
                message.append(copy_of_buffer[i][0])
                #print('message: ', message)
            #append of the first 1 for control
            else:
                message.append(copy_of_buffer[i][0])

        Util.log(self, 'Sending [{}] to DataLink layer'.format(''.join(message)), INFO)
        self.datalink_layer.handle_message(message)
        

    def receive(self):
        p = pyaudio.PyAudio()
        
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        # Loop for messages
        while True:
            #print("Listening...")
            #initial validations
            data = stream.read(CHUNK, exception_on_overflow = False)
            
            if data:
                
                volume_of_data = Util.getVol(data) # Get volume of data that was detected
                
                # Heard a 1
                if volume_of_data > THRESHOLD: # It can be identified that a 1 has been read
                    print("read a 1")
                    # Inserting in the message's buffer
                    if self.is_transmitting:
                        #print("reading...")
                        self.buffer.append((NOISE,Util.timestamp())) # Append NOISE, which is 1, and a timestamp
                        # Initializes a new buffer and starts the thread
                    else:
                        self.buffer = []
                        # Inserting the first bit, for initial control
                        self.buffer.append((NOISE,Util.timestamp()))
                        self.is_transmitting = True
                        Thread(target = self.manager, args = (SECONDS, )).start()

    def send(self, ip, message):
        messages = Util.split(message,8) # 1 byte = 8 bits
        
        for msg in messages:
            string = '{control}{ip}{data}{control}'.format(control=NOISE,ip=ip,data=msg) # Encapsulation of packets with control bits on each end
            Util.log(self, 'Sending [{}] to the environment'.format(''.join(string)), INFO)
            aux = []
            for bit in string:
                if bit == NOISE: # If it's a 1
                    aux.append(NOISE)
                    sys.stdout.write('\r{}'.format(''.join(aux)))
                    sys.stdout.flush()
                    Util.playBeep()        
                else:
                    aux.append(SILENCE)
                    sys.stdout.write('\r{}'.format(''.join(aux)))
                    sys.stdout.flush()
                    time.sleep(SLEEP_TIME)
            print('\n')


