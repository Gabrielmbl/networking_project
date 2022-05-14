from Constants import *
from Network import * 
import Util as Util

class DataLink(object): # OSI Model Data Link Layer: Deals with properly handling the frames
    def __init__(self):
        Util.log(self,"DataLink layer has started",WARNING)
        self.network_layer = Network(MACHINE_B) # MACHINE_B = '01'
        self.motives = {
            self.validate_bits : VALIDATE_BITS,
            self.validate_control_bits : VALIDATE_CONTROL_BITS,
            self.validate_message_lenght : VALIDATE_MESSAGE_LENGHT
        }
    
    def handle_message(self, message):
        validations = [self.validate_control_bits, self.validate_message_lenght , self.validate_bits] 
        validated = True

        for validation in validations:
            if(validation(message) == False): # If a validation fails
                validated = False
                reason = self.motives[validation] 
                break

        if validated:
            message = message[1:-1] # Without control bits -> control-ip-data-control
            ip = message[0:2] # First 2 bits of msg is ip

            Util.log(self, "Message [{}] for the ip [{}] is validated".format(''.join(message[2::]),ip), SUCCESS)
            self.network_layer.route(ip, message[2::]) # Hand ip and message to network layer to route
        else:
            Util.log(self, "Message [{}] not validated due to [{}]".format(''.join(message), reason), FAIL)
            

    def validate_bits(self, message):
        return all([ a == '0' or a =='1' for a in message ]) # Only 1s and 0s in the message

    def validate_control_bits(self, message):
        return message[0] == '1' and message[-1] == '1' # Beggining and end must be 1 -> control-ip-data-control

    def validate_message_lenght(self, message): # Message size should be 12
        return len(message) == MESSAGE_SIZE



