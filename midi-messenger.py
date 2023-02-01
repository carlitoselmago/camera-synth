
import socket
from threading import Thread
import time
import logging
import json
import rtmidi
from classes.midiwrapper import MidiOutWrapper

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
	#{"name":"people","type":0xb0,"extra":0x74,"value":0,"nextvalue":0}, #CC=0xb0
	{"name":"people","type":"PROGRAM_CHANGE","extra":30,"value":0,"nextvalue":0,"channel":1}, #CC=0xb0

	{"name":"topL","type":"PROGRAM_CHANGE","extra":31,"value":0,"nextvalue":0,"channel":2} ,
	{"name":"topR","type":"PROGRAM_CHANGE","extra":32,"value":0,"nextvalue":0,"channel":2} ,
	{"name":"BottomL","type":"PROGRAM_CHANGE","extra":33,"value":0,"nextvalue":0,"channel":3} ,
	{"name":"BottomR","type":"PROGRAM_CHANGE","extra":34,"value":0,"nextvalue":0,"channel":3} 
		]


	def __init__(self):
		self.midiout = rtmidi.MidiOut()
		self.midiout = MidiOuWrapper(self.midiout)
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
		#s.settimeout(0.05)
		s.sendto(b'findip', (ip, port))
		
		try:
			
			data, addr = s.recvfrom(1024)
			#print(data,addr)
			if data == b'SERVER_HERE':
				print("found signal from server")
				return addr
			else:
				return False
		except socket.error:
			return False
		finally:
			s.close()
		print("is_server_up end")

	def scaleMidi(self,value,maxvalue):
		return (float(value)/maxvalue)*(127)

	def translateData2Midi(self,data):

		centers=data["centers"]
		width=data["width"]
		height=data["height"]

		self.people=len(centers)

		peopleV=(float(self.people)/self.maxpeople)*(127)

		topL=0 
		topR=0 
		BottomL=0
		BottomR=0

		#convert centers to percentages
		centersPercent=[]
		for c in centers:
			xPercent=(c[0]*100)/width
			yPercent=(c[1]*100)/height
			centersPercent.append((xPercent,yPercent))

			if xPercent<50 and yPercent<50:
				topL+=1
			if xPercent>50 and yPercent<50:
				topR+=1
			if xPercent<50 and yPercent>50:
				BottomL+=1
			if xPercent>50 and yPercent>50:
				BottomR+=1



		#control = [0xb0, 0x74, peopleV]

		#self.midiout.send_message(control)
		self.midiM[0]["nextvalue"]=peopleV

		maxCorners=6
		self.midiM[1]["nextvalue"]=self.scaleMidi(topL,maxCorners)
		self.midiM[2]["nextvalue"]=self.scaleMidi(topR,maxCorners)
		self.midiM[3]["nextvalue"]=self.scaleMidi(BottomL,maxCorners)
		self.midiM[4]["nextvalue"]=self.scaleMidi(BottomR,maxCorners)

	def handleFluidMidi(self):

		while True:

			for i,m in enumerate(self.midiM):
				nextvalue=int(m["nextvalue"])
				value=int(m["value"])
				if m["nextvalue"]>value:
					value+=1
				elif m["nextvalue"]<value:
					value-=1
				#print("value",int(value),"nextvalue",m["nextvalue"])
				if m["type"]=="PROGRAM_CHANGE":
					self.midiout.channel_message(PROGRAM_CHANGE,m["extra"],int(value),ch=m["channel"])
				#message=[m["type"],m["extra"],int(value)]
				#self.midiout.send_message(message)
				self.midiM[i]["value"]=value

			time.sleep(self.speed)

	def midiMessenger(self,ip,port):
		print("connection stablished with ",ip)
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
			s.connect((ip, port))
			#s.timeout(0.1)
			s.sendto(b'start', (ip, port))
			print("DATA WILL BE RECIEVED")
			while True:
				data = s.recv(1024)
				data=data.decode()
				datalist=json.loads(data)
				#print("datalist")
				#print(datalist)
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
		print("connection end?")

	def get_server_ip(self,local_ip="0.0.0.0"):
		server_check=self.is_server_up("192.168.1.28", self.port)
		print(server_check)
		t = Thread(target=self.handleFluidMidi)
		t.start()

		self.midiMessenger("192.168.1.28",self.port)
		"""
		print("get server ip")
		#octets = local_ip.split('.')[0]
		ipp=local_ip.split(".")
		ipbase=ipp[0]+"."+ipp[1]+"."+ipp[2]+"."
		
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#s.timeout(0.01)

		for i in range(1,300):
			target=ipbase+str(i)
			
			try:

				server_check=self.is_server_up(target, self.port)
				#print("target",target)
			except:
				#print("failed on",target)
				server_check=False
			finally:
				pass
				#print("finally")
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
		"""


if __name__ == '__main__':
	MM=midiMessenger()
	local_ip = MM.get_local_ip()
	#MM.midiMessenger("192.168.1.28",MM.port)
	server_ip=MM.get_server_ip(local_ip)
	print("")
	print("Local IP: ",local_ip)

