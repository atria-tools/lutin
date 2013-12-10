#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re
import BB_Title
import BB_Text
import BB_IndentAndDot
import BB_Link
import BB_Image
import BB_Table

import BB_comment
import BB_lineReturn
import BB_Code
import BB_Specification

##
## @brief Transcode input data in the corect format.
## @param[in] string String to transform.
## @return Transformed string.
##
def transcode(value):
	# remove html property
	value = re.sub(r'<', r'&lt;', value)
	value = re.sub(r'>', r'&gt;', value)
	value = BB_comment.transcode(value)
	value = BB_Title.transcode(value)
	value = BB_Text.transcode(value)
	value = BB_IndentAndDot.transcode(value)
	value = BB_Link.transcode(value)
	value = BB_Image.transcode(value)
	value = BB_Table.transcode(value)
	value = BB_Code.transcode(value)
	value = BB_Specification.transcode(value)
	value = BB_lineReturn.transcode(value)
	return value

##
## @brief transcode a BBcode file in a html file
## @return True if the file is transformed
##
def transcode_file(inputFileName, outputFileName):
	inData = lutinTools.FileReadData(inputFileName)
	if inData == "":
		return False
	outData = transcode(inData)
	debug.warning(" out: " + outputFileName)
	lutinTools.FileWriteData(outputFileName, outData)
	return True


