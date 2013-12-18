#!/usr/bin/python
import os
import sys
import re

import ply.lex as lex

import inspect
import lutinDebug as debug
import lutinTools
import Class

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


class TagStr(str):
	"""Wrapper for a string that allows us to store the line number associated with it"""
	lineno_reg = {}
	def __new__(cls,*args,**kw):
		new_obj =  str.__new__(cls,*args)
		if "lineno" in kw:
			TagStr.lineno_reg[id(new_obj)] = kw["lineno"]
		return new_obj
	
	def __del__(self):
		try:
			del TagStr.lineno_reg[id(self)]
		except: pass
	
	def lineno(self):
		return TagStr.lineno_reg.get(id(self), -1)


doxygenCommentCache = ""

#Track what was added in what order and at what depth
parseHistory = []

def is_namespace(nameStack):
	"""Determines if a namespace is being specified"""
	if len(nameStack) == 0:
		return False
	if nameStack[0] == "namespace":
		return True
	return False

def is_enum_namestack(nameStack):
	"""Determines if a namestack is an enum namestack"""
	if len(nameStack) == 0:
		return False
	if nameStack[0] == "enum":
		return True
	if     len(nameStack) > 1 \
	   and nameStack[0] == "typedef" \
	   and nameStack[1] == "enum":
		return True
	return False

def is_fundamental(s):
	for a in s.split():
		if a not in ["size_t", \
		             "struct", \
		             "union", \
		             "unsigned", \
		             "signed", \
		             "bool", \
		             "char", \
		             "short", \
		             "int", \
		             "float", \
		             "double", \
		             "long", \
		             "void", \
		             "*"]:
			return False
	return True

def is_function_pointer_stack(stack):
	"""Count how many non-nested paranthesis are in the stack.  Useful for determining if a stack is a function pointer"""
	paren_depth = 0
	paren_count = 0
	star_after_first_paren = False
	last_e = None
	for e in stack:
		if e == "(":
			paren_depth += 1
		elif     e == ")" \
		     and paren_depth > 0:
			paren_depth -= 1
			if paren_depth == 0:
				paren_count += 1
		elif     e == "*" \
		     and last_e == "(" \
		     and paren_count == 0 \
		     and paren_depth == 1:
			star_after_first_paren = True
		last_e = e
	if star_after_first_paren and paren_count == 2:
		return True
	else:
		return False

def is_method_namestack(stack):
	r = False
	if '(' not in stack:
		r = False
	elif stack[0] == 'typedef':
		r = False	# TODO deal with typedef function prototypes
	#elif '=' in stack and stack.index('=') < stack.index('(') and stack[stack.index('=')-1] != 'operator': r = False	#disabled July6th - allow all operators
	elif 'operator' in stack:
		r = True	# allow all operators
	elif     '{' in stack \
	     and stack.index('{') < stack.index('('):
		r = False	# struct that looks like a method/class
	elif     '(' in stack \
	     and ')' in stack:
		if     '{' in stack \
		   and '}' in stack:
			r = True
		elif stack[-1] == ';':
			if is_function_pointer_stack(stack):
				r = False
			else:
				r = True
		elif '{' in stack:
			r = True	# ideally we catch both braces... TODO
	else:
		r = False
	#Test for case of property set to something with parens such as "static const int CONST_A = (1 << 7) - 1;"
	if     r \
	   and "(" in stack \
	   and "=" in stack \
	   and 'operator' not in stack:
		if stack.index("=") < stack.index("("): r = False
	return r

def is_property_namestack(nameStack):
	r = False
	if     '(' not in nameStack \
	   and ')' not in nameStack:
		r = True
	elif     "(" in nameStack \
	     and "=" in nameStack \
	     and nameStack.index("=") < nameStack.index("("):
		r = True
	#See if we are a function pointer
	if     not r \
	   and is_function_pointer_stack(nameStack):
		r = True
	return r

def detect_lineno(s):
	"""Detect the line number for a given token string"""
	try:
		rtn = s.lineno()
		if rtn != -1:
			return rtn
	except: pass
	global curLine
	return curLine

def filter_out_attribute_keyword(stack):
	"""Strips __attribute__ and its parenthetical expression from the stack"""
	if "__attribute__" not in stack:
		return stack
	try:
		debug.debug("Stripping __attribute__ from %s"% stack)
		attr_index = stack.index("__attribute__")
		attr_end = attr_index + 1 #Assuming not followed by parenthetical expression which wont happen
		#Find final paren
		if stack[attr_index + 1] == '(':
			paren_count = 1
			for i in xrange(attr_index + 2, len(stack)):
				elm = stack[i]
				if elm == '(':
					paren_count += 1
				elif elm == ')':
					paren_count -= 1
					if paren_count == 0:
						attr_end = i + 1
						break
		new_stack = stack[0:attr_index] + stack[attr_end:]
		debug.debug("stripped stack is %s"% new_stack)
		return new_stack
	except:
		return stack



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
	compleateLine = ""
	compleateLine = compleateLine.join(table);
	if "::" not in compleateLine:
		return table
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
	return out

class parse_file():
	
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
		lex.lex()
		lex.input(headerFileStr)
		global curLine
		global curChar
		curLine = 0
		curChar = 0
		while True:
			tok = lex.token()
			if not tok:
				break
			tok.value = TagStr(tok.value, lineno=tok.lineno)
			debug.debug("TOK: " + str(tok))
			self.stack.append( tok.value )
			curLine = tok.lineno
			curChar = tok.lexpos
			if (tok.type in ('PRECOMP_MACRO', 'PRECOMP_MACRO_CONT')):
				debug.debug("PRECOMP: " + str(tok))
				self.stack = []
				self.nameStack = []
				# Do nothing for macro ==> many time not needed ...
				continue
			if (tok.type == 'OPEN_BRACE'):
				# When we open a brace, this is the time to parse the stack ...
				# Clean the stack : (remove \t\r\n , and concatenate the 'xx', ':', ':', 'yy'  in 'xx::yy',
				self.nameStack = create_compleate_class_name(self.nameStack)
				if len(self.nameStack) <= 0:
					#open brace with no name ...
					debug.warning("[" + str(self.braceDepth) + "] find an empty stack ...")
				elif 'namespace' in self.nameStack:
					debug.info("[" + str(self.braceDepth) + "] find a namespace : " + str(self.nameStack));
				elif 'class' in self.nameStack:
					debug.info("[" + str(self.braceDepth) + "] find a class     : " + str(self.nameStack));
				elif 'enum' in self.nameStack:
					debug.info("[" + str(self.braceDepth) + "] find a enum      : " + str(self.nameStack));
				elif 'struct' in self.nameStack:
					debug.info("[" + str(self.braceDepth) + "] find a struct    : " + str(self.nameStack));
				elif 'typedef' in self.nameStack:
					debug.info("[" + str(self.braceDepth) + "] find a typedef   : " + str(self.nameStack));
				elif 'union' in self.nameStack:
					debug.info("[" + str(self.braceDepth) + "] find a union     : " + str(self.nameStack));
				else:
					debug.warning("[" + str(self.braceDepth) + "] find an unknow stack : " + str(self.nameStack))
				self.stack = []
				self.nameStack = []
				self.braceDepth += 1
			elif tok.type == 'CLOSE_BRACE':
				self.braceDepth -= 1
				debug.info("[" + str(self.braceDepth) + "] close brace");
				if     len(self.m_elementParseStack) != 0 \
				   and self.m_elementParseStack[len(self.m_elementParseStack)-1]['level'] == self.braceDepth :
					self.m_elementParseStack.pop()
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
					debug.info("[" + str(self.braceDepth) + "]     change visibility : " + self.nameStack[0]);
					self.nameStack = []
					self.stack = []
				else :
					self.nameStack.append(tok.value)
			elif tok.type == 'SEMI_COLON':
				if len(self.nameStack) != 0:
					debug.info("[" + str(self.braceDepth) + "]     semicolumn : " + str(self.nameStack));
				self.stack = []
				self.nameStack = []
