#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
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
	               r'<pre>\4</pre>',
	               value,
	               flags=re.DOTALL)
	
	# TODO : remove the basic indentation of the element (to have a better display in the text tutorial ...
	return value


