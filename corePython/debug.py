#!/usr/bin/python

debugLevel=3
debugColor=False

def SetLevel(id):
	global debugLevel
	debugLevel = id
	#print "SetDebug level at " + str(debugLevel)

def EnableColor():
	global debugColor
	debugColor = True

def verbose(input):
	if debugLevel >= 5:
		print input

def debug(input):
	if debugLevel >= 4:
		print input

def info(input):
	if debugLevel >= 3:
		print input

def warning(input):
	if debugLevel >= 2:
		print "WARNING : " + input

def error(input):
	if debugLevel >= 1:
		print "ERROR : " + input
	raise "error happend"


