#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import CppHeaderParser

def parse_doxygen(data) :
	pos = data.find("/*");
	if pos > 0:
		data = data[pos:]
	
	if     data[0] == '/' \
	   and data[1] == '*' \
	   and data[2] == '*':
		data = data[3:len(data)-2]
		data = data.replace("\n** ", "\n")
		data = data.replace("\n**", "\n")
		data = data.replace("\n* ", "\n")
		data = data.replace("\n*", "\n")
		data = data.replace("\n ** ", "\n")
		data = data.replace("\n **", "\n")
		data = data.replace("\n * ", "\n")
		data = data.replace("\n *", "\n")
		data = data.replace("\r", "")
	streams = data.split("@")
	data2 = ""
	for element in streams:
		data2 += "\n"
		if    element[:1] == "\n" \
		   or element[:2] == "\n\n":
			# nothing to do : Nomale case of the first \n
			None
		elif element[:6] == "brief ":
			data2 += element[6:]
			data2 += "\n"
		elif element[:5] == "note ":
			data2 += "\t"
			data2 += "**Notes:** "
			data2 += element[5:]
		elif    element[:14] == "param[in,out] " \
		     or element[:14] == "param[out,in] ":
			data2 += "\t"
			data2 += "**Parameter [input] [output]:** "
			data2 += element[14:]
		elif element[:10] == "param[in] ":
			data2 += "\t"
			data2 += "**Parameter [input]:** "
			data2 += element[10:]
		elif element[:11] == "param[out] ":
			data2 += "\t"
			data2 += "**Parameter [output]:** "
			data2 += element[11:]
		elif element[:6] == "param ":
			data2 += "\t"
			data2 += "**Parameter:** "
			data2 += element[6:]
		elif element[:7] == "return ":
			data2 += "\t"
			data2 += "**Return:** "
			data2 += element[7:]
		else:
			data2 += "unknow : '" + element + "'"
	return data2



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
	if    (    function['constructor'] == True \
	        or function['destructor'] == True \
	        or function['static'] == True ) \
	   and namespace != "":
		lineData = namespace + "::"
	if function['destructor'] :
		lineData += "~"
	lineData += function["name"] + "( ... )"
	file.write("### " + lineData + "\n\n")
	
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
		file.write(parse_doxygen(function["doxygen"]))
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

