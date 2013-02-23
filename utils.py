#
# Utility stackables
#

from __future__ import print_function, absolute_import, unicode_literals, division
from stackable.stackable import Stackable
import json, pickle

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
