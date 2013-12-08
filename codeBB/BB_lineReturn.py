#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re


##
## @brief Transcode balise:
##     \n\n ==> <br/>
## @param[in] value String to transform.
## @return Transformed string.
##
def transcode(value):
	
	value = re.sub(r'\r\n',
	               r'\n',
	               value)
	
	value = re.sub(r'\n\n\n',
	               r'<br/><br/>',
	               value)
	
	value = re.sub(r'\n\n',
	               r'<br/>',
	               value)
	
	value = re.sub(r'<br/>',
	               r'<br/>\n',
	               value)
	
	return value


