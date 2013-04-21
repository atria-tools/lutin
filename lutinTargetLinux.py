#!/usr/bin/python
import lutinDebug as debug
import datetime
import lutinTools
import lutinEnv as environement
import lutinTarget

class TargetLinux(lutinTarget.Target):
	def __init__(self, typeCompilator, debugMode):
		lutinTarget.Target.__init__(self, "Linux", typeCompilator, debugMode)
	
	
