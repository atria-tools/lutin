#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re

listRegExp = [
	[ r'/\*\*(.*?)\*/', 'code-doxygen'],
	[ r'/\*(.*?)\*/', 'code-comment'],
	[ r'//!(.*?)\n', 'code-doxygen'],
	[ r'//(.*?)\n', 'code-comment'],
	[ r'#(.*?)\n', 'code-preproc'],
	[ r'"((\\"|.)*?)"', 'code-text-quote'],
	[ r"'(('|.)*?)'", 'code-text-quote'],
	[ r'(inline|const|class|virtual|private|public|protected|friend|const|extern|auto|register|static|volatile|typedef|struct|union|enum)',
	  'code-storage-keyword'],
	[ r'(bool|BOOL|char(16_t|32_t)?|double|float|u?int(8|16|32|64|128)?(_t)?|long|short|signed|size_t|unsigned|void|(I|U)(8|16|32|64|128))',
	  'code-type'],
	[ r'(((0(x|X)[0-9a-fA-F]*)|(\d+\.?\d*|\.\d+)((e|E)(\+|\-)?\d+)?)(L|l|UL|ul|u|U|F|f)?)',
	  'code-number'],
	[ r'(m_[A-Za-z_0-9])',
	  'code-member'],
	[ r'(( |\t)_[A-Za-z_0-9]*)',
	  'code-input-function'],
	[ r'(return|goto|if|else|case|default|switch|break|continue|while|do|for|sizeof)( |\t|\(|\{)',
	  'code-keyword'],
	[ r'((new|delete|try|catch|memset|fopen|fread|fwrite|fgets|fclose|printf|(f|s|diag_)printf|calloc|malloc|realloc|(cyg|sup)_([a-z]|[A-Z]|[0-9]|_)+)( |\t|\())',
	  'code-function-system'],
	[ r'((\w|_)+[ \t]*\()',
	  'code-function-name'],
	[ r'(NULL|MAX|MIN|__LINE__|__DATA__|__FILE__|__func__|__TIME__|__STDC__)',
	  'code-generic-define'],
	[ r'([A-Z_][A-Z_0-9]{3,500})',
	  'code-macro"'],
	[ r'(==|>=|<=|!=|>{1,2}|<{1,2}|&&|\{|\})',
	  'code-operator'],
	[ r'(true|TRUE|false|FALSE)',
	  '<code-operator'],
	[ r'((\w+::)+\w+)',
	  'code-class']
]

def transcode(value):
	inValue = value
	outValue = ""
	haveFindSomething = False;
	for reg1, color in listRegExp:
		result = re.search(reg1, inValue, re.DOTALL)
		while result != None:
			haveFindSomething = True
			# sub parse the start : 
			outValue += transcode(inValue[:result.start()])
			# transform local
			outValue += '<span class="' + color + '">'
			outValue += result.group()
			outValue += '</span>'
			
			# change the input value
			inValue = inValue[result.end():]
			# Search again ...
			result = re.search(reg1, inValue, re.DOTALL)
	outValue += inValue
	return outValue
