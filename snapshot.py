from scapy.all import IP, ICMP, send, sniff, Raw, sr1
import datetime
import threading
import random 

ip1 = "35.228.216.59"
ip2 = "35.228.28.238"
ip3 = "35.228.78.149"
INTERVAL = 1
global_cont = 0

# current instance number
instanceNr = 1

listIp = [ip1, ip2, ip3]

listIpsToForwardToken = [ip2]

listAliveInstances = None

current_snapshot = None

received_token_from_ip = None

token_sent = None


"""
	use to create a indentifier for token 
	if case u receive your own token back
"""
tokenHash = -1



def threadListen():
	sniff(filter="icmp", count = 0, prn=handleTraffic)

def send_message(ip, message_type, load):
	message = None
	if(message_type == 'empty message'):
		#create empty snapshot
		message = IP(dst=ip)/ICMP()/Raw(load=str('snapshot='))
	if(message_type == 'send token'):
		message = IP(dst=ip)/ICMP()/Raw(load=str('tokenHash=' + str(load)))
	if(message_type == 'send snapshot'):
		message = IP(dst=ip)/ICMP()/Raw(load=str('snapshot=' + str(load)))
	send(message, verbose=True)

def check_received_all_requested_snaps():
	global current_snapshot, listAliveInstances, received_token_from_ip, tokenHash, token_sent
	while(1):
		time.sleep(1)
		# it starts only when we send the first token
		if(tokenHash != -1 and token_sent == True):
			ok = True
			for i in listAliveInstances:
				# means snapshots are not back yet
				if(i == True):
					ok = False

			if(ok):
				send_message(received_token_from_ip, 'send snapshot', current_snapshot)
				print("Full snapshot :")
				print(current_snapshot)
				current_snapshot = None
				listAliveInstances = None
				received_token_from_ip = None
				tokenHash = -1

def handleTraffic(package):
	receivedIp = package[IP].src
	global tokenHash
	global listAliveInstances
	global current_snapshot
	global received_token_from_ip 

	#test for echo-request only
	if(package[ICMP].type == 8):

		if('tokenHash' in package[Raw].load.decode("utf-8")):
			tempTokenHash = package[Raw].load.decode("utf-8").split('=')[1]

			#check if we receive the same token that we send --- for the case we are in a loop
			if(tempTokenHash == tokenHash):
				# in this case we will reply something an empty message
				send_message(receivedIp, 'empty message', None)

			if(tempTokenHash != tokenHash and tokenHash == -1):
				#received token for first time
				#propagate and initialise snapshot 
				
				tokenHash = tempTokenHash
				propagate_token(tokenHash)
				received_token_from_ip = receivedIp

		if('snapshot' in package[Raw].load.decode("utf-8") and tokenHash != -1):
			snapLoad = package[Raw].load.decode("utf-8").split('=')[1]
			ipIndex = listIpsToForwardToken.index(str(receivedIp)) if str(receivedIp) in listIpsToForwardToken else None
			if(ipIndex != None):
				current_snapshot = current_snapshot + snapLoad
				listAliveInstances[ipIndex] = 'Received'

def propagate_token(tokenId):
	global token_sent
	
	# before we send the token we need to check which machines are still alive
	initialise_listAliveInstance()
	global listAliveInstances

	#init snap_shot
	global current_snapshot

	current_snapshot = str(listIp[instanceNr -1]) + ' : ' + str(global_cont) + '\n'


	for i in range(len(listIpsToForwardToken)):
		echo_ping = IP(dst=listIpsToForwardToken[i])/ICMP()/Raw(load=str('echo request'))
		echo_reply = sr1(echo_ping, verbose=False, timeout=1)
		if (echo_reply != None):
			listAliveInstances[i] = True
			send_message(listIpsToForwardToken[i], 'send token', tokenId)

	token_sent = True

def request_snapshot():
	global tokenHash

	if(tokenHash == -1):
		tokenHash = random.randint(0, 10000)
		propagate_token(tokenHash)

def read_user_input():
	while(1):
		command = input()
		if(command == 'ss'):
			request_snapshot()

def increment_cont():
	global global_cont
	while(1):
		time.sleep(INTERVAL)
		global_cont = global_cont + 1

def initialise_listAliveInstance():
	global listAliveInstances

	if(listAliveInstances == None):
		listAliveInstances = []
	for i in range(len(listIpsToForwardToken)):
			listAliveInstances.append(None)



t1_read_input = threading.Thread(target=read_user_input)
t2_increment_cont = threading.Thread(target=increment_cont)
t3_sniff_packages = threading.Thread(target=threadListen)
t4_check_snapshots = threading.Thread(target=check_received_all_requested_snaps)


t1_read_input.start()
t2_increment_cont.start()
t3_sniff_packages.start()
t4_check_snapshots.start()

t1_read_input.join()
t2_increment_cont.join()
t3_sniff_packages.join()
t4_check_snapshots.join()
