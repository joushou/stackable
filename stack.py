#
# Stack - The Stackable container
#

from __future__ import print_function, absolute_import, unicode_literals, division
from stackable.stackable import Stackable
from io import IOBase

class StackError(Exception):
	'Indicates an error in the Stack'
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

class Stack(IOBase):
	'Container for Stackables.'
	def __init__(self, s):
		'Takes a list of Stackables to attach upon construction as an argument.'
		self.stack = []
		self.stacklen = 0
		for i in s:
			self.attach(i)

	def __getitem__(self, key):
		return self.stack.__getitem__(key)

	def __contains__(self, key):
		return self.stack.__getitem__(key)

	def seekable(self): return False
	def writable(self): return True
	def readable(self): return True

	def attach(self, stobj, index=-1):
		'''Attach a stackable at a given index.
If no index is provided, it will be put at the end of the stack.'''
		if stobj == None or not isinstance(stobj, Stackable):
			raise StackError('Object must be Stackable')

		if index < -1:
			raise StackError('Index invalid')

		if index == -1:
			index = self.stacklen

		self.stack.insert(index, stobj)
		self.stacklen = len(self.stack)
		stobj._attach(self)

	def detach(self, stobj):
		'Detach a stackable.'
		self.stack.remove(stobj)
		stobj._detach()
		self.stacklen = len(self.stack)

	def close(self):
		'''Close the stack.
Calls detach on all Stackables.'''
		x = self.stack
		for i in x:
			self.detach(i)
		del x

	def _feed(self, s, a, invert=False, through_self=False):
		'''Internal feeding function.
Used by Stackables that propagate data as part of initialization.'''
		try:
			if invert:
				pos = self.stack.index(s)
			else:
				pos = self.stacklen - self.stack.index(s)

			if through_self:
				pos -= 1
		except ValueError:
			raise StackError('Object not in stack')
		else:
			self.write(a, offset=pos, invert=invert)

	def write(self, a, offset=0, invert=False):
		'''Run data through the stack.'''
		if offset > self.stacklen:
			raise StackError('Offset past length of Stack')

		if invert:
			for i in range(offset, self.stacklen, 1):
				a = self.stack[i]._input(a)
				if a == None: break
			else:
				return a
		else:
			for i in range(self.stacklen-offset-1, -1, -1):
				a = self.stack[i]._output(a)
				if a == None: break
			else:
				return a

	def poll(self, offset=0, invert=False):
		'Poll the stack for input.'
		if offset > self.stacklen:
			raise StackError('Offset past length of Stack')

		itr = range(offset, self.stacklen, 1) if invert else range(self.stacklen-offset-1, -1, -1)

		for i in itr:
			a = self.stack[i].poll()
			if a == NotImplemented:
				continue
			if a != None:
				if i == self.stacklen:
					return a
				else:
					return self.write(a, offset=i+1, invert=True)
		else:
			raise StackError('No pollable Stackables on the stack.')

	def read(self):
		'Polls stack in loop until output is present.'
		ret = None
		while ret == None:
			ret = self.poll()
		return ret
