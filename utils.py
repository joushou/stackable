#
# Utility stackables
#

from __future__ import print_function, absolute_import, unicode_literals, division
from stackable.stackable import Stackable, StackableError
import json, pickle
from time import sleep
from threading import Thread
from datetime import datetime, timedelta

class StackablePickler(Stackable):
	'Pickle codec'
	def process_input(self, data):
		return pickle.loads(data)

	def process_output(self, data):
		return pickle.dumps(data, protocol=2)

class StackableJSON(Stackable):
	'JSON codec'
	def process_input(self, data):
		return json.loads(data)

	def process_output(self, data):
		return json.dumps(data)

class StackableWriter(Stackable):
	'Reads and writes from/to a file'
	def __init__(self, filename):
		super(StackableWriter, self).__init__()
		self.fd = open(filename, "r+")

	def processInput(self, data):
		self.fd.write(data)

	def poll(self):
		return self.fd.read()

class StackablePrinter(Stackable):
	'''Prints all input and output, and returns it unmodified.
	Useful for quick debugging of Stackables.'''
	def __init__(self, printer=print):
		'Takes a printing function as argument - defaults to print'
		self.printer = printer
		super(StackablePrinter, self).__init__()

	def process_input(self, data):
		self.printer(data)
		return data

	def process_output(self, data):
		self.printer(data)
		return data

class StackablePoker(Stackable):
	def __init__(self):
		super(StackablePoker, self).__init__()
		self.reset()

	def reset(self):
		self.timestamp = datetime.now()
		def ping():
			sleep(20)
			self._feed('__stack_ping')
		Thread(target=ping).start()

	def process_output(self, data):
		if (datetime.now() - self.timestamp) > timedelta(seconds=30):
			raise StackableError('Pong not received')
		return data

	def process_input(self, data):
		if data == '__stack_pong':
			self.reset()
			return None
		elif data == '__stack_ping':
			self._feed('__stack_pong')
			return None
		elif (datetime.now() - self.timestamp) > timedelta(seconds=30):
			raise StackableError('Pong not received')
		return data
