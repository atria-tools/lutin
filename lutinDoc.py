#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
# TODO : Add try of generic input ...
sys.path.append(lutinTools.GetCurrentPath(__file__) + "/ply/ply/")
sys.path.append(lutinTools.GetCurrentPath(__file__) + "/cppParser/CppheaderParser/")
import lutinDocHtml
import lutinDocMd




def GenerateDocFile(filename, outFolder, isHtml=True) :
	if isHtml == True:
		lutinDocHtml.GenerateDocFile(filename, outFolder)
	else:
		lutinDocDot.GenerateDocFile(filename, outFolder)