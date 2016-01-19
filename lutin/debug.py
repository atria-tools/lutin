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

debug_level=3
debug_color=False

color_default= ""
color_red    = ""
color_green  = ""
color_yellow = ""
color_blue   = ""
color_purple = ""
color_cyan   = ""


debug_lock = threading.Lock()

def set_level(id):
	global debug_level
	debug_level = id
	#print "SetDebug level at " + str(debug_level)

def get_level():
	global debug_level
	return debug_level

def enable_color():
	global debug_color
	debug_color = True
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

def disable_color():
	global debug_color
	debug_color = True
	global color_default
	color_default= ""
	global color_red
	color_red    = ""
	global color_green
	color_green  = ""
	global color_yellow
	color_yellow = ""
	global color_blue
	color_blue   = ""
	global color_purple
	color_purple = ""
	global color_cyan
	color_cyan   = ""

def extreme_verbose(input, force=False):
	global debug_lock
	global debug_level
	if    debug_level >= 6 \
	   or force == True:
		debug_lock.acquire()
		print(color_blue + input + color_default)
		debug_lock.release()

def verbose(input, force=False):
	global debug_lock
	global debug_level
	if    debug_level >= 5 \
	   or force == True:
		debug_lock.acquire()
		print(color_blue + input + color_default)
		debug_lock.release()

def debug(input, force=False):
	global debug_lock
	global debug_level
	if    debug_level >= 4 \
	   or force == True:
		debug_lock.acquire()
		print(color_green + input + color_default)
		debug_lock.release()

def info(input, force=False):
	global debug_lock
	global debug_level
	if    debug_level >= 3 \
	   or force == True:
		debug_lock.acquire()
		print(input + color_default)
		debug_lock.release()

def warning(input, force=False):
	global debug_lock
	global debug_level
	if    debug_level >= 2 \
	   or force == True:
		debug_lock.acquire()
		print(color_purple + "[WARNING] " + input + color_default)
		debug_lock.release()

def todo(input, force=False):
	global debug_lock
	global debug_level
	if    debug_level >= 3 \
	   or force == True:
		debug_lock.acquire()
		print(color_purple + "[TODO] " + input + color_default)
		debug_lock.release()

def error(input, thread_id=-1, force=False, crash=True):
	global debug_lock
	global debug_level
	if    debug_level >= 1 \
	   or force == True:
		debug_lock.acquire()
		print(color_red + "[ERROR] " + input + color_default)
		debug_lock.release()
	if crash == True:
		from . import multiprocess
		multiprocess.set_error_occured()
		if thread_id != -1:
			threading.interrupt_main()
		exit(-1)
		#os_exit(-1)
		#raise "error happend"

def print_element(type, lib, dir, name, force=False):
	global debug_lock
	global debug_level
	if    debug_level >= 3 \
	   or force == True:
		debug_lock.acquire()
		print(color_cyan + type + color_default + " : " + color_yellow + lib + color_default + " " + dir + " " + color_blue + name + color_default)
		debug_lock.release()

def print_compilator(myString):
	global debug_color
	global debug_lock
	if debug_color == True:
		myString = myString.replace('\\n', '\n')
		myString = myString.replace('\\t', '\t')
		myString = myString.replace('error:', color_red+'error:'+color_default)
		myString = myString.replace('warning:', color_purple+'warning:'+color_default)
		myString = myString.replace('note:', color_green+'note:'+color_default)
		myString = re.sub(r'([/\w_-]+\.\w+):', r'-COLORIN-\1-COLOROUT-:', myString)
		myString = myString.replace('-COLORIN-', color_yellow)
		myString = myString.replace('-COLOROUT-', color_default)
	
	debug_lock.acquire()
	print(myString)
	debug_lock.release()

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
