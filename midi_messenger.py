
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

	serverIP="192.168.1.28"#"192.168.1.133"


	### midi translator vars

	speed=0.07 #speed of while loop translation


	people=0
	maxpeople=4
	last_people=0

	minCC=5

	midiM=[
	#{"name":"people","type":0xb0,"extra":0x74,"value":0,"nextvalue":0}, #CC=0xb0
	{"name":"people","type":"PROGRAM_CHANGE","extra":30,"value":0,"nextvalue":0,"channel":1}, #CC=0xb0

	{"name":"topL","type":"PROGRAM_CHANGE","extra":31,"value":0,"nextvalue":0,"channel":2} ,
	{"name":"topR","type":"PROGRAM_CHANGE","extra":32,"value":0,"nextvalue":0,"channel":2} ,
	{"name":"BottomL","type":"PROGRAM_CHANGE","extra":33,"value":0,"nextvalue":0,"channel":3} ,
	{"name":"BottomR","type":"PROGRAM_CHANGE","extra":34,"value":0,"nextvalue":0,"channel":3} ,

	{"name":"peoplechange","type":"NOTE_ON","extra":34,"value":0,"nextvalue":0,"channel":4} ,	
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

	def is_server_up(self,ip, port,timeout=15):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.settimeout(timeout)
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

		peoplechangemargin=4
		if abs(self.people-self.last_people)>peoplechangemargin:
			#trigger note on
			self.midiM[5]["nextvalue"]=1


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

		self.last_people=len(centers)

	def handleFluidMidi(self):
		midiout = MidiOutWrapper(self.midiout)
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
					PROGRAM_CHANGE=0xb0
					midiout.channel_message(PROGRAM_CHANGE,m["extra"],int(value),ch=m["channel"])
				if m["type"]=="NOTE_ON":
					midiout.note_on(m["extra"], velocity=127,ch= m["channel"])
					
				#message=[m["type"],m["extra"],int(value)]
				#self.midiout.send_message(message)
				

					
				self.midiM[i]["value"]=value

			time.sleep(self.speed)

	def midiMessenger(self,ip,port):
		print("connection stablished with ",ip)
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
			s.connect((ip, port))
			s.settimeout(5)
			s.sendto(b'start', (ip, port))
			print("DATA WILL BE RECIEVED")
			while True:
				try:
					data = s.recv(1024)
					#print(data)
					data=data.decode()
				except:
					print("LOST CONNECTION WITH SERVER, server down?")
					break
					continue
				try:
					datalist=json.loads(data)
					#print("datalist")
					#print(datalist)
					if len(datalist)>0:
						self.translateData2Midi(datalist)
				except:
					print("Problem understanding data")
					#print(data)
					print("")
				try:
					s.sendto(b'ok', (ip, port))
				except:
					print("refused reconect")
					#refused reconect
					pass

		print("connection end?")


	def start_connection(self,local_ip="0.0.0.0"):

		server_check=self.is_server_up(self.serverIP, self.port,0.8)
		
		""" TODO: fix this for the future, it should be fast over poor wifi
		print("get server ip")
		#octets = local_ip.split('.')[0]
		ipp=local_ip.split(".")
		ipbase=ipp[0]+"."+ipp[1]+"."+ipp[2]+"."

		for i in range(1,300):
			target=ipbase+str(i)

			server_check=self.is_server_up(target, self.port,0.8)
			print("server check:",server_check)
			if server_check:
				self.serverIP=server_check[0]
				print("IP FOUND!")
				break
			else:
				print(target,"not the right ip")
		"""
		if server_check:
			t = Thread(target=self.handleFluidMidi)
			t.start()
			self.midiMessenger(self.serverIP,self.port)
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
	print("")
	pause=3
	
	local_ip = MM.get_local_ip()
	print("Local IP: ",local_ip)

	while True:
		try:
			local_ip = MM.get_local_ip()
			MM.start_connection(local_ip)
			print("Server is not ready waiting",pause,"seconds and retry")
			time.sleep(pause)
		except:
			
			print("something went wrong, wait",pause,"seconds and retry")
			time.sleep(pause)

	

