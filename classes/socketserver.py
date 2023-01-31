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
		self.mySocket.bind( (hostName, self.PORT_NUMBER) )

		print ("socket server listening on port {0}\n".format(self.PORT_NUMBER))

	def startSession(self):
		self.listenForClient()
		#self.SS.startStream()
		x = threading.Thread(target=self.startStream)
		x.start()

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
			try:
				self.conn.sendall(str.encode(name))
			except:
				del self.conn
				print("could not communicate with client, restart session")
				self.startSession()

	def startStream(self):
		print("startStream")
		with socket(AF_INET, SOCK_STREAM) as s:
			s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
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
