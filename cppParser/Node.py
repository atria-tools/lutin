#!/usr/bin/python
import lutinDebug as debug

accessList = ['private', 'protected', 'public']

def debug_space(level):
	ret = ""
	for iii in range(0,level):
		ret += "    "
	return ret

class Node():
	def __init__(self, type, name="", file="", lineNumber=0):
		self.nodeType = type
		self.name = name
		self.doc = None
		self.fileName = file
		self.lineNumber = lineNumber
		self.subList = None
		self.access = None
		
	def to_str(self):
		return ""
	
	def str(self):
		return self.to_str()
	
	def get_node_type(self):
		return self.nodeType
	
	def get_name(self):
		return self.name
	
	def debug_display(self, level=0, access = None):
		if access == 'private':
			debug.info(debug_space(level) + "- " + self.nodeType + " => " + self.name)
		elif access == 'protected':
			debug.info(debug_space(level) + "# " + self.nodeType + " => " + self.name)
		elif access == 'public':
			debug.info(debug_space(level) + "+ " + self.nodeType + " => " + self.name)
		else:
			debug.info(debug_space(level) + self.nodeType + " => " + self.name)
		if self.subList!= None:
			for element in self.subList:
				if 'access' in element.keys():
					element['node'].debug_display(level+1, element['access'])
				else:
					element['node'].debug_display(level+1)
	
	def set_access(self, access):
		if access not in accessList:
			debug.warning("This is not a valid access : '" + access + "' : availlable : " + str(accessList))
			return
		if self.access == None:
			debug.error("This Node does not support acces configuration...")
			return
		self.access = access
	
	def get_access(self):
		return self.access
	
	def append(self, newSubElement):
		# just add it in a sub List :
		if self.subList == None:
			debug.error("can not add a '" + newSubElement.nodeType + "' at this '" + self.nodeType + "'")
			return
		if newSubElement.get_node_type() != 'namespace':
			if self.access == None:
				self.subList.append({'node' : newSubElement})
			else:
				self.subList.append({'access' : self.access, 'node' : newSubElement})
			return
		
		# check if the element already exist
		for element in self.subList:
			if element['node'].get_node_type() == 'namespace':
				if element['node'].get_name() == newSubElement.get_name():
					debug.verbose("fusionate with previous declaration")
					element['node'].fusion(newSubElement)
					return
		# normal case adding :
		if self.access == None:
			self.subList.append({'node' : newSubElement})
		else:
			self.subList.append({'access' : self.access, 'node' : newSubElement})
	
	##
	## @ brief only for namespace :
	## 
	##
	def fusion(self, addedElement):
		for element in addedElement.subList:
			self.append(element['node'])
	
	##
	## @brief Get the list of all specify type
	## @param[in] type Type requested ['namespace', 'class', 'struct', 'methode', 'enum', 'define', 'union', 'variable', 'constructor', 'destructor'] (can be a list)
	## @param[in] sorted Request to sort the return list.
	## @return The requested list or []
	##
	def get_all_sub_type(self, type='all', sorted = False):
		if type == 'all':
			return self.subList
		if isinstance(type, list) == False:
			type = [type]
		if self.subList == None:
			return []
		ret = []
		for element in self.subList:
			if element['node'].get_node_type() in type:
				ret.append(element)
		if sorted == True:
			# TODO : Sorted the list ...
			pass
		return ret



class MainNode(Node):
	def __init__(self, type="library", name=""):
		Node.__init__(self, type, name)
		self.subList = []