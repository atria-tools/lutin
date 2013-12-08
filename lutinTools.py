#!/usr/bin/python
import os
import shutil
import errno
import lutinDebug as debug
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

def RemoveFile(path):
	if os.path.isfile(path):
		os.remove(path)

def FileSize(path):
	if not os.path.isfile(path):
		return 0
	statinfo = os.stat(path)
	return statinfo.st_size

def FileReadData(path):
	if not os.path.isfile(path):
		return ""
	file = open(path, "r")
	data_file = file.read()
	file.close()
	return data_file

def FileWriteData(path, data):
	file = open(path, "w")
	file.write(data)
	file.close()

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

def CopyFile(src, dst, force=False):
	if os.path.exists(src)==False:
		debug.error("Request a copy a file that does not existed : '" + src + "'")
	if os.path.exists(dst):
		if     force==False \
		   and os.path.getmtime(dst) > os.path.getmtime(src):
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


def CopyAnythingTarget(target, src, dst):
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
			target.AddFileStaging(tmpPath+"/"+cycleFile,dst+"/"+cycleFile)
