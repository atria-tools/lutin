#!/usr/bin/python
import debug

debugMode=0

def SetDebugMode(val):
	global debugMode
	if val==1:
		debugMode = 1
	else:
		debugMode = 0

def GetDebugMode():
	global debugMode
	return debugMode

CompileMode="gcc"

def SetCompileMode(val):
	global CompileMode
	if val=="clang":
		CompileMode = val
	if val=="gcc":
		CompileMode = val
	else:
		debug.error("not understand compiling tool mode : '" + val + "' can be [gcc/clang]")
		CompileMode = "gcc"

def GetClangMode():
	global CompileMode
	return CompileMode

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


