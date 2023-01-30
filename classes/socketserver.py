from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM,SOCK_STREAM
import sys
import time

class socketServer():
	
	
	PORT_NUMBER = 5000
	SIZE = 1024
	
	client=""
	client_port=""
	
	def __init__(self):
		hostName = gethostbyname( '0.0.0.0' )
		print(hostName)
		self.mySocket = socket( AF_INET, SOCK_DGRAM )
		self.mySocket.bind( (hostName, self.PORT_NUMBER) )

		print ("socket server listening on port {0}\n".format(self.PORT_NUMBER))

	def listenForClient(self):


		while True:
				(data,addr) = self.mySocket.recvfrom(self.SIZE)
				data=data.decode()
				if data=="findip":
					#if client=="":
					print("CLIENT FOUND!")
					self.mySocket.sendto(b'SERVER_HERE',addr)
					#self.mySocket.accept()
					self.client=addr[0]
					self.client_port=addr[1]
					break
				print (data,addr)
				#if data=="start":
				"""
				if len(self.client)>0:
					print("vamooo",self.client)
					self.mySocket.sendto(b'vamooooo!',(self.client,self.client_port))
					#self.mySocket.sendall(b'vamooooo!')
					#time.sleep(1)
				"""
	def sendMessage(self,name="",value=0):
		if "conn" in dir(self):
			self.conn.sendall(str.encode(name))
	
	def startStream(self):
	    print("startStream")
	    with socket(AF_INET, SOCK_STREAM) as s:
		    s.bind(( '0.0.0.0', self.PORT_NUMBER))
		    s.listen()
		    self.conn, addr = s.accept()
		    with self.conn:
			    print(f"Connected by {addr}")
			    while True:
				    data = self.conn.recv(1024)
				    if not data:
					    pass
					    break
				    #self.conn.sendall(b'holaaa')
					

#SS=socketServer()
#SS.listenForClient()
#SS.startStream()
"""
from builtins import bytes

from optparse import OptionParser
import logging
import select
import socket
import sys

import pymidi.server
from pymidi.protocol import DataProtocol
from pymidi.protocol import ControlProtocol
from pymidi import utils

try:
    import coloredlogs
except ImportError:
    coloredlogs = None


#rtmidi part
import time
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

# here we're printing the ports to check that we see the one that loopMidi created. 
# In the list we should see a port called "loopMIDI port".
print(available_ports)

# Attempt to open the port
if available_ports:
    midiout.open_port(7)
else:
    midiout.open_virtual_port("My virtual output")

logger = logging.getLogger('pymidi.examples.server')

DEFAULT_BIND_ADDR = '0.0.0.0:5051'

parser = OptionParser()
parser.add_option(
    '-b',
    '--bind_addr',
    dest='bind_addrs',
    action='append',
    default=None,
    help='<ip>:<port> for listening; may give multiple times; default {}'.format(DEFAULT_BIND_ADDR),
)
parser.add_option(
    '-v', '--verbose', action='store_true', dest='verbose', default=False, help='show verbose logs'
)


def main():
    options, args = parser.parse_args()

    log_level = logging.DEBUG if options.verbose else logging.INFO
    if coloredlogs:
        coloredlogs.install(level=log_level)
    else:
        logging.basicConfig(level=log_level)

    class ExampleHandler(pymidi.server.Handler):
        

        def __init__(self):
            self.logger = logging.getLogger('ExampleHandler')

        def on_peer_connected(self, peer):
            self.logger.info('Peer connected: {}'.format(peer))

        def on_peer_disconnected(self, peer):
            self.logger.info('Peer disconnected: {}'.format(peer))

        def on_midi_commands(self, peer, command_list):
            for command in command_list:
                if command.command == 'note_on':
                    print(command.params)
                    key = command.params.key
                    velocity = command.params.velocity
                    note_on=[0x90, key,velocity]
                    midiout.send_message(note_on)
                    print('Someone hit the key {} with velocity {}'.format(key, velocity))

    bind_addrs = options.bind_addrs
    if not bind_addrs:
        bind_addrs = [DEFAULT_BIND_ADDR]

    server = pymidi.server.Server.from_bind_addrs(bind_addrs)
    server.add_handler(ExampleHandler())

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Got CTRL-C, quitting')
        sys.exit(0)


main()
"""
