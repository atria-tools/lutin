#!/usr/bin/python
import debug
import module
import target_Linux
import host

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

def Build(name):
	if name == "all":
		debug.info("Build all")
		for elem in availlable:
			if elem[1] == "Module":
				if elem[2] == "bin":
					module.Build(elem[0], GetCurrentTarget())
			else:
				debug.error("TODO ... Build package '" + elem[0] + "'")
	elif name == "clean":
		debug.info("Clean all")
		for elem in availlable:
			if elem[1] == "Module":
				module.Clean(elem[0], GetCurrentTarget())
			else:
				debug.error("TODO ... Clean package '" + elem[0] + "'")
	else:
		myLen = len(name)
		if name[myLen-6:] == "-clean":
			cleanName = name[:myLen-6]
			# clean requested
			for elem in availlable:
				if elem[0] == cleanName:
					if elem[1] == "Module":
						debug.info("Clean module '" + cleanName + "'")
						module.Clean(cleanName, GetCurrentTarget())
					else:
						debug.info("Clean package '" + cleanName + "'")
						debug.error("TODO ... Clean package '" + cleanName + "'")
					# todo : clean
					return
			debug.error("not know module name : '" + cleanName + "' to clean it")
		else:
			# Build requested
			for elem in availlable:
				if elem[0] == name:
					if elem[1] == "Module":
						debug.info("Build module '" + name + "'")
						module.Build(name, GetCurrentTarget())
					else:
						debug.info("Build package '" + name + "'")
						debug.error("TODO ... Build package '" + cleanName + "'")
					# todo : build
					return
			debug.error("not know module name : '" + name + "' to build it")


currentTarget=None

def SetTarget(name):
	global currentTarget
	if name=="Linux":
		currentTarget = target_Linux.Target()
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
		SetTarget(host.OS)
		
	return currentTarget

