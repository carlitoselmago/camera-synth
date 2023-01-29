

"""
OSC/Random Example: send random numbers to OSC.
This example sends a pseudo-random number between 0 and 1024
to the OSC receiver on UDP port 2222.

"""

from pythonosc import udp_client
from pythonosc import osc_message_builder
import time
import random


def main():
  #oscSender = udp_client.UDPClient("192.168.1.133", 8000)
  oscSender = udp_client.SimpleUDPClient("192.168.1.133", 8000)
  while True:
    n = random.randint(0, 100)
    print(n)

    #msg = osc_message_builder.OscMessageBuilder(address = "/rand")
    #msg.add_arg(n)
    #oscSender.send(msg.build())
    oscSender.send_message('/1/fader1',n)
	
    time.sleep(1)  

if __name__ == "__main__":
  main()
"""
"""
import mido

outport = mido.open_output('TouchOSC Bridge:TouchOSC Bridge MIDI 1 20:0')

msg = mido.Message('note_on', note=60, velocity=64)
outport.send(msg)

