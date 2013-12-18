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
