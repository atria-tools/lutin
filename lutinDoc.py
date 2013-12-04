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
		self.listVariable = dict()
		self.listFunction = dict()
		self.listNamepsaces = dict()
		
	
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
			debug.error(" can not parse the file: '" + filename + "' error : " + e)
			return False
		
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
		
		# add all namespaces:
		
		# add all global vars:
		
		# add all global function:
		
		return True
	
	##
	## @brief Generate Documentation at the folder ...
	## @param[in] destFolder Destination folder.
	## @param[in] mode (optinnal) generation output mode {html, markdown ...}
	##
	def generate_documantation(self, destFolder, mode="html"):
		if mode == "html":
			if lutinDocHtml.generate(self, destFolder) == False:
				debug.warning("Generation Documentation :'" + mode + "' ==> return an error for " + self.moduleName)
		elif mode == "markdown":
			# todo ...
			None
		else:
			debug.error("Unknow Documantation mode generation :'" + mode + "'")
			return False
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

