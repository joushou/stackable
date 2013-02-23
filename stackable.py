#
# Stackables
#

class StackableError(Exception):
	'Indicates an error in the Stackable'
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

class Stackable(object):
	'''The Stackable object.

A Stackable provides 3 basic features:
 poll           - Poll for available data (if applicable).
 process_input  - Process a given input.
 process_output - Process a given output.

The functions return the post-processed data, allowing it to
continue propagation through the containing Stack.'''
	def __init__(self):
		self._feed = None

	def _input(self, data):
		'Internal feeding function for input.'
		return self.process_input(data)

	def _output(self, data):
		'Internal feeding function for output.'
		return self.process_output(data)

	def _attach(self, feed):
		self._feed = feed

	def _detach(self):
		del self._feed

	def poll(self):
		'Poll; to be implemented by subclass.'
		return NotImplemented

	def process_input(self, data):
		'Input processing; to be implemented by subclass'
		return NotImplemented

	def process_output(self, data):
		'Output processing; to be implemented by subclass'
		return NotImplemented

class BufferedStackable(Stackable):
	'''Buffered variant of Stackable.

Adds input_ready and output_ready methods for determining when data is
ready for processing.'''
	def __init__(self):
		self.input_buffer  = None
		self.output_buffer = None
		super(BufferedStackable, self).__init__()

	def _input(self, data):
		'''Appends to the input buffer.
If self.input_ready evaluates true on the current buffer,
self.process_input is called with current buffer.'''
		if self.input_buffer != None:
			self.input_buffer += data
		else:
			self.input_buffer = data

		if self.input_ready(self.input_buffer):
			x = self.input_buffer
			self.input_buffer = None
			return self.process_input(x)

	def _output(self, data):
		'''Appends to the output buffer.
If self.output_ready evaluates true on the current buffer,
self.process_output is called with current buffer.'''
		if self.output_buffer != None:
			self.output_buffer += data
		else:
			self.output_buffer = data

		if self.output_ready(self.output_buffer):
			x = self.output_buffer
			self.output_buffer = None
			return self.process_output(x)

	def input_ready(self, data):
		'Function to evaluate current state of input buffer.'
		return NotImplemented

	def output_ready(self, data):
		'Function to evaluate current state of output buffer.'
		return NotImplemented
