#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re


##
## @brief Transcode balise:
##     /* ... */
## @param[in] value String to transform.
## @return Transformed string.
##
def transcode(value):
	
	value = re.sub(r'\/\*(.*?)\*\/',
	               r'',
	               value,
	               flags=re.DOTALL)
	"""
	value = re.sub(r'\/\/(.*?)\n',
	               r'',
	               value)
	"""
	return value


