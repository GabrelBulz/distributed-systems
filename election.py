from scapy.all import IP, ICMP, send, sniff, Raw, sr1
import datetime
import threading
import random 

ip1 = "35.228.216.59"
ip2 = "35.228.28.238"
ip3 = "35.228.78.149"
INTERVAL = 1

# current instance number
instanceNr = 1

listIp = [ip1, ip2, ip3]

listIpsToForwardToken = [ip2]

listAliveInstances = None

my_ip = None

election_time = None


"""
	use to create a indentifier for token 
	if case u receive your own token back
"""




def threadListen():
	sniff(filter="icmp", count = 0, prn=handleTraffic)

def send_message(ip, message_type, load):
	message = None
	if(message_type == 'propagate election'):
		message = IP(dst=ip)/ICMP()/Raw(load=str('election:')+str(load))
	if(message_type == 'announce leader'):
		message = IP(dst=ip)/ICMP()/Raw(load=str('new_leader:' + str(load)))

	send(message, verbose=False)

def check_received_election():
	global election_time

	while(1):
		time.sleep(1)
		if(election_time is not None):
			curr_time = datetime.datetime.now()
			marginError = election_time + datetime.timedelta(seconds = 5)
			if curr_time > marginError:
				spread_leader(my_ip)
				print("i am the new leader")
				election_time = None

def handleTraffic(package):
	global election_time

	# #test for echo-request only
	if(package[ICMP].type == 8):

		if('election' in package[Raw].load.decode("utf-8")):
			proposed_leader = package[Raw].load.decode("utf-8").split(':')[1]

			if(proposed_leader != my_ip):

				if(my_ip > proposed_leader):
					spread_election(my_ip)
				else:
					spread_election(proposed_leader)

		if('new_leader' in package[Raw].load.decode("utf-8")):
			election_time = None
			new_leader = package[Raw].load.decode("utf-8").split(':')[1]
			if(new_leader != my_ip):
				print("The new leader is " + str(new_leader))

def spread_leader(ip):
	for i in listIp:
		if(i != my_ip):
			send_message(i, 'announce leader', ip)

def spread_election(ip):
	global election_time

	list_bigger_instance = []

	flag_send_election = None

	for i in listIp:
		if(i > my_ip):
			flag_send_election = True
			send_message(i, "propagate election", ip)
			election_time = datetime.datetime.now()

	if(flag_send_election is None):
		print("I am the new leader")
		spread_leader(my_ip)
		election_time = None


def read_user_input():
	while(1):
		command = input()
		if(command == 'election'):
			spread_election(my_ip)

my_ip = listIp[instanceNr]

t1_read_input = threading.Thread(target=read_user_input)
t2_increment_cont = threading.Thread(target=check_received_election)
t3_sniff_packages = threading.Thread(target=threadListen)


t1_read_input.start()
t2_increment_cont.start()
t3_sniff_packages.start()

t1_read_input.join()
t2_increment_cont.join()
t3_sniff_packages.join()
