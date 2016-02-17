from datetime import datetime
import os
import os.path
import pickle
now = datetime.now()
written = 0
leases = {}
def ping(ip):
	ping_command = 'sudo ping -c 1 -w 1 ' + ip + '> /dev/null'
	if os.system(ping_command) == 0:
		response = 'Responding!'
	else:
		response = 'No Response'
	return response
if os.path.isfile('clients.pickle') == 1:
	with open('clients.pickle', 'rb') as handle:
		clients = pickle.load(handle)
else:
	clients = {}
with open('/var/lib/dhcp/dhcpd.leases', mode='r') as a_file:
	for a_line in a_file:
		if a_line[:5] == 'lease':
			lease = a_line[-14:-2]
		if a_line[:8] == '  starts':
			starts = a_line[-21:-2]
		if a_line[:6] == '  ends':
			ends = a_line[-21:-2]
			end = datetime.strptime(ends, '%Y/%m/%d %H:%M:%S')
		if a_line[:19] == '  hardware ethernet':
			hardware = a_line[-19:-2]
		if a_line[:17] == '  client-hostname':
			client = a_line[19:-3]
			if end > now:
				response = ping(lease)
				clients[hardware] = client
				line = lease+starts+' '+ends+' '+hardware+' '+response+' '+client+' (live)'+'\n'
				leases[lease] = line
				written = 1
		elif a_line[:1] == '}':
			if written == 0:
				if end > now:
					response = ping(lease)
					if hardware in clients:
						client = clients[hardware]
						line = lease+starts+' '+ends+' '+hardware+' '+response+' '+client+' (saved)'+'\n'
					else:
						if lease in leases:
							Dict_leases = leases[lease]
							Dict_leases = Dict_leases[12:51]
							Dict_start = datetime.strptime(Dict_leases, '%Y/%m/%d %H:%M:%S')
							start = datetime.strptime(starts, '%Y/%m/%d %H:%M:%S')
							if Dict_start < start:
								line = Dict_leases
						line = lease+starts+' '+ends+' '+hardware+' '+response+'\n'
					leases[lease] = line
			written = 0
with open('clients.pickle', 'wb') as handle:
	pickle.dump(clients, handle)
for info in leases:
	info = leases[info]
	print (info)
