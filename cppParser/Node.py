#!/usr/bin/python
try :
	# normal install module
	import ply.lex as lex
except ImportError :
	# local module
	import lex
import os
import sys
import re

class Node():
	def __init__(self):
		self.name = ""
		self.doc = None
		self.fileName = ""
		self.lineNumber = ""
		
	def to_str():
		return ""


