#!/usr/bin/python
import lutinDebug as debug
import lutinModule as module
import lutinTargetLinux
import lutinHost

availlable=[]

def AddModule(name, type):
	global availlable
	if type=="BINARY":
		availlable.append([name,"Module", "bin"])
	else:
		availlable.append([name,"Module", "other"])

def AddPackage(name):
	global availlable
	availlable.append([name,"Package", "pkg"])



currentTarget=None

def SetTarget(name):
	global currentTarget
	if name=="Linux":
		currentTarget = lutinTargetLinux.Target()
	elif name=="Windows":
		debug.error("TODO : create target type :'" + name + "'")
	elif name=="MacOs":
		debug.error("TODO : create target type :'" + name + "'")
	elif name=="Android":
		debug.error("TODO : create target type :'" + name + "'")
	else:
		debug.error("Unknow target type :'" + name + "'")


def GetCurrentTarget():
	global currentTarget
	if currentTarget==None:
		SetTarget(lutinHost.OS)
		
	return currentTarget

