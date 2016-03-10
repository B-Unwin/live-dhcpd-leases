import argparse # allows command line arguments
from datetime import datetime
import os# use of ping command
import os.path
import pickle # opens and save dictionaries
client = None
ends = None
global leases
lease = None
leases = {}
MAC = None
now = datetime.now()
starts = None
VLAN = {}
# Start Parser for commandf line arguments and set variables
parser = argparse.ArgumentParser()
parser.add_argument("-D", "--detailed",
                    help="Print out a detailed table of current leases",
                    action="store_true")
parser.add_argument("-S", "--summary",
                    help="Print out a summary of current leases",
                    action="store_true")
parser.add_argument("-N", "--NoPing",
                    help="Do not Ping leased IP addresses",
                    action="store_true")
args = parser.parse_args()
if os.path.isfile('clients.pickle') == 1:
	with open('clients.pickle', 'rb') as handle:
		clients = pickle.load(handle)
else:# or create dictionary if none exists
	clients = {}
def find_lease(a_line):
	if a_line[:5] == 'lease':
		lease = a_line[-14:-2]
		octet = lease.split('.')
		if int(octet[3]) > 10:# static ip's below 11 are of no interest
			leases[lease] = []
			return lease
def find_start(a_line, lease):
	if a_line[:8] == '  starts':
		starts = a_line[-21:-2]
		if len(leases[lease])>0:
			last_starts = leases[lease][0]
			last_start = datetime.strptime(last_starts,'%Y/%m/%d %H:%M:%S')
			start = datetime.strptime(starts,'%Y/%m/%d %H:%M:%S')
			if last_start < start:
				leases[lease].remove[0,1]
				leases[lease].append(starts)
		leases[lease].append(starts)
		return starts
	return
def find_end(a_line, lease):
	if a_line[:6] == '  ends':
		ends = a_line[-21:-2]
		end = datetime.strptime(ends,'%Y/%m/%d %H:%M:%S')
		if end > now:
			leases[lease].append(ends)
			return ends
		else:
			del leases[lease]
			return 0
def find_mac(a_line, lease):
	if a_line[:19] == '  hardware ethernet':
		MAC = a_line[-19:-2]
		leases[lease].append(MAC)
		return MAC
def find_client(a_line, lease, MAC):
	if a_line[:17] == '  client-hostname':
		client = a_line[19:-3]
		leases[lease].append(client)
		leases[lease].append('(live)')
		clients[MAC] = client
		return client
def ping(ip):# Useful to ping each IP adress found in lease
	ping_command = 'sudo ping -c 1 -w 1 ' + ip + '> /dev/null'
	if os.system(ping_command) == 0:
		response = 1
	else:
		response = 0
	return response
with open('/var/lib/dhcp/dhcpd.leases', mode='r') as a_file:
	for a_line in a_file:
		newline = 1
		if lease == None:
			lease = find_lease(a_line)
			continue
		elif starts == None:
			starts = find_start(a_line, lease)
			continue
		elif ends == None:
			ends = find_end(a_line, lease)
			if ends == 0:
				lease = None
				starts = None
				ends = None
			continue
		elif lease in leases:
			if MAC == None:
				MAC = find_mac(a_line, lease)
				continue
			else:
				if client == None:
					client = find_client(a_line, lease, MAC)
					continue
		if a_line[:1] == '}':	
			if lease in leases:
				if len(leases[lease])<4:
					if MAC in clients:
						client = clients[MAC]
						leases[lease].append(client)
						leases[lease].append('(saved)')
					else:
						leases[lease].append('Unknown Client Name')
			lease = None
			starts = None
			ends = None
			MAC = None
			client = None
for ip in leases:
	octet = ip.split('.')
	if octet[2] in VLAN:
		VLAN[octet[2]][0] = VLAN[octet[2]][0] + 1
	else:
		VLAN[octet[2]] = []
		VLAN[octet[2]].append(1)
		VLAN[octet[2]].append(0)
	if args.NoPing == False:
		response = ping(ip)
		if response == 1:
			VLAN[octet[2]][1] = VLAN[octet[2]][1] + 1
			leases[ip].insert(3, 'reponding!')
		else:
			leases[ip].insert(3, 'no reponse')
if args.detailed:
	for ip in sorted(leases.keys()):
		print('%s, %s' % (ip, leases[ip]))
if args.summary:
	print ('There are %s active VLAN\'s on the network:' % (len(VLAN)))
	for sub_network in sorted(VLAN.keys()):
		if args.NoPing == False:
			print('VLAN %s has %s active leases, %s of which are responding to Pimg.' % (sub_network, VLAN[sub_network][0], VLAN[sub_network][1]))
		else:
			print('VLAN %s has %s active leases.' % (sub_network, VLAN[sub_network][0]))
with open('clients.pickle', 'wb') as handle:
	pickle.dump(clients, handle)

