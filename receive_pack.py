from scapy.all import IP, ICMP, send, sniff
import datetime
import threading

ip1 = "35.228.216.59"
ip2 = "35.228.28.238"
ip3 = "35.228.78.149"
INTERVAL = 1
instanceNr = 1

# listIp = [ip1, ip2, ip3]
# listIP = [ip2]

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
		listDEAD = []

		for instanceIp in aliveInstances:
			marginError = aliveInstances[instanceIp]['time'] + datetime.timedelta(seconds = 2*INTERVAL)
			if timeNow > marginError:
				print("Instance with ip: " + str(instanceIp) + "is disconected")
				listDEAD.append(instanceIp)

		for Ips in listDEAD:
			del aliveInstances[Ips]

		time.sleep(INTERVAL)



t1 = threading.Thread(target=threadListen)
t2 = threading.Thread(target=checkAliveInstances)

t1.start()
t2.start()

t1.join()
t2.join()


# send(IP(dest)/ICMP())

# scapy.all.sr1(IP(dst=dest, ttl=0) / ICMP() / "X", verbose=0)

"""
create thread for listening to ICMP
crete theread for checking the alive instances
add lock pe dict de instance
"""


# pingr = IP(dst=dest)/ICMP()/"Hallo"
# x = scapy.all.sr(pingr)
# print(x)
#
#
# str(pkt[0][Raw].load)
# pkt = sniff(filter="icmp", count = 0)
