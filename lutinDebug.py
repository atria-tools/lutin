#!/usr/bin/python
import os
import thread
import lutinMultiprocess
import threading

debugLevel=3
debugColor=False

color_default= ""
color_red    = ""
color_green  = ""
color_yellow = ""
color_blue   = ""
color_purple = ""
color_cyan   = ""


debugLock = threading.Lock()

def SetLevel(id):
	global debugLevel
	debugLevel = id
	#print "SetDebug level at " + str(debugLevel)

def EnableColor():
	global debugColor
	debugColor = True
	global color_default
	color_default= "\033[00m"
	global color_red
	color_red    = "\033[31m"
	global color_green
	color_green  = "\033[32m"
	global color_yellow
	color_yellow = "\033[33m"
	global color_blue
	color_blue   = "\033[34m"
	global color_purple
	color_purple = "\033[35m"
	global color_cyan
	color_cyan   = "\033[36m"

def verbose(input):
	global debugLock
	global debugLevel
	if debugLevel >= 5:
		debugLock.acquire()
		print(color_blue + input + color_default)
		debugLock.release()

def debug(input):
	global debugLock
	global debugLevel
	if debugLevel >= 4:
		debugLock.acquire()
		print(color_green + input + color_default)
		debugLock.release()

def info(input):
	global debugLock
	global debugLevel
	if debugLevel >= 3:
		debugLock.acquire()
		print(input + color_default)
		debugLock.release()

def warning(input):
	global debugLock
	global debugLevel
	if debugLevel >= 2:
		debugLock.acquire()
		print(color_purple + "[WARNING] " + input + color_default)
		debugLock.release()

def error(input, threadID=-1):
	global debugLock
	global debugLevel
	if debugLevel >= 1:
		debugLock.acquire()
		print(color_red + "[ERROR] " + input + color_default)
		debugLock.release()
	lutinMultiprocess.ErrorOccured()
	if threadID != -1:
		thread.interrupt_main()
	exit(-1)
	#os_exit(-1)
	#raise "error happend"

def printElement(type, lib, dir, name):
	global debugLock
	global debugLevel
	if debugLevel >= 3:
		debugLock.acquire()
		print(color_cyan + type + color_default + " : " + color_yellow + lib + color_default + " " + dir + " " + color_blue + name + color_default)
		debugLock.release()


