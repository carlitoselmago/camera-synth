
import socket
from threading import Thread
import time
import logging
import json
import rtmidi


class midiMessenger():

	port=5000
	SIZE=1024

	serverIP=""


	### midi translator vars

	speed=0.01 #speed of while loop translation

	people=0
	maxpeople=8

	minCC=5

	midiM=[
	{"name":"people","type":0xb0,"extra":0x74,"value":0,"nextvalue":0} #CC=0xb0
		]


	def __init__(self):
		self.midiout = rtmidi.MidiOut()
		available_ports = self.midiout.get_ports()

		# here we're printing the ports to check that we see the one that loopMidi created. 
		# In the list we should see a port called "loopMIDI port".
		print(available_ports)

		# Attempt to open the port
		if available_ports:
			for i,p in enumerate(available_ports):
				if "loopMIDI" in p:
					self.midiout.open_port(i)
		else:
		    self.midiout.open_virtual_port("My virtual output")

		logger = logging.getLogger('pymidi.examples.server')


	def get_local_ip(self):
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	    try:
	        s.connect(('10.255.255.255', 1))
	        IP = s.getsockname()[0]
	    except:
	        IP = '127.0.0.1'
	    finally:
	        s.close()
	    return IP

	def is_server_up(self,ip, port):
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	    s.settimeout(0.001)
	    s.sendto(b'findip', (ip, port))
	    try:
	        
	        data, addr = s.recvfrom(1024)
	        #print(data,addr)
	        if data == b'SERVER_HERE':
	            return addr
	        else:
	            return False
	    except socket.error:
	        return False
	    finally:
	        s.close()


	def translateData2Midi(self,data):

		self.people=len(data)

		peopleV=(float(self.people)/self.maxpeople)*(127)

		#control = [0xb0, 0x74, peopleV]

		#self.midiout.send_message(control)
		self.midiM[0]["nextvalue"]=peopleV

	def handleFluidMidi(self):

		while True:

			for i,m in enumerate(self.midiM):
				nextvalue=int(m["nextvalue"])
				value=int(m["value"])
				if m["nextvalue"]>value:
					value+=1
				elif m["nextvalue"]<value:
					value-=1
				print("value",int(value),"nextvalue",m["nextvalue"])
				message=[m["type"],m["extra"],int(value)]
				self.midiout.send_message(message)
				self.midiM[i]["value"]=value

			time.sleep(self.speed)

	def midiMessenger(self,ip,port):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((ip, port))
			s.sendto(b'start', (ip, port))
			while True:
				data = s.recv(1024)
				data=data.decode()
				datalist=json.loads(data)
				print("datalist")
				print(datalist)
				if len(datalist)>0:
					self.translateData2Midi(datalist)
				#self.handleFluidMidi()
				"""
				if data=="morepeople":
					note_on=[0x90, 60,127]
					midiout.send_message(note_on)
				if data=="lesspeople":
					note_on=[0x90, 40,127]
					midiout.send_message(note_on)
				"""
				#print(f"Received {data!r}")
				s.sendto(b'ok', (ip, port))
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		hostName = socket.gethostbyname( '0.0.0.0' )
		s.sendto(b'findip', (ip, port))
		#s.bind( (hostName,port) )
		s.settimeout(2)
		#s.connect((ip,port))
		#s.sendto(b'start', (ip, port))
		while True:

			data, addr = s.recvfrom(1024)
			print(data)
		"""

	def get_server_ip(self,local_ip="0.0.0.0"):
		print("get server ip")
		#octets = local_ip.split('.')[0]
		ipp=local_ip.split(".")
		ipbase=ipp[0]+"."+ipp[1]+"."+ipp[2]+"."
		
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		for i in range(1,300):
			target=ipbase+str(i)
			
			try:
				server_check=self.is_server_up(target, self.port)
			except:
				print("failed on",target)
				server_check=False
			if server_check:
				serverIP=server_check[0]
				print("FOUND ip",serverIP)

				#init messenger
				time.sleep(0.5)

				t = Thread(target=self.handleFluidMidi)
				t.start()

				self.midiMessenger(serverIP,self.port)
				break

		print("")
		print("no connection found")



if __name__ == '__main__':
	MM=midiMessenger()
	local_ip = MM.get_local_ip()
	server_ip=MM.get_server_ip(local_ip)
	print("")
	print("Local IP: ",local_ip)

