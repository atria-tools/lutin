#!/usr/bin/python
import lutinDebug as debug
import datetime
import lutinTools
import lutinModule

class Target:
	def __init__(self, name, typeCompilator, debugMode, generatePackage, arch, cross):
		self.arch = arch
		self.cross = cross
		self.name=name
		self.endGeneratePackage = generatePackage
		debug.info("=================================");
		debug.info("== Target='" + self.name + "'");
		debug.info("=================================");
		self.ar=self.cross + "ar"
		self.ranlib=self.cross + "ranlib"
		if typeCompilator == "clang":
			self.cc=self.cross + "clang"
			self.xx=self.cross + "clang++"
			#self.ar=self.cross + "llvm-ar"
			#self.ranlib="ls"
		else:
			self.cc=self.cross + "gcc"
			self.xx=self.cross + "g++"
			#self.ar=self.cross + "ar"
			#self.ranlib=self.cross + "ranlib"
		self.ld=self.cross + "ld"
		self.nm=self.cross + "nm"
		self.strip=self.cross + "strip"
		self.dlltool=self.cross + "dlltool"
		###############################################################################
		# Target global variables.
		###############################################################################
		self.global_include_cc=[]
		self.global_flags_cc=['-D__TARGET_OS__'+self.name]
		if self.name != "Windows":
			self.global_flags_xx=['-std=c++11']
			self.global_flags_mm=['-std=c++11']
		else:
			self.global_flags_xx=['-std=c++0X']
			self.global_flags_mm=[]
		self.global_flags_m=[]
		self.global_flags_ar=['rcs']
		self.global_flags_ld=[]
		self.global_flags_ld_shared=[]
		self.global_libs_ld=[]
		self.global_libs_ld_shared=[]
		
		self.global_sysroot=""
		
		self.suffix_cmdLine='.cmd'
		self.suffix_dependence='.d'
		self.suffix_obj='.o'
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.so'
		self.suffix_binary=''
		self.suffix_package='.deb'
		
		self.folder_arch="/" + self.name
		
		if "debug"==debugMode:
			self.buildMode = "debug"
		else:
			self.buildMode = "release"
		self.folder_out="/out" + self.folder_arch + "/" + self.buildMode
		self.folder_final="/final"
		self.folder_staging="/staging"
		self.folder_build="/build"
		self.folder_bin="/usr/bin"
		self.folder_lib="/usr/lib"
		self.folder_data="/usr/share"
		self.folder_doc="/usr/share/doc"
		self.buildDone=[]
		self.buildTreeDone=[]
		self.moduleList=[]
		# output staging files list :
		self.listFinalFile=[]
		
	
	def AddFileStaging(self, inputFile, outputFile):
		for source, dst in self.listFinalFile:
			if dst == outputFile :
				debug.verbose("already added : " + outputFile)
				return
		debug.verbose("add file : '" + inputFile + "' ==> '" + outputFile + "'");
		self.listFinalFile.append([inputFile,outputFile])
	
	def copyToStaging(self, binaryName):
		baseFolder = self.GetStagingFolderData(binaryName)
		for source, dst in self.listFinalFile:
			debug.verbose("must copy file : '" + source + "' ==> '" + dst + "'");
			lutinTools.CopyFile(source, baseFolder+"/"+dst)
	
	
	def CleanModuleTree(self):
		self.buildTreeDone = []
		self.listFinalFile = []
	
	
	# TODO : Remove this hack ... ==> really bad ... but usefull
	def SetEwolFolder(self, folder):
		self.folder_ewol = folder
	
	
	def fileGenerateObject(self,binaryName,moduleName,basePath,file):
		list=[]
		list.append(basePath + "/" + file)
		list.append(self.GetBuildFolder(moduleName) + "/" + file + self.suffix_obj)
		list.append(self.GetBuildFolder(moduleName) + "/" + file + self.suffix_dependence)
		list.append(self.GetBuildFolder(moduleName) + "/" + file + self.suffix_cmdLine)
		return list
	"""
		return a list of 3 elements :
			0 : sources files (can be a list)
			1 : destination file
			2 : dependence files module (*.d)
	"""
	def GenerateFile(self,binaryName,moduleName,basePath,file,type):
		list=[]
		if (type=="bin"):
			list.append(file)
			list.append(self.GetStagingFolder(binaryName) + "/" + self.folder_bin + "/" + moduleName + self.suffix_binary)
			list.append(self.GetBuildFolder(moduleName) + "/" + moduleName + self.suffix_dependence)
			list.append(self.GetStagingFolder(binaryName) + "/" + self.folder_bin + "/" + moduleName + self.suffix_cmdLine)
		elif (type=="lib-shared"):
			list.append(file)
			list.append(self.GetStagingFolder(binaryName) + "/" + self.folder_lib + "/" + moduleName + self.suffix_lib_dynamic)
			list.append(self.GetBuildFolder(moduleName) + "/" + moduleName + self.suffix_dependence)
			list.append(self.GetStagingFolder(binaryName) + "/" + self.folder_lib + "/" + moduleName + self.suffix_cmdLine)
		elif (type=="lib-static"):
			list.append(file)
			list.append(self.GetBuildFolder(moduleName) + "/" + moduleName + self.suffix_lib_static)
			list.append(self.GetBuildFolder(moduleName) + "/" + moduleName + self.suffix_dependence)
			list.append(self.GetBuildFolder(moduleName) + "/" + moduleName + self.suffix_cmdLine)
		else:
			debug.error("unknow type : " + type)
		return list
	
	def GetFinalFolder(self):
		return lutinTools.GetRunFolder() + self.folder_out + self.folder_final
	
	def GetStagingFolder(self, binaryName):
		return lutinTools.GetRunFolder() + self.folder_out + self.folder_staging + "/" + binaryName
	
	def GetStagingFolderData(self, binaryName):
		return self.GetStagingFolder(binaryName) + self.folder_data + "/" + binaryName
	
	def GetBuildFolder(self, moduleName):
		return lutinTools.GetRunFolder() + self.folder_out + self.folder_build + "/" + moduleName
	
	def IsModuleBuild(self,module):
		for mod in self.buildDone:
			if mod == module:
				return True
		self.buildDone.append(module)
		return False
	
	def IsModuleBuildTree(self,module):
		for mod in self.buildTreeDone:
			if mod == module:
				return True
		self.buildTreeDone.append(module)
		return False
	
	def AddModule(self, newModule):
		debug.debug("Import nodule for Taget : " + newModule.name)
		self.moduleList.append(newModule)
	
	
	# return inherit packages ...
	"""
	def Build(self, name, packagesName):
		for module in self.moduleList:
			if module.name == name:
				return module.Build(self, packagesName)
		debug.error("request to build an un-existant module name : '" + name + "'")
	"""
	
	def BuildTree(self, name, packagesName):
		for module in self.moduleList:
			if module.name == name:
				module.BuildTree(self, packagesName)
				return
		debug.error("request to build tree on un-existant module name : '" + name + "'")
	
	def Clean(self, name):
		for module in self.moduleList:
			if module.name == name:
				module.Clean(self)
				return
		debug.error("request to clean an un-existant module name : '" + name + "'")
	
	def LoadIfNeeded(self, name):
		for elem in self.moduleList:
			if elem.name == name:
				return
		lutinModule.LoadModule(self, name)
	
	def LoadAll(self):
		listOfAllTheModule = lutinModule.ListAllModule()
		for modName in listOfAllTheModule:
			self.LoadIfNeeded(modName)
	
	def Build(self, name, packagesName=None):
		if name == "dump":
			debug.info("dump all")
			self.LoadAll()
			print 'Dump all module properties'
			for mod in self.moduleList:
				mod.Display(self)
		elif name == "all":
			debug.info("Build all")
			self.LoadAll()
			for mod in self.moduleList:
				if self.name=="Android":
					if mod.type == "PACKAGE":
						mod.Build(self, None)
				else:
					if    mod.type == "BINARY" \
					   or mod.type == "PACKAGE":
						mod.Build(self, None)
		elif name == "clean":
			debug.info("Clean all")
			self.LoadAll()
			for mod in self.moduleList:
				mod.Clean(self)
		else:
			# get the action an the module ....
			gettedElement = name.split("-")
			moduleName = gettedElement[0]
			if len(gettedElement)>=2:
				actionName = gettedElement[1]
			else :
				actionName = "build"
			debug.verbose("requested : " + moduleName + "-" + actionName)
			if actionName == "install":
				self.Build(moduleName + "-build")
				self.InstallPackage(moduleName)
			elif actionName == "uninstall":
				self.UnInstallPackage(moduleName)
			elif actionName == "log":
				self.Log(moduleName)
			else:
				self.LoadIfNeeded(moduleName)
				# clean requested
				for mod in self.moduleList:
					if mod.name == moduleName:
						if actionName == "dump":
							debug.info("dump module '" + moduleName + "'")
							return mod.Display(self)
						elif actionName == "clean":
							debug.info("clean module '" + moduleName + "'")
							return mod.Clean(self)
						elif actionName == "build":
							debug.debug("build module '" + moduleName + "'")
							return mod.Build(self, None)
				debug.error("not know module name : '" + moduleName + "' to '" + actionName + "' it")
	

__startTargetName="lutinTarget"

def TargetLoad(targetName, compilator, mode, generatePackage):
	theTarget = __import__(__startTargetName + targetName)
	#try:
	tmpTarget = theTarget.Target(compilator, mode, generatePackage)
	return tmpTarget
	#except:
	#	debug.error("Can not create the Target : '" + targetName + "'")
