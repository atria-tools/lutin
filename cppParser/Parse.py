#!/usr/bin/python
import os
import sys
import re

import lex

import inspect
import lutinDebug as debug
import lutinTools
import Class
import Namespace
import Struct
import Union
import Methode
import Enum
import Variable

tokens = [
	'NUMBER',
	'NAME',
	'OPEN_PAREN',
	'CLOSE_PAREN',
	'OPEN_BRACE',
	'CLOSE_BRACE',
	'OPEN_SQUARE_BRACKET',
	'CLOSE_SQUARE_BRACKET',
	'COLON',
	'SEMI_COLON',
	'COMMA',
	'TAB',
	'BACKSLASH',
	'PIPE',
	'PERCENT',
	'EXCLAMATION',
	'CARET',
	'COMMENT_SINGLELINE',
	'COMMENT_MULTILINE',
	'PRECOMP_MACRO',
	'PRECOMP_MACRO_CONT',
	'ASTERISK',
	'AMPERSTAND',
	'EQUALS',
	'MINUS',
	'PLUS',
	'DIVIDE',
	'CHAR_LITERAL',
	'STRING_LITERAL',
	'NEW_LINE',
	'SQUOTE',
]

t_ignore = " \r.?@\f"
t_NUMBER = r'[0-9][0-9XxA-Fa-f]*'
t_NAME = r'[<>A-Za-z_~][A-Za-z0-9_]*'
t_OPEN_PAREN = r'\('
t_CLOSE_PAREN = r'\)'
t_OPEN_BRACE = r'{'
t_CLOSE_BRACE = r'}'
t_OPEN_SQUARE_BRACKET = r'\['
t_CLOSE_SQUARE_BRACKET = r'\]'
t_SEMI_COLON = r';'
t_COLON = r':'
t_COMMA = r','
t_TAB = r'\t'
t_BACKSLASH = r'\\'
t_PIPE = r'\|'
t_PERCENT = r'%'
t_CARET = r'\^'
t_EXCLAMATION = r'!'
t_PRECOMP_MACRO = r'\#.*'
t_PRECOMP_MACRO_CONT = r'.*\\\n'
def t_COMMENT_SINGLELINE(t):
	r'\/\/.*\n'
	global doxygenCommentCache
	if t.value.startswith("///") or t.value.startswith("//!"):
		if doxygenCommentCache:
			doxygenCommentCache += "\n"
		if t.value.endswith("\n"):
			doxygenCommentCache += t.value[:-1]
		else:
			doxygenCommentCache += t.value
	t.lexer.lineno += len(filter(lambda a: a=="\n", t.value))
t_ASTERISK = r'\*'
t_MINUS = r'\-'
t_PLUS = r'\+'
t_DIVIDE = r'/(?!/)'
t_AMPERSTAND = r'&'
t_EQUALS = r'='
t_CHAR_LITERAL = "'.'"
t_SQUOTE = "'"
#found at http://wordaligned.org/articles/string-literals-and-regular-expressions
#TODO: This does not work with the string "bla \" bla"
t_STRING_LITERAL = r'"([^"\\]|\\.)*"'
#Found at http://ostermiller.org/findcomment.html
def t_COMMENT_MULTILINE(t):
	r'/\*([^*]|\n|(\*+([^*/]|\n)))*\*+/'
	global doxygenCommentCache
	if t.value.startswith("/**") or t.value.startswith("/*!"):
		#not sure why, but get double new lines
		v = t.value.replace("\n\n", "\n")
		#strip prefixing whitespace
		v = re.sub("\n[\s]+\*", "\n*", v)
		doxygenCommentCache += v
	t.lexer.lineno += len(filter(lambda a: a=="\n", t.value))
def t_NEWLINE(t):
	r'\n+'
	t.lexer.lineno += len(t.value)

def t_error(v):
	print( "Lex error: ", v )

lex.lex()

doxygenCommentCache = ""

supportedAccessSpecifier = [
	'public',
	'protected',
	'private'
]

##
## @brief Join the class name element : ['class', 'Bar', ':', ':', 'Foo'] -> ['class', 'Bar::Foo']
## @param table Input table to convert. ex: [':', '\t', 'class', 'Bar', ':', ':', 'Foo']
## @return The new table. ex: ['class', 'Bar::Foo']
##
def create_compleate_class_name(table):
	if "::" not in "".join(table):
		out = table
	else:
		# we need to convert it :
		out = []
		for name in table:
			if len(out) == 0: 
				out.append(name)
			elif     name == ":" \
			     and out[-1].endswith(":"):
				out[-1] += name
			elif out[-1].endswith("::"):
				out[-2] += out[-1] + name
				del out[-1]
			else:
				out.append(name)
	table = out
	if 'operator' not in "".join(table):
		out = table
	else:
		out = []
		for name in table:
			if len(out) == 0:
				out.append(name)
			elif     name in ['<','>','='] \
			     and out[-1][:8] == 'operator' \
			     and len(out[-1])-8 < 2:
				out[-1] += name
			else:
				out.append(name)
			
	return out


class parse_file():
	
	def gen_debug_space(self):
		ret = "[" + str(len(self.braceDepthType)+1) + "]"
		for iii in range(0,len(self.braceDepthType)):
			ret += "    "
		return ret
	
	def __init__(self, fileName):
		self.m_classes = []
		self.m_elementParseStack = []
		debug.info("Parse File tod document : '" + fileName + "'")
		
		self.headerFileName = fileName
		
		self.anon_union_counter = [-1, 0]
		# load all the file data :
		headerFileStr = lutinTools.FileReadData(fileName)
		
		# Make sure supportedAccessSpecifier are sane
		for i in range(0, len(supportedAccessSpecifier)):
			if " " not in supportedAccessSpecifier[i]: continue
			supportedAccessSpecifier[i] = re.sub("[ ]+", " ", supportedAccessSpecifier[i]).strip()
		
		# Strip out template declarations
		# TODO : What is the real need ???
		headerFileStr = re.sub("template[\t ]*<[^>]*>", "", headerFileStr)
		# remove all needed \r unneeded ==> this simplify next resExp ...
		headerFileStr = re.sub("\r", "\r\n", headerFileStr)
		headerFileStr = re.sub("\r\n\n", "\r\n", headerFileStr)
		headerFileStr = re.sub("\r", "", headerFileStr)
		# TODO : Can generate some error ...
		headerFileStr = re.sub("\#if 0(.*?)(\#endif|\#else)", "", headerFileStr, flags=re.DOTALL)
		
		debug.debug(headerFileStr)

		# Change multi line #defines and expressions to single lines maintaining line nubmers
		matches = re.findall(r'(?m)^(?:.*\\\n)+.*$', headerFileStr)
		is_define = re.compile(r'[ \t\v]*#[Dd][Ee][Ff][Ii][Nn][Ee]')
		for m in matches:
			#Keep the newlines so that linecount doesnt break
			num_newlines = len(filter(lambda a: a=="\n", m))
			if is_define.match(m):
				new_m = m.replace("\n", "<**multiLine**>\\n")
			else:
				# Just expression taking up multiple lines, make it take 1 line for easier parsing
				new_m = m.replace("\\\n", " ")
			if (num_newlines > 0):
				new_m += "\n"*(num_newlines)
			headerFileStr = headerFileStr.replace(m, new_m)
		
		#Filter out Extern "C" statements. These are order dependent
		headerFileStr = re.sub(r'extern( |\t)+"[Cc]"( |\t)*{', "{", headerFileStr)
		
		###### debug.info(headerFileStr)
		self.stack = [] # token stack to find the namespace and the element name ...
		self.nameStack = [] # 
		self.braceDepth = 0
		self.braceDepthType = []
		self.subModuleCountBrace = 0;
		lex.lex()
		lex.input(headerFileStr)
		self.curLine = 0
		self.curChar = 0
		while True:
			tok = lex.token()
			if not tok:
				break
			debug.debug("TOK: " + str(tok))
			self.stack.append( tok.value )
			self.curLine = tok.lineno
			self.curChar = tok.lexpos
			# special case to remove internal function define in header:
			if self.previous_is('function') == True:
				if tok.type == 'OPEN_BRACE':
					self.subModuleCountBrace += 1
				elif tok.type == 'CLOSE_BRACE':
					self.subModuleCountBrace -= 1
				if self.subModuleCountBrace <= 0:
					self.brace_type_pop()
				continue
			# normal case:
			if (tok.type in ('PRECOMP_MACRO', 'PRECOMP_MACRO_CONT')):
				debug.debug("PRECOMP: " + str(tok))
				self.stack = []
				self.nameStack = []
				# Do nothing for macro ==> many time not needed ...
				continue
			if tok.type == 'OPEN_BRACE':
				# When we open a brace, this is the time to parse the stack ...
				# Clean the stack : (remove \t\r\n , and concatenate the 'xx', ':', ':', 'yy'  in 'xx::yy',
				self.nameStack = create_compleate_class_name(self.nameStack)
				if len(self.nameStack) <= 0:
					#open brace with no name ...
					self.brace_type_push('empty', [])
				elif is_a_function(self.nameStack):
					# need to parse sub function internal description...
					self.subModuleCountBrace = 1
					self.brace_type_push('function', self.nameStack)
				elif 'namespace' in self.nameStack:
					self.brace_type_push('namespace', self.nameStack)
				elif 'class' in self.nameStack:
					self.brace_type_push('class', self.nameStack)
				elif 'enum' in self.nameStack:
					self.brace_type_push('enum', self.nameStack)
				elif 'struct' in self.nameStack:
					self.brace_type_push('struct', self.nameStack)
				elif 'typedef' in self.nameStack:
					self.brace_type_push('typedef', self.nameStack)
				elif 'union' in self.nameStack:
					self.brace_type_push('union', self.nameStack)
				else:
					self.brace_type_push('unknow', self.nameStack)
				self.stack = []
				self.nameStack = []
			elif tok.type == 'CLOSE_BRACE':
				if len(self.nameStack) != 0:
					if self.previous_is('enum') == True:
						debug.info(self.gen_debug_space() + "enum list... : " + str(self.nameStack));
					else:
						debug.warning(self.gen_debug_space() + "end brace DROP : " + str(self.nameStack));
				self.stack = []
				self.nameStack = []
				self.brace_type_pop()
				self.nameStack = create_compleate_class_name(self.nameStack)
			if tok.type == 'OPEN_PAREN':
				self.nameStack.append(tok.value)
			elif tok.type == 'CLOSE_PAREN':
				self.nameStack.append(tok.value)
			elif tok.type == 'OPEN_SQUARE_BRACKET':
				self.nameStack.append(tok.value)
			elif tok.type == 'CLOSE_SQUARE_BRACKET':
				self.nameStack.append(tok.value)
			elif tok.type == 'TAB':
				pass
			elif tok.type == 'EQUALS':
				self.nameStack.append(tok.value)
			elif tok.type == 'COMMA':
				self.nameStack.append(tok.value)
			elif tok.type == 'BACKSLASH':
				self.nameStack.append(tok.value)
			elif tok.type == 'PIPE':
				self.nameStack.append(tok.value)
			elif tok.type == 'PERCENT':
				self.nameStack.append(tok.value)
			elif tok.type == 'CARET':
				self.nameStack.append(tok.value)
			elif tok.type == 'EXCLAMATION':
				self.nameStack.append(tok.value)
			elif tok.type == 'SQUOTE':
				pass
			elif tok.type == 'NUMBER':
				self.nameStack.append(tok.value)
			elif tok.type == 'MINUS':
				self.nameStack.append(tok.value)
			elif tok.type == 'PLUS':
				self.nameStack.append(tok.value)
			elif tok.type == 'STRING_LITERAL':
				self.nameStack.append(tok.value)
			elif     tok.type == 'NAME' \
			      or tok.type == 'AMPERSTAND' \
			      or tok.type == 'ASTERISK' \
			      or tok.type == 'CHAR_LITERAL':
				self.nameStack.append(tok.value)
			elif tok.type == 'COLON':
				if self.nameStack[0] in ['private', 'protected', 'public']:
					debug.debug(self.gen_debug_space() + "change visibility : " + self.nameStack[0]);
					self.brace_type_change_access(self.nameStack[0])
					self.nameStack = []
					self.stack = []
				else :
					self.nameStack.append(tok.value)
			elif tok.type == 'SEMI_COLON':
				if len(self.nameStack) != 0:
					self.nameStack = create_compleate_class_name(self.nameStack)
					if is_a_function(self.nameStack):
						debug.info(self.gen_debug_space() + "function : " + str(self.nameStack));
					elif 'namespace' in self.nameStack:
						debug.debug(self.gen_debug_space() + "find a namespace DECLARATION : " + str(self.nameStack));
					elif 'class' in self.nameStack:
						debug.debug(self.gen_debug_space() + "find a class     DECLARATION : " + str(self.nameStack));
					elif 'enum' in self.nameStack:
						debug.debug(self.gen_debug_space() + "find a enum      DECLARATION : " + str(self.nameStack));
					elif 'struct' in self.nameStack:
						debug.debug(self.gen_debug_space() + "find a struct    DECLARATION : " + str(self.nameStack));
					elif 'typedef' in self.nameStack:
						debug.info(self.gen_debug_space() + "find a typedef   DECLARATION : " + str(self.nameStack));
					elif 'union' in self.nameStack:
						debug.debug(self.gen_debug_space() + "find a union     DECLARATION : " + str(self.nameStack));
					else:
						if self.previous_is('enum') == True:
							debug.info(self.gen_debug_space() + "enum list : " + str(self.nameStack));
						else:
							# TODO : Check if it is true in all case : 
							self.brace_type_append('variable', self.nameStack);
							#debug.warning(self.gen_debug_space() + "semicolumn : " + str(self.nameStack));
				self.stack = []
				self.nameStack = []
	
	def create_element(self, type, stack):
		ret = None
		if type == 'empty':
			pass
		elif type == 'namespace':
			ret = Namespace.Namespace(stack, self.headerFileName, self.curLine)
		elif type == 'class':
			ret = Class.Class(stack, self.headerFileName, self.curLine)
		elif type == 'struct':
			ret = Struct.Struct(stack, self.headerFileName, self.curLine)
		elif type == 'typedef':
			#ret = Namespace.Namespace(stack, self.headerFileName, self.curLine)
			# TODO ...
			pass
		elif type == 'union':
			ret = Union.Union(stack, self.headerFileName, self.curLine)
		elif type == 'function':
			ret = Methode.Methode(stack, self.headerFileName, self.curLine)
		elif type == 'enum':
			ret = Enum.Enum(stack, self.headerFileName, self.curLine)
		elif type == 'variable':
			ret = Variable.Variable(stack, self.headerFileName, self.curLine)
		else:
			debug.error("unknow type ...")
		return ret
	
	def brace_type_push(self, type, stack):
		debug.info(self.gen_debug_space() + "find a <<" + type + ">> : " + str(stack));
		myClassElement = self.create_element(type, stack)
		element = { 'type' : type,
		            'stack' : stack,
		            'access' : None,
		            'node' : myClassElement
		          }
		if type == 'class':
			element['access'] = "private"
		elif type == 'struct':
			element['access'] = "public"
		self.braceDepthType.append(element)
		#debug.info ("append : " + str(element))
	
	def brace_type_append(self, type, stack):
		debug.info(self.gen_debug_space() + " append a <<" + type + ">> : " + str(stack));
		lastType = self.get_last_type()
		newType = self.create_element(type, stack)
		if newType == None:
			debug.info("TODO : Parse the special type")
			return
		if len(self.braceDepthType) == 0:
			debug.info("TODO : Append in glocal directly ...")
			return
		self.braceDepthType[len(self.braceDepthType)-1]['node'].append(newType)
	
	def brace_type_pop(self):
		self.braceDepthType.pop()
	
	def brace_type_change_access(self, newOne):
		if len(self.braceDepthType) == 0:
			debug.error("set access in nothing ... ")
			return
		if newOne not in supportedAccessSpecifier:
			debug.error("unknow access type : " + newOne)
			return
		if self.braceDepthType[len(self.braceDepthType)-1]['access'] == None:
			debug.error("Can not set access in other as : 'class' or 'struct' :" + str(self.braceDepthType[len(self.braceDepthType)-1]))
			return
		self.braceDepthType[len(self.braceDepthType)-1]['access'] = newOne
	
	def previous_is(self, type):
		if self.get_last_type() == type:
			return True
		return False
	
	def get_last_type(self):
		if len(self.braceDepthType) > 0:
			return self.braceDepthType[len(self.braceDepthType)-1]['type']
		return None

def is_a_function(stack) :
	# in a function we need to have functionName + ( + )
	if len(stack) < 3:
		return False
	#can end with 2 possibilities : ')', 'const' or ')'
	if    stack[len(stack)-1] == ')' \
	   or (     stack[len(stack)-2] == ')' \
	        and stack[len(stack)-1] == 'const'):
		return True
	return False