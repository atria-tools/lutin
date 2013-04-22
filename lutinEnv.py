#!/usr/bin/python
import lutinDebug as debug

forceMode=False

def SetForceMode(val):
	global forceMode
	if val==1:
		forceMode = 1
	else:
		forceMode = 0

def GetForceMode():
	global forceMode
	return forceMode


