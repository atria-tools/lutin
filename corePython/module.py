#!/usr/bin/python
import sys
import os
import inspect
import fnmatch
import module
import host
import buildTools
import debug
import buildList
import heritage
import dependency

def RunCommand(cmdLine):
	debug.debug(cmdLine)
	ret = os.system(cmdLine)
	# TODO : Use "subprocess" instead ==> permit to pipline the renderings ...
	if ret != 0:
		#print "result val = " + str(ret)
		debug.error("can not compile file ... ")
"""
	
"""
class module:
	"""
	Module class represent all system needed for a specific
		module like 
			- type (bin/lib ...)
			- dependency
			- flags
			- files
			- ...
	"""
	def __init__(self, file, moduleName, moduleType):
		## Remove all variable to prevent error of multiple deffinition of the module ...
		self.originFile=''
		self.originFolder=''
		# type of the module:
		self.type='LIBRARY'
		# Name of the module
		self.name=''
		# Dependency list:
		self.depends=[]
		# export PATH
		self.export_path=[]
		self.local_path=[]
		self.export_flags_ld=[]
		self.export_flags_cc=[]
		self.export_flags_xx=[]
		self.export_flags_m=[]
		self.export_flags_mm=[]
		# list of all flags:
		self.flags_ld=[]
		self.flags_cc=[]
		self.flags_xx=[]
		self.flags_m=[]
		self.flags_mm=[]
		self.flags_s=[]
		self.flags_ar=[]
		# sources list:
		self.src=[]
		# copy files and folders:
		self.files=[]
		self.folders=[]
		self.isBuild=False
		## end of basic INIT ...
		if moduleType == 'BINARY' \
				or moduleType == 'LIBRARY' \
				or moduleType == 'PACKAGE' \
				or moduleType == 'PREBUILD':
			self.type=moduleType
		else :
			debug.error('for module "%s"' %moduleName)
			debug.error('    ==> error : "%s" ' %moduleType)
			raise 'Input value error'
		self.originFile = file;
		self.originFolder = buildTools.GetCurrentPath(self.originFile)
		self.name=moduleName
		self.localHeritage = heritage.heritage(self)
	
	###############################################################################
	## Commands for running gcc to compile a m++ file.
	###############################################################################
	def Compile_mm_to_o(self, file, binary, target, depancy):
		# TODO : Check depedency ...
		buildTools.CreateDirectoryOfFile(dst)
		debug.printElement("m++", self.name, "<==", file)
		"""
		cmdLine= $(TARGET_CXX) \
			-o " + dst + " \
			$(TARGET_GLOBAL_C_INCLUDES) \
			$(PRIVATE_C_INCLUDES) \
			$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
			$(TARGET_GLOBAL_CFLAGS) $(TARGET_GLOBAL_CPPFLAGS) $(CXX_FLAGS_WARNINGS) \
			$(PRIVATE_CFLAGS) $(PRIVATE_CPPFLAGS) \
			"-c -MMD -MP -g" 
			"-x objective-c" +
			src
		"""
		return tmpList[1]
	
	###############################################################################
	## Commands for running gcc to compile a m file.
	###############################################################################
	def Compile_m_to_o(self, file, binary, target, depancy):
		# TODO : Check depedency ...
		buildTools.CreateDirectoryOfFile(dst)
		debug.printElement("m", self.name, "<==", file)
		"""
		$(TARGET_CC) \
			-o $@ \
			$(TARGET_GLOBAL_C_INCLUDES) \
			$(PRIVATE_C_INCLUDES) \
			$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
			$(TARGET_GLOBAL_CFLAGS) $(TARGET_GLOBAL_CPPFLAGS) $(CXX_FLAGS_WARNINGS) \
			$(PRIVATE_CFLAGS) $(PRIVATE_CPPFLAGS) \
			-D__EWOL_APPL_NAME__="$(PROJECT_NAME2)" \
			-c -MMD -MP -g \
			-x objective-c \
			$(call path-from-top,$<)
		"""
		return tmpList[1]
	
	###############################################################################
	## Commands for running gcc to compile a C++ file.
	###############################################################################
	def Compile_xx_to_o(self, file, binary, target, depancy):
		tmpList = target.GenerateFile(binary, self.name,self.originFolder,file,"obj")
		# check the dependency for this file :
		if False==dependency.NeedReBuild(tmpList[1], tmpList[0], tmpList[2]):
			return tmpList[1]
		buildTools.CreateDirectoryOfFile(tmpList[1])
		debug.printElement("c++", self.name, "<==", file)
		cmdLine=buildTools.ListToStr([
			target.xx,
			"-o", tmpList[1] ,
			buildTools.AddPrefix("-I",self.export_path),
			buildTools.AddPrefix("-I",self.local_path),
			buildTools.AddPrefix("-I",depancy.path),
			target.global_flags_cc,
			target.global_flags_xx,
			depancy.flags_cc,
			depancy.flags_xx,
			self.flags_cc,
			" -c -MMD -MP -g ",
			tmpList[0]])
		RunCommand(cmdLine)
		"""
		$(TARGET_CXX) \
		-o $@ \
		$(TARGET_GLOBAL_C_INCLUDES) \
		$(PRIVATE_C_INCLUDES) \
		$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
		$(TARGET_GLOBAL_CFLAGS) $(TARGET_GLOBAL_CPPFLAGS) $(CXX_FLAGS_WARNINGS) \
		$(PRIVATE_CFLAGS) $(PRIVATE_CPPFLAGS) \
		-D__EWOL_APPL_NAME__="$(PROJECT_NAME2)" \
		-c -MMD -MP -g \
		$(call path-from-top,$<)
		"""
		return tmpList[1]
	
	###############################################################################
	## Commands for running gcc to compile a C file.
	###############################################################################
	def Compile_cc_to_o(self, file, binary, target, depancy):
		tmpList = target.GenerateFile(binary,self.name,self.originFolder,file,"obj")
		# check the dependency for this file :
		if False==dependency.NeedReBuild(tmpList[1], tmpList[0], tmpList[2]):
			return tmpList[1]
		buildTools.CreateDirectoryOfFile(tmpList[1])
		debug.printElement("c", self.name, "<==", file)
		cmdLine=buildTools.ListToStr([
			target.cc,
			"-o", tmpList[1],
			buildTools.AddPrefix("-I",self.export_path),
			buildTools.AddPrefix("-I",self.local_path),
			buildTools.AddPrefix("-I",depancy.path),
			target.global_flags_cc,
			depancy.flags_cc,
			self.flags_cc,
			" -c -MMD -MP -g ",
			tmpList[0]])
		RunCommand(cmdLine)
		"""
		$(TARGET_CC) \
		-o $@ \
		$(TARGET_GLOBAL_C_INCLUDES) \
		$(PRIVATE_C_INCLUDES) \
		$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
		$(TARGET_GLOBAL_CFLAGS) $(CC_FLAGS_WARNINGS) \
		$(PRIVATE_CFLAGS) \
		-D__EWOL_APPL_NAME__="$(PROJECT_NAME2)" \
		-c -MMD -MP -g \
		$(call path-from-top,$<)
		"""
		return tmpList[1]
	
	
	###############################################################################
	## Commands for running ar.
	###############################################################################
	def Link_to_a(self, file, binary, target, depancy):
		tmpList = target.GenerateFile(binary, self.name,self.originFolder,file,"lib-static")
		# check the dependency for this file :
		if False==dependency.NeedRePackage(tmpList[1], tmpList[0], True) \
				and False==dependency.NeedRePackage(tmpList[1], depancy.src, False):
			return tmpList[1]
		buildTools.CreateDirectoryOfFile(tmpList[1])
		debug.printElement("StaticLib", self.name, "==>", tmpList[1])
		# explicitly remove the destination to prevent error ...
		if os.path.exists(tmpList[1]) and os.path.isfile(tmpList[1]):
			os.remove(tmpList[1])
		#$(Q)$(TARGET_AR) $(TARGET_GLOBAL_ARFLAGS) $(PRIVATE_ARFLAGS) $@ $(PRIVATE_ALL_OBJECTS)
		cmdLine=buildTools.ListToStr([
			target.ar,
			target.global_flags_ar,
			self.flags_ar,
			tmpList[1],
			tmpList[0],
			depancy.src])
		RunCommand(cmdLine)
		#$(Q)$(TARGET_RANLIB) $@
		cmdLine=buildTools.ListToStr([
			target.ranlib,
			tmpList[1] ])
		RunCommand(cmdLine)
		return tmpList[1]
	
	
	###############################################################################
	## Commands for running gcc to link a shared library.
	###############################################################################
	def Link_to_so(self, file, binary, target, depancy):
		tmpList = target.GenerateFile(binary, self.name,self.originFolder,file,"lib-shared")
		# check the dependency for this file :
		if False==dependency.NeedRePackage(tmpList[1], tmpList[0], True) \
				and False==dependency.NeedRePackage(tmpList[1], depancy.src, False):
			return tmpList[1]
		buildTools.CreateDirectoryOfFile(tmpList[1])
		debug.error("SharedLib")# + self.name + " ==> " + dst)
		#debug.printElement("SharedLib", self.name, "==>", tmpList[1])
		"""$(Q)$(TARGET_CXX) \
			-o $@ \
			$(TARGET_GLOBAL_LDFLAGS_SHARED) \
			-Wl,-Map -Wl,$(basename $@).map \
			-shared \
			-Wl,-soname -Wl,$(notdir $@) \
			-Wl,--no-undefined \
			$(PRIVATE_LDFLAGS) \
			$(PRIVATE_ALL_OBJECTS) \
			-Wl,--whole-archive \
			$(PRIVATE_ALL_WHOLE_STATIC_LIBRARIES) \
			-Wl,--no-whole-archive \
			-Wl,--as-needed \
			$(PRIVATE_ALL_STATIC_LIBRARIES) \
			$(PRIVATE_ALL_SHARED_LIBRARIES) \
			$(PRIVATE_LDLIBS) \
			$(TARGET_GLOBAL_LDLIBS_SHARED)
		"""
	
	
	###############################################################################
	## Commands for running gcc to link an executable.
	###############################################################################
	def Link_to_bin(self, file, binary, target, depancy):
		tmpList = target.GenerateFile(binary, self.name,self.originFolder,file,"bin")
		# check the dependency for this file :
		if False==dependency.NeedRePackage(tmpList[1], tmpList[0], True) \
				and False==dependency.NeedRePackage(tmpList[1], depancy.src, False):
			return tmpList[1]
		buildTools.CreateDirectoryOfFile(tmpList[1])
		debug.printElement("Executable", self.name, "==>", tmpList[1])
		#$(Q)$(TARGET_AR) $(TARGET_GLOBAL_ARFLAGS) $(PRIVATE_ARFLAGS) $@ $(PRIVATE_ALL_OBJECTS)
		cmdLine=buildTools.ListToStr([
			target.xx,
			"-o", tmpList[1],
			tmpList[0],
			depancy.src,
			self.flags_ld,
			depancy.flags_ld,
			target.global_flags_ld])
		RunCommand(cmdLine)
		"""
		$(TARGET_CXX) \
			-o $@ \
			$(TARGET_GLOBAL_LDFLAGS) \
			-Wl,-Map -Wl,$(basename $@).map \
			-Wl,-rpath-link=$(TARGET_OUT_STAGING)/lib \
			-Wl,-rpath-link=$(TARGET_OUT_STAGING)/usr/lib \
			$(PRIVATE_LDFLAGS) \
			$(PRIVATE_ALL_OBJECTS) \
			-Wl,--whole-archive \
			$(PRIVATE_ALL_WHOLE_STATIC_LIBRARIES) \
			-Wl,--no-whole-archive \
			-Wl,--as-needed \
			$(PRIVATE_ALL_STATIC_LIBRARIES) \
			$(PRIVATE_ALL_SHARED_LIBRARIES) \
			$(PRIVATE_LDLIBS) \
			$(TARGET_GLOBAL_LDLIBS)
		"""
		#$(call strip-executable)
	
	###############################################################################
	## Commands for copying files
	###############################################################################
	def files_to_staging(self, binaryName, target):
		baseFolder = target.GetStagingFolderData(binaryName)
		for element in self.files:
			debug.verbose("Might copy file : " + element[0] + " ==> " + element[1])
			buildTools.CopyFile(self.originFolder+"/"+element[0], baseFolder+"/"+element[1])
	
	###############################################################################
	## Commands for copying files
	###############################################################################
	def folders_to_staging(self, binaryName, target):
		baseFolder = target.GetStagingFolderData(binaryName)
		for element in self.folders:
			debug.verbose("Might copy folder : " + element[0] + "==>" + element[1])
			buildTools.CopyAnything(self.originFolder+"/"+element[0], baseFolder+"/"+element[1])
	
	# call here to build the module
	def Build(self, binaryName, target):
		# ckeck if not previously build
		if target.IsModuleBuild(self.name)==True:
			return self.localHeritage
		
		if binaryName==None \
				and self.type=='BINARY':
			# this is the endpoint binary ...
			binaryName = self.name
		else :
			# TODO : Set it better ...
			None
		
		# build dependency befor
		listSubFileNeededToBuild = []
		subHeritage = heritage.heritage(None)
		for dep in self.depends:
			inherit = Build(dep, binaryName, target)
			# add at the heritage list :
			subHeritage.AddSub(inherit)
		
		# build local sources
		for file in self.src:
			#debug.info(" " + self.name + " <== " + file);
			fileExt = file.split(".")[-1]
			if fileExt == "c" or fileExt == "C":
				resFile = self.Compile_cc_to_o(file, binaryName, target, subHeritage)
				listSubFileNeededToBuild.append(resFile)
			elif fileExt == "cpp" or fileExt == "CPP" or fileExt == "cxx" or fileExt == "CXX" or fileExt == "xx" or fileExt == "XX":
				resFile = self.Compile_xx_to_o(file, binaryName, target, subHeritage)
				listSubFileNeededToBuild.append(resFile)
			else:
				debug.verbose(" TODO : gcc " + self.originFolder + "/" + file)
		# generate end point:
		if self.type=='PREBUILD':
			# nothing to add ==> just dependence
			None
		elif self.type=='LIBRARY':
			resFile = self.Link_to_a(listSubFileNeededToBuild, binaryName, target, subHeritage)
			self.localHeritage.AddSources(resFile)
		elif self.type=='BINARY':
			resFile = self.Link_to_bin(listSubFileNeededToBuild, binaryName, target, subHeritage)
			# generate tree for this special binary
			self.BuildTree(target, self.name)
		else:
			debug.error("Dit not know the element type ... (impossible case) type=" + self.type)
			
		self.localHeritage.AddSub(subHeritage)
		# return local dependency ...
		return self.localHeritage
	
	# call here to build the module
	def BuildTree(self, target, binaryName):
		# ckeck if not previously build
		if target.IsModuleBuildTree(self.name)==True:
			return
		#build tree of all submodules
		for dep in self.depends:
			inherit = BuildTree(dep, target, binaryName)
		# add all the elements
		self.files_to_staging(binaryName, target)
		self.folders_to_staging(binaryName, target)
	
	
	# call here to Clean the module
	def Clean(self, target):
		if self.type=='PREBUILD':
			# nothing to add ==> just dependence
			None
		elif self.type=='LIBRARY':
			# remove folder of the lib ... for this targer
			folderBuild = target.GetBuildFolder(self.name)
			debug.info("remove folder : '" + folderBuild + "'")
			buildTools.RemoveFolderAndSubFolder(folderBuild)
		elif self.type=='BINARY':
			# remove folder of the lib ... for this targer
			folderBuild = target.GetBuildFolder(self.name)
			debug.info("remove folder : '" + folderBuild + "'")
			buildTools.RemoveFolderAndSubFolder(folderBuild)
			folderStaging = target.GetStagingFolder(self.name)
			debug.info("remove folder : '" + folderStaging + "'")
			buildTools.RemoveFolderAndSubFolder(folderStaging)
		else:
			debug.error("Dit not know the element type ... (impossible case) type=" + self.type)
	
	def AppendToInternalList(self, listout, list):
		if type(list) == type(str()):
			listout.append(list)
		else:
			# mulyiple imput in the list ...
			for elem in list:
				listout.append(elem)
	
	def AddModuleDepend(self, list):
		self.AppendToInternalList(self.depends, list)
	
	def AddExportPath(self, list):
		self.AppendToInternalList(self.export_path, list)
	
	def AddPath(self, list):
		self.AppendToInternalList(self.local_path, list)
	
	def AddExportflag_LD(self, list):
		self.AppendToInternalList(self.export_flags_ld, list)
	
	def AddExportFlag_CC(self, list):
		self.AppendToInternalList(self.export_flags_cc, list)
	
	def AddExportFlag_XX(self, list):
		self.AppendToInternalList(self.export_flags_xx, list)
	
	def AddExportFlag_M(self, list):
		self.AppendToInternalList(self.export_flags_m, list)
	
	def AddExportFlag_MM(self, list):
		self.AppendToInternalList(self.export_flags_mm, list)
	
	# add the link flag at the module
	def CompileFlags_LD(self, list):
		self.AppendToInternalList(self.flags_ld, list)
	
	def CompileFlags_CC(self, list):
		self.AppendToInternalList(self.flags_cc, list)
	
	def CompileFlags_XX(self, list):
		self.AppendToInternalList(self.flags_xx, list)
	
	def CompileFlags_M(self, list):
		self.AppendToInternalList(self.flags_m, list)
	
	def CompileFlags_MM(self, list):
		self.AppendToInternalList(self.flags_mm, list)
	
	def CompileFlags_S(self, list):
		self.AppendToInternalList(self.flags_s, list)
	
	def AddSrcFile(self, list):
		self.AppendToInternalList(self.src, list)
	
	def CopyFile(self, src, dst):
		self.files.append([src,dst])
	
	def CopyFolder(self, src, dst):
		self.folders.append([src,dst])
	
	def PrintList(self, description, list):
		if len(list) > 0:
			print '        %s' %description
			for elem in list:
				print '            %s' %elem
	
	def Display(self):
		print '-----------------------------------------------'
		print ' package : "%s"' %self.name
		print '-----------------------------------------------'
		print '    type:"%s"' %self.type
		print '    file:"%s"' %self.originFile
		print '    folder:"%s"' %self.originFolder
		self.PrintList('depends',self.depends)
		self.PrintList('flags_ld',self.flags_ld)
		self.PrintList('flags_cc',self.flags_cc)
		self.PrintList('flags_xx',self.flags_xx)
		self.PrintList('flags_m',self.flags_m)
		self.PrintList('flags_mm',self.flags_mm)
		self.PrintList('flags_s',self.flags_s)
		self.PrintList('src',self.src)
		self.PrintList('files',self.files)
		self.PrintList('folders',self.folders)
		self.PrintList('export_path',self.export_path)
		self.PrintList('export_flags_ld',self.export_flags_ld)
		self.PrintList('export_flags_cc',self.export_flags_cc)
		self.PrintList('export_flags_xx',self.export_flags_xx)
		self.PrintList('export_flags_m',self.export_flags_m)
		self.PrintList('export_flags_mm',self.export_flags_mm)
		self.PrintList('local_path',self.local_path)


# the list of all module is named : moduleList
moduleList = []

"""
	
"""
def AddModule(newModule):
	global moduleList
	for tmpMod in moduleList:
		if (tmpMod.name == newModule.name):
			debug.error("try to insert a secont time the same module name : " + newModule.name)
			return
	moduleList.append(newModule)
	# with "all" we just build the bianties and packages
	buildList.AddModule(newModule.name, newModule.type)

"""
	
"""
def Dump():
	print 'Dump all module properties'
	if 'moduleList' in globals():
		for mod in moduleList:
			mod.Display()
	else:
		print ' ==> no module added ...'



# return inherit packages ...
def Build(name, binName, target):
	for module in moduleList:
		if module.name == name:
			return module.Build(binName, target)
	debug.error("request to build an un-existant module name : '" + name + "'")

def BuildTree(name,target,binName):
	for module in moduleList:
		if module.name == name:
			module.BuildTree(target,binName)
			return
	debug.error("request to build tree on un-existant module name : '" + name + "'")


def Clean(name,target):
	for module in moduleList:
		if module.name == name:
			module.Clean(target)
			return
	debug.error("request to clean an un-existant module name : '" + name + "'")





def ImportPath(path):
	matches = []
	debug.debug('Start find sub File : "%s"' %path)
	for root, dirnames, filenames in os.walk(path):
		tmpList = fnmatch.filter(filenames, 'Makefile_*.py')
		# Import the module :
		for filename in tmpList:
			debug.debug('    Find a file : "%s"' %os.path.join(root, filename))
			#matches.append(os.path.join(root, filename))
			sys.path.append(os.path.dirname(os.path.join(root, filename)) )
			moduleName = filename.replace('.py', '')
			debug.debug('try load : %s' %moduleName)
			__import__(moduleName)
			# note : Better to do a module system ==> proper ...





