#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import codeHLcpp
import codeHLBBcode
import codeHLJava
import codeHLjson
import codeHLPython
import codeHLXML
import codeHLshell


def transcode(type, value):
	if type == "c++":
		value = codeHLcpp.transcode(value)
	elif type == "java":
		value = codeHLJava.transcode(value)
	elif type == "bbcode":
		value = codeHLBBcode.transcode(value)
	elif type == "python":
		value = codeHLPython.transcode(value)
	elif type == "json":
		value = codeHLjson.transcode(value)
	elif type == "xml":
		value = codeHLXML.transcode(value)
	elif type == "shell":
		value = codeHLshell.transcode(value)
	
	return value

