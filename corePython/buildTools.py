#!/usr/bin/python
import os
import shutil
import errno
import debug
import fnmatch


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


def RemoveFolderAndSubFolder(path):
	if os.path.isdir(path):
		debug.verbose("remove folder : '" + path + "'")
		shutil.rmtree(path)



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
	if type(list) == type(None):
		return ""
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

def CopyFile(src, dst):
	if os.path.exists(dst):
		if os.path.getmtime(dst) > os.path.getmtime(src):
			return
	debug.printElement("copy file", src, "==>", dst)
	CreateDirectoryOfFile(dst)
	shutil.copyfile(src, dst)


def CopyAnything(src, dst):
	tmpPath = os.path.dirname(os.path.realpath(src))
	tmpRule = os.path.basename(src)
	for root, dirnames, filenames in os.walk(tmpPath):
		tmpList = filenames
		if len(tmpRule)>0:
			tmpList = fnmatch.filter(filenames, tmpRule)
		# Import the module :
		for cycleFile in tmpList:
			#for cycleFile in filenames:
			#debug.info("Might copy : '" + tmpPath+cycleFile + "' ==> '" + dst + "'")
			CopyFile(tmpPath+"/"+cycleFile,dst+"/"+cycleFile)
