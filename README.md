stackable
=========

Stackable IO system for Python

It's comprised of the following components:

* Stackable
The superclass for Stackable IO objects, and provides 3 methods to be overridden: process_input, process_output and poll.
The BufferedStackable also implements input_ready and output_ready, which can be overridden with logic to determine if enough data has been accumulated for processing.

* Stack
The container for Stackables, that handle data propagation. It is a subclass of IOBase to allow use as file-like object.
It also provides a poll method that will poll the first pollable Stackable on the stack, and can propagate data both ways through the stack.

* Network
Simple implementations of socket and packet assembly, in the form of StackableSocket and StackablePacketAssembler

* Cryptography
Simple stream cipher (ARC4). I might add more here.

* Utilities
Simple implementations of simple utilities, such as StackablePickler, StackableJSON and StackablePrinter

It's a project that spawned from a simple idea of abstracting data manipulation into common, connectable blocks within a different project. (My Mother-Of-All-Projects, "synapse")
I decided to separate the projects as part of my usual codebase-cleanups, as well as to make it available to anyone who would be crazy enough to use the project, either directly or for inspiration.
