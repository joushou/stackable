#
# Network Stackables
#

from stackable import Stackable, BufferedStackable, StackableError
from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack

class StackableSocket(Stackable):
	'Stackable socket wrapper'
	def __init__(self, sock=None, ip=None, port=None):
		super(Stackable, self).__init__()
		if sock != None:
			self.socket = sock
		else:
			self.socket = socket(AF_INET, SOCK_STREAM)
		self.socket.settimeout(None)
		if None not in (ip, port):
			self.socket.connect((ip, port))

	def __del__(self):
		self.socket.close()

	def process_input(self, data):
		return data

	def process_output(self, data):
		self.socket.sendall(data)

	def poll(self):
		a = self.socket.recv(10240)
		if a == b'':
			raise StackableError('Connection closed')
		else:
			return a

class StackablePacketAssembler(BufferedStackable):
	'''Stackable packet layer - Provides both assembly and disassembly of packets.
	Uses length-header to determine length of payload, and supports a 4-byte header magic.'''
	def __init__(self, magics=[[1,3,3,7]]):
		super(StackablePacketAssembler, self).__init__()
		self.magics = magics
		self.buf = b''
		self.bleft = 4
		self.dropped = 0
		self.reset()

	def reset(self):
		'Reset state'
		self.len = 0
		self.hdr = []
		self.state = 0
		self.sndhdr = self.magics[0]

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
				self.hdr = unpack('!4B', self.buf[0:4])
				if self.hdr not in self.magics:
					# If the header is incorrect,
					#  stuff all but the first byte back and retry
					self.buf = self.buf[1:]
					self.bleft += 4
					self.dropped += 1
					self.reset()
					continue

				self.buf = self.buf[4:]
				self.bleft += 4
				self.state += 1
			elif self.state == 1:
				# Size marker
				self.len = unpack('!I', self.buf[0:4])[0]

				self.buf = self.buf[4:]
				self.bleft += self.len
				self.state += 1
			elif self.state == 2:
				# Payload
				z = unpack(('!%ds' % self.len), self.buf[0:self.len])[0]

				self.buf = self.buf[self.len:]
				self.bleft += 4
				self.reset()
				return z

	def process_output(self, data):
		packedMsg  = pack(('!%ds' % len(data)), data)
		packedHdr1 = pack('!4B', self.sndhdr[0],
		                  		 self.sndhdr[1],
		                  		 self.sndhdr[2],
		                  		 self.sndhdr[3])
		packedHdr2 = pack('!I', len(packedMsg))
		return packedHdr1 + packedHdr2 + packedMsg

