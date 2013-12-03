#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import CppHeaderParser

def display_doxygen_param(comment, input, output):
	data = "<b>Parameter"
	if input == True:
		data += " [input]"
	if output == True:
		data += " [output]"
	data += ":</b> "
	#extract first element:
	val = comment.find(" ")
	var = comment[:val]
	endComment = comment[val:]
	data += "<span class=\"code-argument\">" + var + "</span> " + endComment
	
	data += "<br/>"
	return data


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
		if    element[:1] == "\n" \
		   or element[:2] == "\n\n":
			# nothing to do : Nomale case of the first \n
			None
		elif element[:6] == "brief ":
			data2 += element[6:]
			data2 += "<br/>"
	
	for element in streams:
		if    element[:1] == "\n" \
		   or element[:2] == "\n\n":
			# nothing to do : Nomale case of the first \n
			None
		elif element[:5] == "note ":
			data2 += "<b>Notes:</b> "
			data2 += element[5:]
			data2 += "<br/> "
	
	data3 = ""
	for element in streams:
		if    element[:1] == "\n" \
		   or element[:2] == "\n\n":
			# nothing to do : Nomale case of the first \n
			None
		elif    element[:14] == "param[in,out] " \
		     or element[:14] == "param[out,in] ":
			data3 += display_doxygen_param(element[14:], True, True)
		elif element[:10] == "param[in] ":
			data3 += display_doxygen_param(element[10:], True, False)
		elif element[:11] == "param[out] ":
			data3 += display_doxygen_param(element[11:], False, True)
		elif element[:6] == "param ":
			data3 += display_doxygen_param(element[6:], False, False)
		elif element[:7] == "return ":
			data3 += "<b>Return:</b> "
			data3 += element[7:]
			data3 += "<br/>"
	if data3 != "":
		data2 += "<ul>\n"
		data2 += data3
		data2 += "</ul>\n"
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
	parameterPos = len(lineData) + sizefunction+2;
	lineData +="<a class=\"code-function\" href=\"#"+ function["name"] + "\">" + function["name"] + "</a>"
	lineData += writeExpendSize("", sizefunction+1 - len(function["name"]))
	lineData += "("
	file.write(lineData);
	isFirst = True
	for param in function["parameters"]:
		if isFirst == False:
			file.write(",<br/>")
			file.write(writeExpendSize("",parameterPos))
		file.write(param['type'])
		if param['name'] != "":
			file.write(" ")
			file.write("<span class=\"code-argument\">" + param['name'] + "</span>")
		isFirst = False
	file.write(");")
	file.write("<br>")


def displayFunction(namespace, function, file, classement, sizeReturn, sizefunction) :
	lineData = ""
	if    (    function['constructor'] == True \
	        or function['destructor'] == True \
	        or function['static'] == True ) \
	   and namespace != "":
		lineData = namespace + "::"
	if function['destructor'] :
		lineData += "~"
	lineData +="<a id=\""+ function["name"] + "\">" + function["name"] + "</a> ()"
	file.write("<h3>" + lineData + "</h3>\n\n")
	
	file.write("<pre>\n");
	if function['destructor'] :
		lineData = "~"
	elif function['constructor'] :
		lineData = ""
	else :
		lineData = function["rtnType"] + " "
	
	parameterPos = len(lineData) + len(function["name"]) + 1;
	lineData += "<span class=\"code-function\">" + function["name"] + "</span>"
	lineData += "("
	file.write(lineData);
	isFirst = True
	for param in function["parameters"]:
		if isFirst == False:
			file.write(",\n")
			file.write(writeExpendSize("", parameterPos))
		file.write(param['type'])
		if param['name'] != "":
			file.write(" ")
			file.write("<span class=\"code-argument\">" + param['name'] + "</span>")
		isFirst = False
	file.write(");")
	file.write("</pre>\n");
	file.write("<br/>\n")
	if "doxygen" in function:
		# TODO : parse doxygen ...
		file.write(parse_doxygen(function["doxygen"]))
	file.write("<br/>\n")





def calsulateSizeFunction(function, size) :
	if len(function["name"]) > size:
		return len(function["name"])+1
	return size

def calsulateSizeReturn(function, size) :
	if len(function["rtnType"]) > size:
		return len(function["rtnType"])+1
	return size

def add_header(file):
	file.write("<!DOCTYPE html>\n")
	file.write("<html>\n")
	file.write("<head>\n")
	file.write("	<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0\">\n")
	file.write("	<title>Ewol Library</title>\n")
	file.write("	<link rel=\"stylesheet\" href=\"base.css\">\n")
	file.write("</head>\n")
	file.write("<body>\n")
	file.write("	<div class=\"navbar navbar-fixed-top\">\n");
	file.write("		<div class=\"container\">\n")
	file.write("			Ewol Library\n")
	file.write("		</div>\n")
	file.write("	</div>\n")
	file.write("	<div class=\"container\" id=\"content\">\n")

def add_buttom(file):
	file.write("	</div>\n")
	file.write("</body>\n")
	file.write("</html>\n")

def GenerateDocFile(filename, outFolder) :
	try:
		metaData = CppHeaderParser.CppHeader(filename)
	except CppHeaderParser.CppParseError,  e:
		debug.error(" can not parse the file: '" + filename + "' error : " + e)
		return False
	
	lutinTools.CreateDirectoryOfFile(outFolder+"/");
	lutinTools.CopyFile(lutinTools.GetCurrentPath(__file__)+"/theme/base.css", outFolder+"/base.css")
	
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
		classFileName += ".html"
		file = open(classFileName, "w")
		
		add_header(file)
		
		file.write("<h1>" + className + "</h1>\n")
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
		
		file.write("<h2>Synopsis:</h2>\n")
		# display all functions :
		# TODO: ...
		file.write("<pre>\n");
		for function in localClass["methods"]["public"]:
			displayReductFunction(function, file, "public:   ", sizeReturn, sizefunction)
		for function in localClass["methods"]["protected"]:
			displayReductFunction(function, file, "protected:", sizeReturn, sizefunction)
		for function in localClass["methods"]["private"]:
			displayReductFunction(function, file, "private:  ", sizeReturn, sizefunction)
		file.write("</pre>\n");
		file.write("\n")
		file.write("\n")


		if len(localClass['inherits']) != 0:
			file.write("<h2>Object Hierarchy:</h2>\n")
			file.write("<pre>\n")
			for heritedClass in localClass['inherits']:
				file.write("" + heritedClass['class'] + "\n")
			file.write("    |\n")
			file.write("    +--> " +  localClass['name'] + "\n")
			file.write("</pre>\n")
			file.write("<br/>\n")


		"""
		file.write("<h2>Signals:</h2>\n")
		# display all signals :
		# TODO: ...
		
		file.write("<h2>Configuration:</h2>\n")
		# display all configuration :
		# TODO: ...
		"""
		
		if "doxygen" in localClass:
			file.write("<h2>Description:</h2>\n")
			# display Class description :
			file.write(localClass["doxygen"])
		
		
		file.write("<h2>Detail:<h2>\n")
		# display all the class internal functions :
		for function in localClass["methods"]["public"]:
			displayFunction(localClass['namespace'] , function, file, "public:   ", sizeReturn, sizefunction)
			file.write("\n<hr/>\n")
		for function in localClass["methods"]["protected"]:
			displayFunction(localClass['namespace'] , function, file, "protected:", sizeReturn, sizefunction)
			file.write("\n<hr/>\n")
		for function in localClass["methods"]["private"]:
			displayFunction(localClass['namespace'] , function, file, "private:  ", sizeReturn, sizefunction)
			file.write("\n<hr/>\n")
		
		add_buttom(file)
		
		file.close()


"""

"""

