#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re


##
## @brief Transcode .
##      =?=Page Title=?=
##      ==Title 1==
##      ===Title 2===
##      ====Title 3====
##      =====Title 4=====
##      ======Title 5======
## @param[in] value String to transform.
## @return Transformed string.
##
def transcode(value):
	
	value = re.sub(r'=\?=(.*?)=\?=',
	               r'<h1><center>\1</center></h1>',
	               value)
	
	value = re.sub(r'\n======(.*?)======',
	               r'\n<h5>\1</h5>',
	               value)
	
	value = re.sub(r'\n=====(.*?)=====',
	               r'\n<h4>\1</h4>',
	               value)
	
	value = re.sub(r'\n====(.*?)====',
	               r'\n<h3>\1</h3>',
	               value)
	
	value = re.sub(r'\n===(.*?)===',
	               r'\n<h2>\1</h2>',
	               value)
	
	value = re.sub(r'\n==(.*?)==',
	               r'\n<h1>\1</h1>',
	               '\n' + value)
	
	value = value[1:]
	
	return value


