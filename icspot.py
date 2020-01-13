import os
import sys
import socket, thread
from array import array
from time import sleep, ctime
from scapy.utils import hexdump

from Hpfeedshdr import HPFhandler
from utils import ext_ip
import json
import string
import ConfigParser
import time
import logging

logger = logging.getLogger(__name__)

# for hpfeeds
class FeedWorker(object):
    def __init__(self, config):
        self.config = config
        config = ConfigParser.ConfigParser()
        config.read(self.config)

	self.public_ip = None
	if config.getboolean('fetch_public_ip', 'enabled'):
            urls = json.loads(config.get('fetch_public_ip', 'urls'))
            self.public_ip = ext_ip.get_ext_ip(urls)

        if config.getboolean('hpfeeds', 'enabled'):
            host = config.get('hpfeeds', 'host')
            port = config.getint('hpfeeds', 'port')
            ident = config.get('hpfeeds', 'ident')
            secret = config.get('hpfeeds', 'secret')
            channels = eval(config.get('hpfeeds', 'channels'))
            try:
                self.feeder = HPFhandler(host, port, ident, secret, channels)
                self.feeder._start_connection()
            except Exception as e:
                logger.exception(e.message)
                self.friends_feeder = None

    def push(self,data):
        if self.feeder:
            self.feeder.feeddata(json.dumps(data))



#def init_server(port=502):
def init_server(port=None):
	UDP_LIST = [2123, 2152, 3386, 5006, 5007, 5094, 17185, 30718, 34962, 44818, 47808]
	# UDP
	if port in UDP_LIST:
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	    s.bind(('', port))
	    logger.info('Server listening port : %s', port)
	# TCP
	else:
	    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    s.bind(('', port))
	    s.listen(1)
	    logger.info('Server listening port : %s', port)

	logs = open('./iec.log', 'a', 0)
	#sys.stdout = logs
	loop(s, logs, port)


def handle(conn, addr, logs, port):
	# for Hpfeeds
	st =FeedWorker("hpfeeds.conf")
	public_ip =  st.public_ip
	hptime = time.strftime('%Y-%m-%d %H:%M:%S')
	all_protocol = {'102':'s7comm', '502': 'modbus', '771':'RealPort', '789':'Red Lion', '1200':'Codesys', '1911':'Tridium Fox', '1962':'PCWorx', '2123':'GPRS Tunneling', '2152':'GPRS Tunneling', '2404':'IEC104', '2455':'Codesys', '3386':'GPRS Tunneling', '4991':'Tridium Fox SSL', '5006':'Mitsubishi MELSEC', '5007':'Mitsubishi MELSEC', '5094':'HART-IP', '9600':'OMRON FINS', '17185':'Vxworks WDB', '18245':'GE SRTP', '18246':'GE SRTP', '20000':'DNP3', '20547':'ProConOS', '30718':'Lantronix', '34962':'Profinet', '37777':'Dahua Dvr', '44818':'EtherNet/IP', '47808':'bacnet'}

	#buffer = array('B', [0]*30)
	buffer = None
	while 1:
		try:
			buffer = conn.recv(1024)
			if len(buffer) > 0:
                            hp = {
        		            'remote': [addr[0],None],
                		    'data_type': all_protocol[str(port)],
	                	    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        	        	    'public_ip': public_ip,
	                	    'data': {'request':buffer.encode('hex'),'response': None,},
		                    'id': None
                                 }
                            st.push(hp)
                            logger.info(hp)
			    logger.info(str(hexdump(buffer)))
                            logger.info('Received data:%s', hexdump(buffer))
			    conn.send(buffer)
			    sleep(1)
			else:
				logger.info("Connection lost")
				#exit(1)
				break

		except Exception, e:
                    logger.error(e)
                    logger.info("Connection terminated")
		    #exit(1)
                    break

def handle_udp(s, addr, data_buffer, logs, port):
	# for Hpfeeds
	st =FeedWorker("hpfeeds.conf")
	public_ip =  st.public_ip
	hptime = time.strftime('%Y-%m-%d %H:%M:%S')
	all_protocol = {'102':'s7comm', '502': 'modbus', '771':'RealPort', '789':'Red Lion', '1200':'Codesys', '1911':'Tridium Fox', '1962':'PCWorx', '2123':'GPRS Tunneling', '2152':'GPRS Tunneling', '2404':'IEC104', '2455':'Codesys', '3386':'GPRS Tunneling', '4991':'Tridium Fox SSL', '5006':'Mitsubishi MELSEC', '5007':'Mitsubishi MELSEC', '5094':'HART-IP', '9600':'OMRON FINS', '17185':'Vxworks WDB', '18245':'GE SRTP', '18246':'GE SRTP', '20000':'DNP3', '20547':'ProConOS', '30718':'Lantronix', '34962':'Profinet', '37777':'Dahua Dvr', '44818':'EtherNet/IP', '47808':'bacnet'}

	#buffer = array('B', [0]*30)
	buffer = None
	try:
		buffer = data_buffer
		if len(buffer) > 0:
	                hp = {
       		            'remote': [addr[0],None],
               		    'data_type': all_protocol[str(port)],
                	    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
       	        	    'public_ip': public_ip,
                	    'data': {'request':buffer.encode('hex'),'response': None,},
	                    'id': None,
       		            }

	                st.push(hp)
                        logger.info(hp)
                        logger.info(str(hexdump(buffer)))
                        logger.info('Received data:%s', hexdump(buffer))
			s.sendto(buffer, addr)
			sleep(1)
		else:
			logger.info("Connection lost")
			exit(1)

	except Exception, e:
            logger.error(e)
            logger.info("Connection terminated")
	    exit(1)




def loop(s, logs, port):
	UDP_LIST = [2123, 2152, 3386, 5006, 5007, 5094, 17185, 30718, 34962, 44818, 47808]
	while 1:
		if port in UDP_LIST:
			data_buffer, addr = s.recvfrom(1024)
			if len(data_buffer)>0:
				logger.info('New connection from %s:%s' ,addr[0] ,port)
				thread.start_new_thread(handle_udp, (s, addr, data_buffer, logs, port))
		else:
			conn, addr = s.accept()
			logger.info('New connection from %s:%s ' ,addr[0] ,port)
			thread.start_new_thread(handle, (conn, addr, logs, port))