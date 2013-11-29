#!/usr/bin/python
import lutinDebug as debug
import sys
import CppHeaderParser
import lutinTools

def writeExpendSize(data, size) :
	ret = data
	for iii in range(len(ret), size):
		ret += " "
	return ret

def displayReductFunction(className, function, file, classement, sizeReturn, sizefunction) :
	lineData = "\t" + classement + " "
	
	if function['destructor'] :
		lineData += writeExpendSize("", sizeReturn+1)
	elif function['constructor'] :
		lineData += writeExpendSize("", sizeReturn)
		lineData += "~"
	else :
		lineData += writeExpendSize(function["rtnType"], sizeReturn+1)
	
	lineData += writeExpendSize(function["name"], sizefunction+1)
	lineData += "("
	file.write(lineData);
	parameterPos = len(lineData);
	isFirst = True
	for param in function["parameters"]:
		if isFirst == False:
			file.write(",\n")
			file.write(writeExpendSize("",parameterPos))
		file.write(param['type'])
		if param['name'] != "":
			file.write(" ")
			file.write(param['name'])
		isFirst = False
	file.write(");")
	file.write("\n")

def calsulateSizeFunction(function, size) :
	if len(function["name"]) > size:
		return len(function["name"])+1
	return size

def calsulateSizeReturn(function, size) :
	if len(function["rtnType"]) > size:
		return len(function["rtnType"])+1
	return size

def GenerateDocFile(filename, outFolder) :
	try:
		metaData = CppHeaderParser.CppHeader(filename)
	except CppHeaderParser.CppParseError,  e:
		debug.error(" can not parse the file: '" + filename + "' error : " + e)
		return False
	
	lutinTools.CreateDirectoryOfFile(outFolder+"/");
	
	for element in metaData.classes:
		classFileName = outFolder + "/";
		localClass = metaData.classes[element]
		if localClass['namespace'] == "":
			className = localClass['name']
		else:
			className = localClass['namespace'] + "::" + localClass['name']
		debug.debug("    class: " + className)
		classFileName += className
		# Replace all :: with __
		classFileName = classFileName.replace(":", "_")
		classFileName = classFileName.replace(" ", "")
		classFileName += ".md"
		file = open(classFileName, "w")
		
		file.write(className + "\n")
		for iii in range(0,len(className)):
			file.write("=");
		file.write("\n")
		file.write("\n")
		# calculate function max size return & function name size:
		sizeReturn=0
		sizefunction=0
		for function in localClass["methods"]["public"]:
			sizefunction = calsulateSizeFunction(function, sizefunction)
			sizeReturn = calsulateSizeReturn(function, sizeReturn)
		for function in localClass["methods"]["protected"]:
			sizefunction = calsulateSizeFunction(function, sizefunction)
			sizeReturn = calsulateSizeReturn(function, sizeReturn)
		for function in localClass["methods"]["private"]:
			sizefunction = calsulateSizeFunction(function, sizefunction)
			sizeReturn = calsulateSizeReturn(function, sizeReturn)
		
		file.write("Synopsis:\n")
		file.write("---------\n")
		file.write("\n")
		# display all functions :
		# TODO: ...
		for function in localClass["methods"]["public"]:
			displayReductFunction(localClass['name'], function, file, "public:   ", sizeReturn, sizefunction)
		for function in localClass["methods"]["protected"]:
			displayReductFunction(localClass['name'], function, file, "protected:", sizeReturn, sizefunction)
		for function in localClass["methods"]["private"]:
			displayReductFunction(localClass['name'], function, file, "private:  ", sizeReturn, sizefunction)
		
		file.write("\n")
		file.write("\n")
		
		file.write("Signals:\n")
		file.write("--------\n")
		file.write("\n")
		# display all signals :
		# TODO: ...
		
		file.write("Configuration:\n")
		file.write("--------------\n")
		file.write("\n")
		# display all configuration :
		# TODO: ...
		
		file.write("Description:\n")
		file.write("------------\n")
		file.write("\n")
		# display Class description :
		# TODO: ...
		
		
		file.write("Detail:\n")
		file.write("-------\n")
		file.write("\n")
		# display all the class internal functions :
		# TODO: ...
		
		
		
		if len(localClass['inherits']) != 0:
			for heritedClass in localClass['inherits']:
				debug.debug("        heritage : " + str(heritedClass['class']))
				
		
		file.close()


"""

"""

