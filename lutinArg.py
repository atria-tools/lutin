#!/usr/bin/python
import sys
import lutinDebug as debug

class argElement:
	def __init__(self, option, value=""):
		self.m_option = option;
		self.m_arg = value;
	
	def GetOptionName(self):
		return self.m_option
	
	def GetArg(self):
		return self.m_arg
	
	def Display(self):
		if len(self.m_arg)==0:
			debug.info("element : " + self.m_option)
		else:
			debug.info("element : " + self.m_option + ":" + self.m_arg)


class argDefine:
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
	
	def GetOptionSmall(self):
		return self.m_optionSmall
		
	def GetOptionBig(self):
		return self.m_optionBig
	
	def NeedParameters(self):
		return self.m_haveParam
	
	def GetPorperties(self):
		return ""
	
	def CheckAvaillable(self, argument):
		if len(self.m_list)==0:
			return True
		for element,desc in self.m_list:
			if element == argument:
				return True
		return False
	
	def Display(self):
		if self.m_optionSmall != "" and self.m_optionBig != "":
			print("		-" + self.m_optionSmall + " / --" + self.m_optionBig)
		elif self.m_optionSmall != "":
			print("		-" + self.m_optionSmall)
		elif self.m_optionSmall != "":
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
	
	def Parse(self, argList, currentID):
		return currentID;


class argSection:
	def __init__(self,
	             sectionName="",
	             desc=""):
		self.m_section = sectionName;
		self.m_description = desc;
	
	def GetOptionSmall(self):
		return ""
		
	def GetOptionBig(self):
		return ""
		
	def GetPorperties(self):
		return " [" + self.m_section + "]"
	
	def Display(self):
		print("	[" + self.m_section + "] : " + self.m_description)
	
	def Parse(self, argList, currentID):
		return currentID;


class lutinArg:
	def __init__(self):
		self.m_listProperties = []
	
	def Add(self, argument):
		self.m_listProperties.append(argument) #argDefine(smallOption, bigOption, haveParameter, parameterList, description));
	
	def AddSection(self, sectionName, sectionDesc):
		self.m_listProperties.append(argSection(sectionName, sectionDesc))
	
	def Parse(self):
		listArgument = [] # composed of list element
		NotParseNextElement=False
		for iii in range(1, len(sys.argv)):
			# special case of parameter in some elements
			if NotParseNextElement==True:
				NotParseNextElement = False
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
					if prop.GetOptionBig()=="":
						continue
					if prop.GetOptionBig() == option[2:2+len(prop.GetOptionBig())]:
						# find it
						debug.verbose("find argument 2 : " + option[2:2+len(prop.GetOptionBig())])
						if prop.NeedParameters()==True:
							internalSub = option[2+len(prop.GetOptionBig()):]
							if len(internalSub)!=0:
								if len(optionParam)!=0:
									# wrong argument ...
									debug.warning("maybe wrong argument for : '" + prop.GetOptionBig() + "' cmdLine='" + argument + "'")
									prop.Display()
									continue
								optionParam = internalSub
							if len(optionParam)==0:
								#Get the next parameters 
								if len(sys.argv) > iii+1:
									optionParam = sys.argv[iii+1]
									NotParseNextElement=True
								else :
									# missing arguments
									debug.warning("parsing argument error : '" + prop.GetOptionBig() + "' Missing : subParameters ... cmdLine='" + argument + "'")
									prop.Display()
									exit(-1)
							if prop.CheckAvaillable(optionParam)==False:
								debug.warning("argument error : '" + prop.GetOptionBig() + "' SubParameters not availlable ... cmdLine='" + argument + "' option='" + optionParam + "'")
								prop.Display()
								exit(-1)
							listArgument.append(argElement(prop.GetOptionBig(),optionParam))
							argumentFound = True
						else:
							if len(optionParam)!=0:
								debug.warning("parsing argument error : '" + prop.GetOptionBig() + "' need no subParameters : '" + optionParam + "'   cmdLine='" + argument + "'")
								prop.Display()
							listArgument.append(argElement(prop.GetOptionBig()))
							argumentFound = True
						break;
				if False==argumentFound:
					debug.error("UNKNOW argument : '" + argument + "'")
			elif option[:1]=="-":
				# small argument
				for prop in self.m_listProperties:
					if prop.GetOptionSmall()=="":
						continue
					if prop.GetOptionSmall() == option[1:1+len(prop.GetOptionSmall())]:
						# find it
						debug.verbose("find argument 1 : " + option[1:1+len(prop.GetOptionSmall())])
						if prop.NeedParameters()==True:
							internalSub = option[1+len(prop.GetOptionSmall()):]
							if len(internalSub)!=0:
								if len(optionParam)!=0:
									# wrong argument ...
									debug.warning("maybe wrong argument for : '" + prop.GetOptionBig() + "' cmdLine='" + argument + "'")
									prop.Display()
									continue
								optionParam = internalSub
							if len(optionParam)==0:
								#Get the next parameters 
								if len(sys.argv) > iii+1:
									optionParam = sys.argv[iii+1]
									NotParseNextElement=True
								else :
									# missing arguments
									debug.warning("parsing argument error : '" + prop.GetOptionBig() + "' Missing : subParameters  cmdLine='" + argument + "'")
									prop.Display()
									exit(-1)
							if prop.CheckAvaillable(optionParam)==False:
								debug.warning("argument error : '" + prop.GetOptionBig() + "' SubParameters not availlable ... cmdLine='" + argument + "' option='" + optionParam + "'")
								prop.Display()
								exit(-1)
							listArgument.append(argElement(prop.GetOptionBig(),optionParam))
							argumentFound = True
						else:
							if len(optionParam)!=0:
								debug.warning("parsing argument error : '" + prop.GetOptionBig() + "' need no subParameters : '" + optionParam + "'  cmdLine='" + argument + "'")
								prop.Display()
							listArgument.append(argElement(prop.GetOptionBig()))
							argumentFound = True
						break;
			
			if argumentFound==False:
				#unknow element ... ==> just add in the list ...
				debug.verbose("unknow argument : " + argument)
				listArgument.append(argElement(argument, ""))
			
		#for argument in listArgument:
		#	argument.Display()
		#exit(0)
		return listArgument;
	
	
	
	def Display(self):
		print "usage:"
		listOfPropertiesArg = "";
		for element in self.m_listProperties :
			listOfPropertiesArg += element.GetPorperties()
		print "	" + sys.argv[0] + listOfPropertiesArg + " ..."
		for element in self.m_listProperties :
			element.Display()