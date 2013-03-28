#
# Utility stackables
#

from __future__ import print_function, absolute_import, unicode_literals, division
from stackable.stackable import Stackable, StackableError
import json, pickle
from time import sleep
from threading import Thread, Event
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

from collections import deque
class StackableInjector(Stackable):
	def __init__(self):
		super(StackableInjector, self).__init__()
		self.in_buf = deque()
		self.out_buf = deque()

	def push(self, data):
		self.in_buf.append(data)

	def poll(self):
		if len(self.in_buf):
			return self.in_buf.popleft()
		return None

	def process_output(self, data):
		self.out_buf.append(data)
		return data

class StackablePoker(Stackable):
	def __init__(self, interval=20, send=True, ping_string='__stack_ping', pong_string='__stack_pong'):
		super(StackablePoker, self).__init__()
		self.ping_string = ping_string.encode('utf-8')
		self.pong_string = pong_string.encode('utf-8')
		self.w = Event()
		self.interval = interval
		self.send = send
		if self.send:
			self.reset()

	def _detach(self):
		super(StackablePoker, self)._detach()
		self.w.set()

	def reset(self):
		self.timestamp = datetime.now()
		def ping():
			print("[POKER] Waiting %d secs before pinging" % self.interval)
			self.w.wait(self.interval)
			try:
				self._feed(self.ping_string)
				print("[POKER] Sent ping")
			except:
				print("[POKER] Couldn't send ping")
				pass
		x = Thread(target=ping)
		x.daemon = True
		x.start()

	def process_output(self, data):
		if self.send and (datetime.now() - self.timestamp) > timedelta(seconds=30):
			raise StackableError('Pong not received')
		return data

	def process_input(self, data):
		if data == self.pong_string:
			print("[POKER] Received pong")
			self.reset()
			return None
		elif data == self.ping_string:
			print("[POKER] Received ping & sending pong")
			self._feed(self.pong_string)
			return None
		elif self.send and (datetime.now() - self.timestamp) > timedelta(seconds=30):
			raise StackableError('Pong not received')
		return data
