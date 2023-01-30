
import socket
from threading import Thread
import time

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

def is_server_up(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0.001)
    try:
        s.sendto(b'findip', (ip, port))
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

def midiMessenger(ip,port):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((ip, port))
		s.sendto(b'start', (ip, port))
		while True:
			data = s.recv(1024)
			print(f"Received {data!r}")
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

def get_server_ip(local_ip="0.0.0.0"):
	#octets = local_ip.split('.')[0]
	ipp=local_ip.split(".")
	ipbase=ipp[0]+"."+ipp[1]+"."+ipp[2]+"."
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	for i in range(1,300):
		target=ipbase+str(i)
		server_check=is_server_up(target, port)
		if server_check:
			serverIP=server_check[0]
			print("FOUND ip",serverIP)

			#init messenger
			time.sleep(0.5)
			midiMessenger(serverIP,port)
			break



if __name__ == '__main__':
    local_ip = get_local_ip()
    server_ip=get_server_ip(local_ip)
    print("")
    print("Local IP: ",local_ip)
    
