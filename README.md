# live-dhcpd-leases
compile a list of live leases handed out by a local dhcpd server
includes ping for each ip address, this can be slow for many ip addresses therefor this brach shall be kept seperate.
a stable dictionary of mac addresses and client's to create a more complete table when client's field is not populated in dhcpd.leases
