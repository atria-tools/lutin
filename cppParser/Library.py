#!/usr/bin/python
import LutinDebug as debug
import os
import sys
import re

class Libray():
	def __init__(self, libName):
		self.name = libName
		# CPP section:
		self.namespaces = []
		self.classes = []
		# C section:
		self.structs = []
		self.variables = []
		self.methodes = []
		self.unions = []
		self.types = []
	
	

