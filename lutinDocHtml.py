#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import CppHeaderParser
import re
import codeBB

global_class_link = {
	"std::string"    : "http://www.cplusplus.com/reference/string/string/",
	"std::u16string" : "http://www.cplusplus.com/reference/string/u16string/",
	"std::u32string" : "http://www.cplusplus.com/reference/string/u32string/",
	"std::wstring"   : "http://www.cplusplus.com/reference/string/wstring/",
	"std::vector"    : "http://www.cplusplus.com/reference/vector/vector/"
	}


def replace_type(match):
	value = "<span class=\"code-type\">" + match.group() + "</span>"
	return value

def replace_storage_keyword(match):
	value = "<span class=\"code-storage-keyword\">" + match.group() + "</span>"
	return value

def display_color(valBase):
	# storage keyword :
	p = re.compile("(inline|const|class|virtual|private|public|protected|friend|const|extern|auto|register|static|volatile|typedef|struct|union|enum)")
	val = p.sub(replace_storage_keyword, valBase)
	# type :
	p = re.compile("(bool|BOOL|char(16_t|32_t)?|double|float|u?int(8|16|32|64|128)?(_t)?|long|short|signed|size_t|unsigned|void|(I|U)(8|16|32|64|128))")
	val = p.sub(replace_type, val)
	return val, len(valBase)

def display_type(type, myDoc):
	type = type.replace("inline ", "")
	lenght = 0;
	isFirst = True
	out = ''
	# we split all the element in list sepa=rated with space to keep class... and standard c+ class
	for element in type.split(' '):
		if isFirst == False:
			out += " "
			lenght += 1
		isFirst = False
		# check if the element in internal at the current lib
		name, link = myDoc.get_class_link(element)
		if len(link) != 0:
			out += "<a href=\"" + link + "\" class=\"code-type\">" + name + "</a>"
			lenght += len(element)
		# Ckeck if the variable in a standard class:
		elif element in global_class_link.keys():
			out += "<a href=\"" + global_class_link[element] + "\" class=\"code-type\">" + element + "</a>"
			lenght += len(element)
		else:
			data, lenghtTmp = display_color(element)
			out += data
			lenght += lenghtTmp
	# get every subelement class :
	return [out,lenght]

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
	# TODO : Check if it exist in the parameter list ...
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
		data = data.replace("\r", '')
	streams = data.split("@")
	data2 = ''
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
	
	data3 = ''
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
	if data3 != '':
		data2 += "<ul>\n"
		data2 += data3
		data2 += "</ul>\n"
	return data2

def white_space(size) :
	ret = ''
	for iii in range(len(ret), size):
		ret += " "
	return ret

def display_reduct_function(function, file, classement, sizeReturn, sizefunction, myDoc) :
	file.write(classement + " ")
	lenght = len(classement)+1;
	if function['destructor'] :
		file.write(white_space(sizeReturn) + "~")
		lenght += sizeReturn+1;
	elif function['constructor'] :
		file.write(white_space(sizeReturn+1))
		lenght += sizeReturn+1;
	else :
		typeData, typeLen = display_type(function["rtnType"], myDoc);
		file.write(typeData)
		file.write(white_space(sizeReturn+1 - typeLen))
		lenght += sizeReturn+1;
	parameterPos = lenght + sizefunction+2;
	file.write("<a class=\"code-function\" href=\"#"+ function["name"] + "\">" + function["name"] + "</a>")
	file.write(white_space(sizefunction+1 - len(function["name"])))
	file.write("(")
	isFirst = True
	for param in function["parameters"]:
		if isFirst == False:
			file.write(",<br/>")
			file.write(white_space(parameterPos))
		
		typeData, typeLen = display_type(param["type"], myDoc);
		file.write(typeData)
		if param['name'] != "":
			file.write(" ")
			file.write("<span class=\"code-argument\">" + param['name'] + "</span>")
		isFirst = False
	file.write(");")
	file.write("<br>")


def displayFunction(namespace, function, file, classement, sizeReturn, sizefunction, myDoc) :
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
		file.write("~")
		lenght = 1;
	elif function['constructor'] :
		lenght = 0;
	else :
		typeData, typeLen = display_type(function["rtnType"], myDoc);
		file.write(typeData + " ")
		lenght = typeLen+1;
	
	parameterPos = lenght + len(function["name"]) + 1;
	file.write("<span class=\"code-function\">" + function["name"] + "</span>(")
	isFirst = True
	for param in function["parameters"]:
		if isFirst == False:
			file.write(",\n")
			file.write(white_space(parameterPos))
		typeData, typeLen = display_type(param["type"], myDoc);
		file.write(typeData)
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

def class_name_to_file_name(className):
	className = className.replace(":", "_")
	className = className.replace(" ", "")
	className += ".html"
	return className

def generate(myDoc, outFolder) :
	lutinTools.CopyFile(lutinTools.GetCurrentPath(__file__)+"/theme/base.css", outFolder+"/base.css")
	# create common header
	genericHeader  = "<!DOCTYPE html>\n"
	genericHeader += "<html>\n"
	genericHeader += "<head>\n"
	genericHeader += "	<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0\">\n"
	genericHeader += "	<title>" + myDoc.moduleName + " Library</title>\n"
	genericHeader += "	<link rel=\"stylesheet\" href=\"base.css\">\n"
	genericHeader += "</head>\n"
	genericHeader += "<body>\n"
	genericHeader += "	<div class=\"navbar navbar-fixed-top\">\n"
	genericHeader += "		<div class=\"container\">\n"
	genericHeader += "			<h1>" + myDoc.moduleName + " Library</h1>\n"
	#genericHeader += "			<ul>\n"
	baseNamespace = ""
	for className in sorted(myDoc.listClass.iterkeys()) :
		pos = className.find("::")
		if pos >= 0:
			namespace = className[:pos]
			rest = className[pos+2:]
		else:
			namespace = ""
			rest = className
		if baseNamespace != namespace:
			if baseNamespace != "":
				genericHeader += "				</ul>\n"
			genericHeader += "				<li>" + namespace + "</li>\n"
			genericHeader += "				<ul>\n"
			baseNamespace = namespace
			
		genericHeader += "				<li><a href=\"" + class_name_to_file_name(className) + "\">" + rest + "</a></li>\n"
		
	if baseNamespace != "":
		genericHeader += "				</ul>\n"
	
	for enumName in sorted(myDoc.listEnum.iterkeys()) :
		pos = enumName.find("::")
		if pos >= 0:
			namespace = enumName[:pos]
			rest = enumName[pos+2:]
		else:
			namespace = ""
			rest = enumName
		if baseNamespace != namespace:
			if baseNamespace != "":
				genericHeader += "				</ul>\n"
			genericHeader += "				<li>" + namespace + "</li>\n"
			genericHeader += "				<ul>\n"
			baseNamespace = namespace
			
		genericHeader += "				<li><a href=\"" + class_name_to_file_name(enumName) + "\">" + rest + "</a></li>\n"
		
	if baseNamespace != "":
		genericHeader += "				</ul>\n"
		
	#genericHeader += "			</ul>\n"
	genericHeader += "		</div>\n"
	genericHeader += "	</div>\n"
	genericHeader += "	<div class=\"container\" id=\"content\">\n"
	
	genericFooter  = "	</div>\n"
	genericFooter += "</body>\n"
	genericFooter += "</html>\n"
	
	# create index.hml : 
	file = open(outFolder + "/index.html", "w")
	file.write(genericHeader)
	file.write("<h1>" + myDoc.moduleName + "</h1>");
	file.write("<br/>");
	file.write("TODO : Main page ...");
	file.write("<br/>");
	file.write("<br/>");
	file.write(genericFooter)
	file.close();
	
	for className in sorted(myDoc.listClass.iterkeys()) :
		localClass = myDoc.listClass[className]
		debug.debug("    class: " + className)
		classFileName = outFolder + "/" + class_name_to_file_name(className)
		# create directory (in case)
		lutinTools.CreateDirectoryOfFile(classFileName);
		debug.printElement("doc", myDoc.moduleName, "<==", className)
		# open the file :
		file = open(classFileName, "w")
		
		file.write(genericHeader)
		
		file.write("<h1>Class: " + className + "</h1>\n")
		file.write("<br/>\n")
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
			display_reduct_function(function, file, "+ ", sizeReturn, sizefunction, myDoc)
		for function in localClass["methods"]["protected"]:
			display_reduct_function(function, file, "# ", sizeReturn, sizefunction, myDoc)
		for function in localClass["methods"]["private"]:
			display_reduct_function(function, file, "- ", sizeReturn, sizefunction, myDoc)
		file.write("</pre>\n");
		file.write("\n")
		file.write("\n")
		heritage = myDoc.get_heritage_list(className)
		heritageDown = myDoc.get_down_heritage_list(className)
		if    len(heritage) > 1 \
		   or len(heritageDown) > 0:
			file.write("<h2>Object Hierarchy:</h2>\n")
			file.write("<pre>\n")
			level = 0;
			for heritedClass in heritage:
				if level != 0:
					file.write(white_space(level*4) + "+--> ")
				if heritedClass != className:
					name, link = myDoc.get_class_link(heritedClass)
					file.write("<a href=\"" + link + "\">" + name + "</a>\n")
				else:
					file.write("<b>" + heritedClass + "</b>\n")
				level += 1;
			for heritedClass in heritageDown:
				file.write(white_space(level*4) + "+--> ")
				name, link = myDoc.get_class_link(heritedClass)
				file.write("<a href=\"" + link + "\">" + name + "</a>\n")
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
			displayFunction(localClass['namespace'] , function, file, "+ ", sizeReturn, sizefunction, myDoc)
			file.write("\n<hr/>\n")
		for function in localClass["methods"]["protected"]:
			displayFunction(localClass['namespace'] , function, file, "# ", sizeReturn, sizefunction, myDoc)
			file.write("\n<hr/>\n")
		for function in localClass["methods"]["private"]:
			displayFunction(localClass['namespace'] , function, file, "- ", sizeReturn, sizefunction, myDoc)
			file.write("\n<hr/>\n")
		
		file.write(genericFooter)
		
		file.close()
	
	for enumName in sorted(myDoc.listEnum.iterkeys()) :
		localEnum = myDoc.listEnum[enumName]
		debug.debug("    enum: " + enumName)
		fileName = outFolder + "/" + class_name_to_file_name(enumName)
		# create directory (in case)
		lutinTools.CreateDirectoryOfFile(fileName);
		debug.printElement("doc", myDoc.moduleName, "<==", enumName)
		# open the file :
		file = open(fileName, "w")
		
		file.write(genericHeader)
		
		file.write("<h1>Enum: " + enumName + "</h1>\n")
		file.write("<br/>\n")
		file.write("Value :<br>\n")
		file.write("<ul>\n")
		#debug.info("    enum: " + str(localEnum))
		for value in localEnum["values"]:
			file.write("<li>" + value["name"])
			if "doxygen" in value.keys():
				file.write("       " + value["doxygen"] )
			file.write("</li>")
		file.write("</ul>\n")
		
		file.write(genericFooter)
		
		file.close()
	
	for docInputName in myDoc.listDocFile :
		codeBB.transcode_file(docInputName, docInputName+".html")



