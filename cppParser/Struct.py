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

import inspect

class CppStruct(dict):
    Structs = []
    def __init__(self, nameStack):
        if len(nameStack) >= 2: self['type'] = nameStack[1]
        else: self['type'] = None
        self['fields'] = []
        self.Structs.append( self )
        global curLine
        self["line_number"] = curLine
