import Util as Util
from Constants import *

class Network(object): # OSI Model Network Layer: Deals with properly routing the packets to their designed destination. 

    def __init__(self, ip):
        Util.log(self, "Network layer has started", WARNING)
        self.ip = ip

    def route(self, ip, message):
        if(''.join(ip) == self.ip): # If message was sent to MACHINE_B = '01', then it has been received
            Util.log(self,"[{}] Message {} received".format(type(self).__name__,''.join(message)), SUCCESS)
        else: # If message was sent to other machine, then message is discarded
            Util.log(self,"[{}] Message {} discarded".format(type(self).__name__,''.join(message)), FAIL)
