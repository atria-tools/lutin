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


printPrettyMode=False

def SetPrintPrettyMode(val):
	global printPrettyMode
	if val==True:
		printPrettyMode = True
	else:
		printPrettyMode = False

def GetPrintPrettyMode():
	global printPrettyMode
	return printPrettyMode

def PrintPretty(myString):
	global printPrettyMode
	if True==printPrettyMode:
		if myString[len(myString)-1]==' ' : 
			tmpcmdLine = myString[:len(myString)-1]
		else :
			tmpcmdLine = myString
		tmpcmdLine = tmpcmdLine.replace(' ', '\n\t')
		tmpcmdLine = tmpcmdLine.replace('\n\t\n\t', '\n\t')
		tmpcmdLine = tmpcmdLine.replace('\n\t\n\t', '\n\t')
		tmpcmdLine = tmpcmdLine.replace('\n\t\n\t', '\n\t')
		tmpcmdLine = tmpcmdLine.replace('-o\n\t', '-o ')
		tmpcmdLine = tmpcmdLine.replace('-D\n\t', '-D ')
		tmpcmdLine = tmpcmdLine.replace('-I\n\t', '-I ')
		tmpcmdLine = tmpcmdLine.replace('-L\n\t', '-L ')
		tmpcmdLine = tmpcmdLine.replace('g++\n\t', 'g++\t')
		tmpcmdLine = tmpcmdLine.replace('gcc\n\t', 'gcc\t')
		tmpcmdLine = tmpcmdLine.replace('ar\n\t', 'ar\t')
		tmpcmdLine = tmpcmdLine.replace('ranlib\n\t', 'ranlib\t')
		tmpcmdLine = tmpcmdLine.replace('\n\t', ' \\\n\t')
		
		return tmpcmdLine
	else:
		return myString
