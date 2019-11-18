from scapy.all import IP, ICMP, send, sniff, Raw
import datetime
import threading

ip1 = "35.228.216.59"
ip2 = "35.228.28.238"
ip3 = "35.228.78.149"
INTERVAL = 1

#current instance number
instanceNr = 1

listIp = [ip1, ip2, ip3]


aliveInstances = {}

def threadListen():
	pkt = sniff(filter="icmp", count = 0, prn=updateAliveInstances)

def updateAliveInstances(package):

	if('echo-reply' not in str(package.summary())):
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
			marginError = aliveInstances[instanceIp]['time'] + datetime.timedelta(seconds = 3*INTERVAL)
			if timeNow > marginError:
				print("Instance with ip: " + str(instanceIp) + " is disconected")
				print("Last pack nr " + str(aliveInstances[instanceIp]['count']))
				listDEAD.append(instanceIp)

		for Ips in listDEAD:
			del aliveInstances[Ips]

		time.sleep(INTERVAL)

def sendPack(destIp, ping_counter):
	ping = IP(dst=destIp)/ICMP()/Raw(load=str(ping_counter))
	send(ping, verbose=False)

def sendPackAtInterval():
	counter = 0
	while(1):
		time.sleep(INTERVAL)
		#ip to send messages to
		destIp = listIp[instanceNr%len(listIp)]
		counter = counter+1
		sendPack(destIp, counter)


t1_listen = threading.Thread(target=threadListen)
t2_checkInstances = threading.Thread(target=checkAliveInstances)
t3_sendPing = threading.Thread(target=sendPackAtInterval)

t1_listen.start()
t2_checkInstances.start()
t3_sendPing.start()

t1_listen.join()
t2_checkInstances.join()
t3_sendPing.join()
