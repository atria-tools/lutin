#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
# TODO : Add try of generic input ...
sys.path.append(lutinTools.GetCurrentPath(__file__) + "/ply/ply/")
sys.path.append(lutinTools.GetCurrentPath(__file__) + "/cppParser/CppheaderParser/")
import CppHeaderParser

def writeExpendSize(data, size) :
	ret = data
	for iii in range(len(ret), size):
		ret += " "
	return ret

def displayReductFunction(function, file, classement, sizeReturn, sizefunction) :
	lineData = classement + " "
	
	if function['destructor'] :
		lineData += writeExpendSize("", sizeReturn)
		lineData += "~"
	elif function['constructor'] :
		lineData += writeExpendSize("", sizeReturn+1)
	else :
		lineData += writeExpendSize(function["rtnType"], sizeReturn+1)
	
	lineData += writeExpendSize(function["name"], sizefunction+1)
	lineData += "("
	file.write("\t" + lineData);
	parameterPos = len(lineData);
	isFirst = True
	for param in function["parameters"]:
		if isFirst == False:
			file.write(",\n\t")
			file.write(writeExpendSize("",parameterPos))
		file.write(param['type'])
		if param['name'] != "":
			file.write(" ")
			file.write(param['name'])
		isFirst = False
	file.write(");")
	file.write("\n")


def displayFunction(namespace, function, file, classement, sizeReturn, sizefunction) :
	lineData = ""
	if namespace != "":
		lineData = namespace + "::"
	if function['destructor'] :
		lineData += "~"
	lineData += function["name"] + "( ... )"
	file.write(lineData + "\n")
	for iii in range(0, len(lineData)):
		file.write(".")
	file.write("\n\n")

	if function['destructor'] :
		lineData = "~"
	elif function['constructor'] :
		lineData = ""
	else :
		lineData = function["rtnType"] + " "

	lineData += function["name"]
	lineData += "("
	file.write("\t" + lineData);
	parameterPos = len(lineData);
	isFirst = True
	for param in function["parameters"]:
		if isFirst == False:
			file.write(",\n\t")
			file.write(writeExpendSize("",parameterPos))
		file.write(param['type'])
		if param['name'] != "":
			file.write(" ")
			file.write(param['name'])
		isFirst = False
	file.write(");")
	file.write("\n\n")
	if "doxygen" in function:
		# TODO : parse doxygen ...
		file.write(function["doxygen"])
		file.write("\n")
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
		classFileName = outFolder + "/"
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
			displayReductFunction(function, file, "public:   ", sizeReturn, sizefunction)
		for function in localClass["methods"]["protected"]:
			displayReductFunction(function, file, "protected:", sizeReturn, sizefunction)
		for function in localClass["methods"]["private"]:
			displayReductFunction(function, file, "private:  ", sizeReturn, sizefunction)
		
		file.write("\n")
		file.write("\n")


		if len(localClass['inherits']) != 0:
			file.write("Object Hierarchy:\n")
			file.write("-----------------\n")
			file.write("\n")
			for heritedClass in localClass['inherits']:
				file.write("\t" + heritedClass['class'] + "\n")
			file.write("\t    |\n")
			file.write("\t    +--> " +  localClass['name'] + "\n")
			file.write("\n")
			file.write("\n")


		"""
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
		"""
		
		if "doxygen" in localClass:
			file.write("Description:\n")
			file.write("------------\n")
			file.write("\n")
			# display Class description :
			file.write(localClass["doxygen"])
			file.write("\n")
			file.write("\n")
		
		
		file.write("Detail:\n")
		file.write("-------\n")
		file.write("\n")
		# display all the class internal functions :
		for function in localClass["methods"]["public"]:
			displayFunction(localClass['namespace'] , function, file, "public:   ", sizeReturn, sizefunction)
			file.write("\n________________________________________________________________________\n\n")
		for function in localClass["methods"]["protected"]:
			displayFunction(localClass['namespace'] , function, file, "protected:", sizeReturn, sizefunction)
			file.write("\n________________________________________________________________________\n\n")
		for function in localClass["methods"]["private"]:
			displayFunction(localClass['namespace'] , function, file, "private:  ", sizeReturn, sizefunction)
			file.write("\n________________________________________________________________________\n\n")



		if len(localClass['inherits']) != 0:
			for heritedClass in localClass['inherits']:
				debug.debug("        heritage : " + str(heritedClass['class']))
				
		
		file.close()


"""

"""

