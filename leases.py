from datetime import datetime
now = datetime.now()
written = 0
with open('leases.txt', mode='w') as b_file:
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
					line = lease+starts+' '+ends+' '+hardware+' '+client+'\n'
					b_file.write(line)
					written = 1
			elif a_line[:1] == '}':
				if written == 0:
					if end > now:
						line = lease+starts+' '+ends+' '+hardware+'\n'
						b_file.write(line)
				written = 0
with open('leases.txt', mode='r') as c_file:
	for b_line in c_file:
		print (b_line)
