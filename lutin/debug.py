#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import os
import threading
import re

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

def set_level(id):
	global debugLevel
	debugLevel = id
	#print "SetDebug level at " + str(debugLevel)

def get_level():
	global debugLevel
	return debugLevel

def enable_color():
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
	color_blue   = "\033[01;34m"
	global color_purple
	color_purple = "\033[35m"
	global color_cyan
	color_cyan   = "\033[36m"

def extreme_verbose(input, force=False):
	global debugLock
	global debugLevel
	if    debugLevel >= 6 \
	   or force == True:
		debugLock.acquire()
		print(color_blue + input + color_default)
		debugLock.release()

def verbose(input, force=False):
	global debugLock
	global debugLevel
	if    debugLevel >= 5 \
	   or force == True:
		debugLock.acquire()
		print(color_blue + input + color_default)
		debugLock.release()

def debug(input, force=False):
	global debugLock
	global debugLevel
	if    debugLevel >= 4 \
	   or force == True:
		debugLock.acquire()
		print(color_green + input + color_default)
		debugLock.release()

def info(input, force=False):
	global debugLock
	global debugLevel
	if    debugLevel >= 3 \
	   or force == True:
		debugLock.acquire()
		print(input + color_default)
		debugLock.release()

def warning(input, force=False):
	global debugLock
	global debugLevel
	if    debugLevel >= 2 \
	   or force == True:
		debugLock.acquire()
		print(color_purple + "[WARNING] " + input + color_default)
		debugLock.release()

def todo(input, force=False):
	global debugLock
	global debugLevel
	if    debugLevel >= 3 \
	   or force == True:
		debugLock.acquire()
		print(color_purple + "[TODO] " + input + color_default)
		debugLock.release()

def error(input, threadID=-1, force=False, crash=True):
	global debugLock
	global debugLevel
	if    debugLevel >= 1 \
	   or force == True:
		debugLock.acquire()
		print(color_red + "[ERROR] " + input + color_default)
		debugLock.release()
	if crash==True:
		from . import multiprocess
		multiprocess.error_occured()
		if threadID != -1:
			threading.interrupt_main()
		exit(-1)
		#os_exit(-1)
		#raise "error happend"

def print_element(type, lib, dir, name, force=False):
	global debugLock
	global debugLevel
	if    debugLevel >= 3 \
	   or force == True:
		debugLock.acquire()
		print(color_cyan + type + color_default + " : " + color_yellow + lib + color_default + " " + dir + " " + color_blue + name + color_default)
		debugLock.release()

def print_compilator(myString):
	global debugColor
	global debugLock
	if debugColor == True:
		myString = myString.replace('\\n', '\n')
		myString = myString.replace('\\t', '\t')
		myString = myString.replace('error:', color_red+'error:'+color_default)
		myString = myString.replace('warning:', color_purple+'warning:'+color_default)
		myString = myString.replace('note:', color_green+'note:'+color_default)
		myString = re.sub(r'([/\w_-]+\.\w+):', r'-COLORIN-\1-COLOROUT-:', myString)
		myString = myString.replace('-COLORIN-', color_yellow)
		myString = myString.replace('-COLOROUT-', color_default)
	
	debugLock.acquire()
	print(myString)
	debugLock.release()

def get_color_set() :
	global color_default
	global color_red
	global color_green
	global color_yellow
	global color_blue
	global color_purple
	global color_cyan
	return {
	    "default": color_default,
	    "red": color_red,
	    "green": color_green,
	    "yellow": color_yellow,
	    "blue": color_blue,
	    "purple": color_purple,
	    "cyan": color_cyan,
	    }
