#
# Cryptographic Stackables
#

from __future__ import print_function, absolute_import, unicode_literals, division
from stackable.stackable import Stackable, BufferedStackable
from crypto.rabbit import Rabbit

class StackableRabbit(Stackable):
	def __init__(self, key, iv):
		super(StackableRabbit, self).__init__()
		self.rabbit = Rabbit()
		self.rabbit.keysetup(key)
		self.rabbit.ivsetup(iv)
		self.rabbit.savestate()
		self.iv = iv

	def process_input(self, data):
		self.rabbit.restorestate()
		return bytes(self.rabbit.encrypt(bytearray(data)))

	def process_output(self, data):
		self.rabbit.restorestate()
		return bytes(self.rabbit.encrypt(bytearray(data)))

class StackableARC4(Stackable):
	def __init__(self, key='Key', state_size = 256):
		super(StackableARC4, self).__init__()
		if self.initialized == False:
			self.k = bytearray(key)
			self.ss = state_size
			self.initialized = True

	def reset(self):
		kl = len(self.k)
		self.j = 0
		self.i = 0
		self.state = []
		self.sl = 0
		self.state = [i for i in range(self.ss)]
		j = 0
		for i in range(self.ss):
			j = (j + self.state[i] + self.k[i % kl]) % self.ss

			self.state[i] ^= self.state[j]
			self.state[j] ^= self.state[i]
			self.state[i] ^= self.state[j]
		self.sl = len(self.state)

	def prng(self):
		self.i = (self.j + 1) % self.sl
		self.j = (self.j + self.state[self.i]) % self.sl

		self.state[self.i] ^= self.state[self.j]
		self.state[self.j] ^= self.state[self.i]
		self.state[self.i] ^= self.state[self.j]

		return self.state[(self.state[self.i] + self.state[self.j]) % self.sl]

	def process_input(self, data):
		self.reset()
		a = bytearray(b'')
		for i in bytearray(data):
			a.append(self.prng() ^ i)
		self.inputBuffer = None
		return str(a)

	def process_output(self, data):
		self.reset()
		a = bytearray(b'')
		for i in bytearray(data):
			a.append(self.prng() ^ i)
		self.outputBuffer = None
		return str(a)
