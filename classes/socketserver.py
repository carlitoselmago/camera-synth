from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR
import sys
import time
import threading

class socketServer():


	PORT_NUMBER = 5000
	SIZE = 1024

	client=""
	client_port=""

	def __init__(self):
		hostName = gethostbyname( '0.0.0.0' )
		print(hostName)
		self.mySocket = socket( AF_INET, SOCK_DGRAM )
		#
		self.mySocket.bind( (hostName, self.PORT_NUMBER) )
		self.mySocket.settimeout(15)
		print ("socket server listening on port {0}\n".format(self.PORT_NUMBER))

	def startSession(self):
		x = threading.Thread(target=self.runSession)
		x.start()
			
	def runSession(self):
		pause=3
		while True:
			try:
				self.listenForClient()
				#self.SS.startStream()
				self.startStream()
				
				print("something went wrong, waiting",pause,"seconds")
				time.sleep(pause)
			except:
				print("something went wrong, waiting",pause,"seconds")
				time.sleep(pause)

	def listenForClient(self):

	
		try:
			(data,addr) = self.mySocket.recvfrom(self.SIZE)
			data=data.decode()
			if data=="findip":
				#if client=="":
				print("CLIENT FOUND!",addr)
				self.mySocket.sendto(b'SERVER_HERE',addr)
				#self.mySocket.accept()
				self.client=addr[0]
				self.client_port=addr[1]
			
			print (data,addr)
			#time.sleep(0.0001)
		except:
			print("client never appeared")
			
	def sendMessage(self,name="",value=0):
		if "conn" in dir(self):
			try:
				self.conn.sendall(str.encode(name))
			except:
				del self.conn
				print("could not communicate with client, restart session")
				#self.startSession()

	def startStream(self):
		print("startStream")
		with socket(AF_INET, SOCK_STREAM) as s:
		
			s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			s.bind(( '0.0.0.0', self.PORT_NUMBER))
			s.settimeout(2)
			s.listen()
			self.conn, addr = s.accept()
			with self.conn:
				print(f"Connected by {addr}")
				while True:
					try:
						data = self.conn.recv(1024)
					except:
						print("could not communicate with client, restart session")
						s.close()
						#self.runSession()
						break

					finally:
						try:
							client=self.conn.getpeername()

						except:
							print("connection dead")
							print("could not communicate with client, restart session")
							s.close()
							#self.runSession()
							break

					if not data:
						print("no data")
						pass
						break
