from scapy.all import IP, ICMP, send, sniff, Raw
import datetime
import threading

ip1 = "35.228.216.59"
ip2 = "35.228.28.238"
ip3 = "35.228.78.149"
INTERVAL = 1


aliveInstances = {}

def threadListen():
	pkt = sniff(filter="icmp", count = 0, prn=updateAliveInstances)

def updateAliveInstances(package):

	receivedIp = package[IP].src
	cout_nr = int(package[Raw].load.decode("utf-8"))

	if receivedIp in aliveInstances.keys():
		aliveInstances[receivedIp]['time'] = datetime.datetime.now()
		aliveInstances[receivedIp]['count'] = cout_nr
	else:
		print("New ip registred: " + str(receivedIp))
		aliveInstances[receivedIp] = {'time' : datetime.datetime.now(), 'count' : cout_nr}

def checkAliveInstances():

	while(1):
		timeNow = datetime.datetime.now()
		listDEAD = []

		for instanceIp in aliveInstances:
			marginError = aliveInstances[instanceIp]['time'] + datetime.timedelta(seconds = 2*INTERVAL)
			if timeNow > marginError:
				print("Instance with ip: " + str(instanceIp) + " is disconected")
				print("Last pack nr " + str(aliveInstances[instanceIp]['count']))
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
