#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import codeHL
import re


##
## @brief Transcode balise :
##   [code language=cpp]
##   int main(void) {
##   	return 0;
##   }
##   [/code]
## @param[in] value String to transform.
## @return Transformed string.
##
def transcode(value):
	#value = re.sub(r'\[code(( |\t|\n|\r)+style=(.*))?\](.*?)\[/code\]',
	value = re.sub(r'\[code(( |\t|\n|\r)+style=(.*?))?\](.*?)\[/code\]',
	               replace_code, #r'<pre>\4</pre>',
	               value,
	               flags=re.DOTALL)
	
	# TODO : remove the basic indentation of the element (to have a better display in the text tutorial ...
	return value



def replace_code(match):
	if match.group() == "":
		return ""
	#debug.info("plop: " + str(match.groups()))
	value = codeHL.transcode(match.groups()[2], match.groups()[3])
	return '<pre>' + value + '</pre>'

