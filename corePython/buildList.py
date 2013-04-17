#!/usr/bin/python
import debug
import module

availlable=[]

def AddModule(name):
	global availlable
	availlable.append([name,"Module"])

def AddPackage(name):
	global availlable
	availlable.append([name,"Package"])

def Build(name):
	if name == "all":
		debug.info("Build all")
		for elem in availlable:
			if elem[1] == "Module":
				module.Build(elem[0])
			else:
				debug.error("TODO ... Build package '" + elem[0] + "'")
	elif name == "clean":
		debug.info("Clean all")
		for elem in availlable:
			if elem[1] == "Module":
				module.Clean(elem[0])
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
						module.Clean(cleanName)
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
						module.Build(name)
					else:
						debug.info("Build package '" + name + "'")
						debug.error("TODO ... Build package '" + cleanName + "'")
					# todo : build
					return
			debug.error("not know module name : '" + name + "' to build it")



