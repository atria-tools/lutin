#!/usr/bin/python
import os

"""
	
"""
def GetRunFolder():
	return os.getcwd()

"""
	
"""
def GetCurrentPath(file):
	return os.path.dirname(os.path.realpath(file))

def CreateDirectoryOfFile(file):
	folder = os.path.dirname(file)
	try:
		os.stat(folder)
	except:
		os.makedirs(folder)


def ListToStr(list):
	if type(list) == type(str()):
		return list + " "
	else:
		result = ""
		# mulyiple imput in the list ...
		for elem in list:
			result += ListToStr(elem)
		return result

def AddPrefix(prefix,list):
	if type(list) == type(str()):
		return prefix+list
	else:
		if len(list)==0:
			return ''
		else:
			result=[]
			for elem in list:
				result.append(prefix+elem)
			return result
