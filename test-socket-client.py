"""
import sys
from socket import socket, AF_INET, SOCK_DGRAM,gethostbyname,gethostname
import time



SERVER_IP   = '192.168.1.133'
PORT_NUMBER = 5000
SIZE = 1024
print ("Test client sending packets to IP {0}, via port {1}\n".format(SERVER_IP, PORT_NUMBER))

mySocket = socket( AF_INET, SOCK_DGRAM )

while True:
        mySocket.sendto('cool',(SERVER_IP,PORT_NUMBER))
        time.sleep(1)
sys.exit()
"""
import socket
from threading import Thread

port=5000
SIZE=1024

serverIP=""

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
    
def captureServerIP(s):
	#print("capture server ip init")
	(data,addr) = s.recvfrom(SIZE)
	serverIP=addr[0]
	print("serverIP set!!!!",serverIP)
	#print(data,addr)

def get_server_ip(local_ip="0.0.0.0"):
	#octets = local_ip.split('.')[0]
	ipp=local_ip.split(".")
	ipbase=ipp[0]+"."+ipp[1]+"."+ipp[2]+"."
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	t = Thread(target=captureServerIP, args=[s,])
	t.start()
	for i in range(1,300):
		target=ipbase+str(i)
		
		try:
			#con=s.sendto(b'findip',(target,port))
			#con=s.connect((target, port))
			con=s.sendto(b'findip',(target,port))
			
			#print(target,con)
		except:
			pass
		


if __name__ == '__main__':
    local_ip = get_local_ip()
    server_ip=get_server_ip(local_ip)
    print("Local IP: ",local_ip)
    
