#
# Network Stackables
#

from __future__ import print_function, absolute_import, unicode_literals, division
from stackable.stackable import Stackable, BufferedStackable, StackableError
from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack

class StackableSocket(Stackable):
	'Stackable socket wrapper'
	def __init__(self, sock=None, ip=None, port=None):
		super(Stackable, self).__init__()
		try:
			if sock != None:
				self.socket = sock
			else:
				self.socket = socket(AF_INET, SOCK_STREAM)
			self.socket.settimeout(None)
			if None not in (ip, port):
				self.socket.connect((ip, port))
		except:
			raise StackableError('Error occured while connecting socket')

	def process_input(self, data):
		return data

	def process_output(self, data):
		try:
			self.socket.sendall(data)
		except:
			raise StackableError('Error occured while writing to socket')
		return data

	def poll(self):
		try:
			a = self.socket.recv(10240)
		except:
			raise StackableError('Error occured while reading from socket')
		if a == b'':
			raise StackableError('Connection closed')
		else:
			return a

class StackablePacketAssembler(BufferedStackable):
	'''Stackable packet layer - Provides both assembly and disassembly of packets.
	Uses length-header to determine length of payload, and supports a 4-byte header magic.'''
	def __init__(self, magics=[(1,3,3,7)], acceptAllMagic=False):
		super(StackablePacketAssembler, self).__init__()
		self.acceptAllMagic = acceptAllMagic
		self.magics = magics
		self.buf = b''
		self.state = 0
		self.bleft = 4
		self.len = 0
		self.dropped = 0
		self.hdr = []
		self.sndhdr = magics[0]

	def input_ready(self, data):
		'Check if the we\'ve received the expected amount'
		if (self.bleft - len(data)) <= 0:
			self.bleft -= len(data)
			return True
		return False

	def process_input(self, data):
		'Process the input for packet disassembly'
		self.buf += data
		while self.bleft <= 0:
			if self.state == 0:
				# Header
				self.hdr = unpack(str('!4B'), self.buf[0:4])
				if self.hdr not in self.magics and not self.acceptAllMagic:
					# If the header is incorrect,
					#  stuff all but the first byte back and retry
					self.buf = self.buf[1:]
					self.bleft += 4
					self.dropped += 1
					continue

				self.buf = self.buf[4:]
				self.bleft += 4
				self.state += 1
			elif self.state == 1:
				# Size marker
				self.len = unpack(str('!I'), self.buf[0:4])[0]

				self.buf = self.buf[4:]
				self.bleft += self.len
				self.state += 1
			elif self.state == 2:
				# Payload
				z = unpack((str('!%ds') % self.len), self.buf[0:self.len])[0]

				self.buf = self.buf[self.len:]
				self.bleft += 4
				self.state = 0
				return z

	def process_output(self, data):
		packedMsg  = pack((str('!%ds') % len(data)), data)
		packedHdr1 = pack(str('!4B'), self.sndhdr[0],
		                  		 self.sndhdr[1],
		                  		 self.sndhdr[2],
		                  		 self.sndhdr[3])
		packedHdr2 = pack(str('!I'), len(packedMsg))
		return packedHdr1 + packedHdr2 + packedMsg

