from scapy.all import IP, ICMP, send, sniff, Raw
import datetime
import threading

ip1 = "35.228.216.59"
ip2 = "35.228.28.238"
ip3 = "35.228.78.149"
INTERVAL = 1
instanceNr = 1

instanceCenter = ip1

def sendPack(destIp, ping_counter):
	ping = IP(dst=destIp)/ICMP()/Raw(load=str(ping_counter))
	send(ping)

counter = 1
while(1):
	time.sleep(INTERVAL)
	counter = counter+1
	sendPack(instanceCenter, counter)
