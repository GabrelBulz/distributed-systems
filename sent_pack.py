from scapy.all import IP, ICMP, send, sniff
import datetime
import threading

ip1 = "35.228.216.59"
ip2 = "35.228.28.238"
ip3 = "35.228.78.149"
INTERVAL = 1
instanceNr = 1

# listIp = [ip1, ip2, ip3]
listIP = [ip2]

aliveInstances = {}

def threadListen():
	pkt = sniff(filter="icmp", count = 0, prn=updateAliveInstances)

def updateAliveInstances(package):

	receivedIp = package[IP].src

	if receivedIp in aliveInstances.keys():
		aliveInstances[receivedIp]['time'] = datetime.datetime.now()
	else:
		print("New ip registred: " + str(receivedIp))
		aliveInstances[receivedIp] = {'time' : datetime.datetime.now()}

def checkAliveInstances():

	while(1):
		timeNow = datetime.datetime.now()

		for instanceIp in aliveInstances:
			marginError = aliveInstances[instanceIp]['time'] + datetime.timedelta(seconds = 2*INTERVAL)
			if timeNow > marginError:
				print("Instance with ip: " + str(instanceIp) + "is disconected")
				del aliveInstances[instanceIp]



def sendPack(destIp):
	ping = IP(dst=destIp)/ICMP()
	send(ping)

# try:
# 	thread.start_new_thread(updateAliveInstances)
# 	thread.start_new_thread(checkAliveInstances)
# except Exception as e:
# 	raise

while(1):
	time.sleep(INTERVAL)
	sendPack(ip2)

# send(IP(dest)/ICMP())

# scapy.all.sr1(IP(dst=dest, ttl=0) / ICMP() / "X", verbose=0)

"""
create thread for listening to ICMP
crete theread for checking the alive instances
"""


# pingr = IP(dst=dest)/ICMP()/"Hallo"
# x = scapy.all.sr(pingr)
# print(x)
#
#
# str(pkt[0][Raw].load)
# pkt = sniff(filter="icmp", count = 0)
