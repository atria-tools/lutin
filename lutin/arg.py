#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import sys
from . import debug

class ArgElement:
	def __init__(self, option, value=""):
		self.m_option = option;
		self.m_arg = value;
	
	def get_option_nName(self):
		return self.m_option
	
	def get_arg(self):
		return self.m_arg
	
	def display(self):
		if len(self.m_arg)==0:
			debug.info("option : " + self.m_option)
		elif len(self.m_option)==0:
			debug.info("element :       " + self.m_arg)
		else:
			debug.info("option : " + self.m_option + ":" + self.m_arg)


class ArgDefine:
	def __init__(self,
	             smallOption="", # like v for -v
	             bigOption="", # like verbose for --verbose
	             list=[], # ["val", "description"]
	             desc="",
	             haveParam=False):
		self.m_optionSmall = smallOption;
		self.m_optionBig = bigOption;
		self.m_list = list;
		if len(self.m_list)!=0:
			self.m_haveParam = True
		else:
			if True==haveParam:
				self.m_haveParam = True
			else:
				self.m_haveParam = False
		self.m_description = desc;
	
	def get_option_small(self):
		return self.m_optionSmall
		
	def get_option_big(self):
		return self.m_optionBig
	
	def need_parameters(self):
		return self.m_haveParam
	
	def get_porperties(self):
		return ""
	
	def check_availlable(self, argument):
		if len(self.m_list)==0:
			return True
		for element,desc in self.m_list:
			if element == argument:
				return True
		return False
	
	def display(self):
		if self.m_optionSmall != "" and self.m_optionBig != "":
			print("		-" + self.m_optionSmall + " / --" + self.m_optionBig)
		elif self.m_optionSmall != "":
			print("		-" + self.m_optionSmall)
		elif self.m_optionBig != "":
			print("		--" + self.m_optionBig)
		else:
			print("		???? ==> internal error ...")
		if self.m_description != "":
			print("			" + self.m_description)
		if len(self.m_list)!=0:
			hasDescriptiveElement=False
			for val,desc in self.m_list:
				if desc!="":
					hasDescriptiveElement=True
					break;
			if hasDescriptiveElement==True:
				for val,desc in self.m_list:
					print("				" + val + " : " + desc)
			else:
				tmpElementPrint = ""
				for val,desc in self.m_list:
					if len(tmpElementPrint)!=0:
						tmpElementPrint += " / "
					tmpElementPrint += val
				print("				{ " + tmpElementPrint + " }")
	
	def parse(self, argList, currentID):
		return currentID;


class ArgSection:
	def __init__(self,
	             sectionName="",
	             desc=""):
		self.m_section = sectionName;
		self.m_description = desc;
	
	def get_option_small(self):
		return ""
		
	def get_option_big(self):
		return ""
		
	def get_porperties(self):
		return " [" + self.m_section + "]"
	
	def display(self):
		print("	[" + self.m_section + "] : " + self.m_description)
	
	def parse(self, argList, currentID):
		return currentID;


class LutinArg:
	def __init__(self):
		self.m_listProperties = []
	
	def add(self, argument):
		self.m_listProperties.append(argument) #ArgDefine(smallOption, bigOption, haveParameter, parameterList, description));
	
	def add_section(self, sectionName, sectionDesc):
		self.m_listProperties.append(ArgSection(sectionName, sectionDesc))
	
	def parse(self):
		listArgument = [] # composed of list element
		NotparseNextElement=False
		for iii in range(1, len(sys.argv)):
			# special case of parameter in some elements
			if NotparseNextElement==True:
				NotparseNextElement = False
				continue
			debug.verbose("parse [" + str(iii) + "]=" + sys.argv[iii])
			argument = sys.argv[iii]
			optionList = argument.split("=")
			debug.verbose(str(optionList))
			if type(optionList) == type(str()):
				option = optionList
			else:
				option = optionList[0]
			optionParam = argument[len(option)+1:]
			debug.verbose(option)
			argumentFound=False;
			if option[:2]=="--":
				# big argument
				for prop in self.m_listProperties:
					if prop.get_option_big()=="":
						continue
					if prop.get_option_big() == option[2:]:
						# find it
						debug.verbose("find argument 2 : " + option[2:])
						if prop.need_parameters()==True:
							internalSub = option[2+len(prop.get_option_big()):]
							if len(internalSub)!=0:
								if len(optionParam)!=0:
									# wrong argument ...
									debug.warning("maybe wrong argument for : '" + prop.get_option_big() + "' cmdLine='" + argument + "'")
									prop.display()
									continue
								optionParam = internalSub
							if len(optionParam)==0:
								#Get the next parameters 
								if len(sys.argv) > iii+1:
									optionParam = sys.argv[iii+1]
									NotparseNextElement=True
								else :
									# missing arguments
									debug.warning("parsing argument error : '" + prop.get_option_big() + "' Missing : subParameters ... cmdLine='" + argument + "'")
									prop.display()
									exit(-1)
							if prop.check_availlable(optionParam)==False:
								debug.warning("argument error : '" + prop.get_option_big() + "' SubParameters not availlable ... cmdLine='" + argument + "' option='" + optionParam + "'")
								prop.display()
								exit(-1)
							listArgument.append(ArgElement(prop.get_option_big(),optionParam))
							argumentFound = True
						else:
							if len(optionParam)!=0:
								debug.warning("parsing argument error : '" + prop.get_option_big() + "' need no subParameters : '" + optionParam + "'   cmdLine='" + argument + "'")
								prop.display()
							listArgument.append(ArgElement(prop.get_option_big()))
							argumentFound = True
						break;
				if False==argumentFound:
					debug.error("UNKNOW argument : '" + argument + "'")
			elif option[:1]=="-":
				# small argument
				for prop in self.m_listProperties:
					if prop.get_option_small()=="":
						continue
					if prop.get_option_small() == option[1:1+len(prop.get_option_small())]:
						# find it
						debug.verbose("find argument 1 : " + option[1:1+len(prop.get_option_small())])
						if prop.need_parameters()==True:
							internalSub = option[1+len(prop.get_option_small()):]
							if len(internalSub)!=0:
								if len(optionParam)!=0:
									# wrong argument ...
									debug.warning("maybe wrong argument for : '" + prop.get_option_big() + "' cmdLine='" + argument + "'")
									prop.display()
									continue
								optionParam = internalSub
							if len(optionParam)==0:
								#Get the next parameters 
								if len(sys.argv) > iii+1:
									optionParam = sys.argv[iii+1]
									NotparseNextElement=True
								else :
									# missing arguments
									debug.warning("parsing argument error : '" + prop.get_option_big() + "' Missing : subParameters  cmdLine='" + argument + "'")
									prop.display()
									exit(-1)
							if prop.check_availlable(optionParam)==False:
								debug.warning("argument error : '" + prop.get_option_big() + "' SubParameters not availlable ... cmdLine='" + argument + "' option='" + optionParam + "'")
								prop.display()
								exit(-1)
							listArgument.append(ArgElement(prop.get_option_big(),optionParam))
							argumentFound = True
						else:
							if len(optionParam)!=0:
								debug.warning("parsing argument error : '" + prop.get_option_big() + "' need no subParameters : '" + optionParam + "'  cmdLine='" + argument + "'")
								prop.display()
							listArgument.append(ArgElement(prop.get_option_big()))
							argumentFound = True
						break;
			
			if argumentFound==False:
				#unknow element ... ==> just add in the list ...
				debug.verbose("unknow argument : " + argument)
				listArgument.append(ArgElement("", argument))
			
		#for argument in listArgument:
		#	argument.display()
		#exit(0)
		return listArgument;
	
	
	
	def display(self):
		print("usage:")
		listOfPropertiesArg = "";
		for element in self.m_listProperties :
			listOfPropertiesArg += element.get_porperties()
		print("	" + sys.argv[0] + listOfPropertiesArg + " ...")
		for element in self.m_listProperties :
			element.display()