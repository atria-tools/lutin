#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
# TODO : Add try of generic input ...
sys.path.append(lutinTools.GetCurrentPath(__file__) + "/ply/ply/")
sys.path.append(lutinTools.GetCurrentPath(__file__) + "/cppParser/CppHeaderParser/")
import CppHeaderParser
import lutinDocHtml
import lutinDocMd

##
## @brief Main Documantion class
## @param[in] moduleName Name of the module of this element
##
class doc:
	def __init__(self, moduleName):
		self.moduleName = moduleName
		self.listClass = dict()
		self.listEnum = dict()
		self.listVariable = dict()
		self.listFunction = dict()
		self.listNamepsaces = dict()
		self.target = None
	
	##
	## @brief Add a File at the parsing system
	## @param[in] filename File To add at the parsing element system.
	## @return True if no error occured, False otherwise
	##
	def add_file(self, filename):
		debug.debug("adding file in documantation : '" + filename + "'");
		try:
			metaData = CppHeaderParser.CppHeader(filename)
		except CppHeaderParser.CppParseError, e:
			debug.warning(" can not parse the file: '" + filename + "' error : " + str(e))
			return False
		
		#debug.info(str(metaData.enums))
		
		# add all classes :
		for element in metaData.classes:
			localClass = metaData.classes[element]
			if localClass['namespace'] == '':
				className = localClass['name']
			else:
				className = localClass['namespace'] + "::" + localClass['name']
			if className in self.listClass.keys():
				debug.warning("Might merge class : '" + className + "' file : " + filename)
			else:
				self.listClass[className] = localClass
		
		# add all enums:
		for localEnum in metaData.enums:
			if localEnum['namespace'] == '':
				enumName = localEnum['name']
			else:
				enumName = localEnum['namespace'] + "::" + localEnum['name']
				enumName = enumName.replace("::::", "::")
			if enumName in self.listEnum.keys():
				debug.warning("Might merge enum : '" + enumName + "' file : " + filename)
			else:
				self.listEnum[enumName] = localEnum
		
		# add all namaspace:
		
		# add all namespaces:
		
		# add all global vars:
		
		# add all global function:
		
		return True
	
	##
	## @brief Generate Documentation at the folder ...
	## @param[in] destFolder Destination folder.
	## @param[in] mode (optinnal) generation output mode {html, markdown ...}
	##
	def generate_documantation(self, target, destFolder, mode="html"):
		# local store of the target
		self.target = target
		if mode == "html":
			if lutinDocHtml.generate(self, destFolder) == False:
				debug.warning("Generation Documentation :'" + mode + "' ==> return an error for " + self.moduleName)
		elif mode == "markdown":
			# todo ...
			None
		else:
			debug.error("Unknow Documantation mode generation :'" + mode + "'")
			self.target = None
			return False
		self.target = None
		return True
	
	##
	## @brief Get the heritage list (parent) of one element.
	## @param[in] element Element name.
	## @return List of all element herited
	##
	def get_heritage_list(self, element):
		list = []
		# get element class :
		if element in self.listClass.keys():
			localClass = self.listClass[element]
			if len(localClass['inherits']) != 0:
				# TODO : Support multiple heritage ...
				isFirst = True
				for heritedClass in localClass['inherits']:
					if isFirst == True:
						list = self.get_heritage_list(heritedClass['class'])
						break;
		debug.verbose("find parent : " + element)
		list.append(element);
		return list
	
	##
	## @brief Get the heritage list (child) of this element.
	## @param[in] curentClassName Element name.
	## @return List of all childs
	##
	def get_down_heritage_list(self, curentClassName):
		list = []
		# get element class :
		for element in self.listClass:
			localClass = self.listClass[element]
			if len(localClass['inherits']) != 0:
				for heritedClass in localClass['inherits']:
					if curentClassName == heritedClass['class']:
						list.append(element)
						break;
		debug.verbose("find childs : " + str(list))
		return list
	
	##
	## @brief trnsform the classname in a generic link (HTML)
	## @param[in] elementName Name of the class requested
	## @return [className, link]
	##
	def get_class_link(self, elementName):
		if    elementName == "const" \
		   or elementName == "enum" \
		   or elementName == "void" \
		   or elementName == "char" \
		   or elementName == "char32_t" \
		   or elementName == "float" \
		   or elementName == "double" \
		   or elementName == "bool" \
		   or elementName == "int8_t" \
		   or elementName == "uint8_t" \
		   or elementName == "int16_t" \
		   or elementName == "uint16_t" \
		   or elementName == "int32_t" \
		   or elementName == "uint32_t" \
		   or elementName == "int64_t" \
		   or elementName == "uint64_t" \
		   or elementName == "int" \
		   or elementName == "T" \
		   or elementName == "CLASS_TYPE" \
		   or elementName[:5] == "std::" \
		   or elementName[:6] == "appl::" \
		   or elementName == "&" \
		   or elementName == "*" \
		   or elementName == "**":
			return [elementName, ""]
		if elementName in self.listClass.keys():
			link = elementName.replace(":","_") + ".html"
			return [elementName, link]
		elif elementName in self.listEnum.keys():
			link = elementName.replace(":","_") + ".html"
			return [elementName, link]
		else:
			return self.target.doc_get_link(elementName)
		return [elementName, ""]
	
	##
	## @brief trnsform the classname in a generic link (HTML) (external access ==> from target)
	## @param[in] elementName Name of the class requested
	## @return [className, link]
	##
	def get_class_link_from_target(self, elementName):
		# reject when auto call :
		if self.target != None:
			return [elementName, ""]
		# search in local list :
		if elementName in self.listClass.keys():
			link = elementName.replace(":","_") + ".html"
			return [elementName, "../" + self.moduleName + "/" + link]
		elif elementName in self.listEnum.keys():
			link = elementName.replace(":","_") + ".html"
			return [elementName, "../" + self.moduleName + "/" + link]
		# did not find :
		return [elementName, ""]
	
	

