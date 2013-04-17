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
import target_Linux


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
		# sources list:
		self.src=[]
		# copy files and folders:
		self.files=[]
		self.folders=[]
		self.isBuild=False
		## end of basic INIT ...
		if moduleType == 'BINARY' \
				or moduleType == 'LIBRARY' \
				or moduleType == 'PACKAGE':
			self.type=moduleType
		else :
			debug.error('for module "%s"' %moduleName)
			debug.error('    ==> error : "%s" ' %moduleType)
			raise 'Input value error'
		self.originFile = file;
		self.originFolder = buildTools.GetCurrentPath(self.originFile)
		self.name=moduleName
	
	###############################################################################
	## Commands for running gcc to compile a m++ file.
	###############################################################################
	def Compile_mm_to_o(self, src, dst):
		buildTools.CreateDirectoryOfFile(dst)
		debug.info("m++: " + self.name + " <== " + src)
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
	###############################################################################
	## Commands for running gcc to compile a m file.
	###############################################################################
	def Compile_m_to_o(self, src, dst):
		buildTools.CreateDirectoryOfFile(dst)
		debug.info("m: " + self.name + " <== " + src)
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
	
	###############################################################################
	## Commands for running gcc to compile a C++ file.
	###############################################################################
	def Compile_xx_to_o(self, src, dst):
		buildTools.CreateDirectoryOfFile(dst)
		debug.info("c++: " + self.name + " <== " + src)
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
	
	###############################################################################
	## Commands for running gcc to compile a C file.
	###############################################################################
	
	def Compile_cc_to_o(self, src, dst):
		buildTools.CreateDirectoryOfFile(dst)
		debug.info("c: " + self.name + " <== " + src)
		cmdLine=buildTools.ListToStr([
			target_Linux.TARGET_CC,
			"-o", dst ,
			buildTools.AddPrefix("-I",self.export_path),
			buildTools.AddPrefix("-I",self.local_path),
			self.flags_cc,
			" -c -MMD -MP -g ",
			src])
		debug.debug(cmdLine)
		ret = os.system(cmdLine)
		print "result val = " + str(ret)
		if ret != 0:
			debug.error("can not compile file : " + src)
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
	
	
	###############################################################################
	## Commands for running ar.
	###############################################################################
	
	def Link_to_a(self, src, dst):
		buildTools.CreateDirectoryOfFile(dst)
		debug.info("StaticLib: " + self.name + " ==> " + dst)
		# explicitly remove the destination to prevent error ...
		os.remove(dst)
		#$(Q)$(TARGET_AR) $(TARGET_GLOBAL_ARFLAGS) $(PRIVATE_ARFLAGS) $@ $(PRIVATE_ALL_OBJECTS)
		#$(Q)$(TARGET_RANLIB) $@
	
	
	###############################################################################
	## Commands for running gcc to link a shared library.
	###############################################################################
	
	def Link_to_so(self, src, dst):
		buildTools.CreateDirectoryOfFile(dst)
		debug.info("SharedLib: " + self.name + " ==> " + dst)
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
	def Link_to_bin(self, src, dst):
		buildTools.CreateDirectoryOfFile(dst)
		debug.info("Executable: " + self.name + " ==> " + dst)
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
	

	# call here to build the module
	def Build(self):
		# ckeck if not previously build
		if self.isBuild==True:
			return
		# build dependency befor
		for dep in self.depends:
			Build(dep)
		# build local sources
		for file in self.src:
			debug.info(" " + self.name + " <== " + file);
			fileExt = file.split(".")[-1]
			if fileExt == "c" or fileExt == "C":
				source = self.originFolder + "/" + file
				destination = buildTools.GetRunFolder() + "/out/test/build/" + file + ".o"
				print source
				print destination
				self.Compile_cc_to_o(source, destination)
			else:
				debug.verbose(" TODO : gcc " + self.originFolder + "/" + file)
		# generate end point:
		if self.type=='LIBRARY':
			debug.info("(lib) " + self.name + ".a <== *.o");
		else:
			debug.info("(bin) " + self.name + ".a <== *.o");
		#build ended ...
		self.isBuild=True
	
	# call here to Clean the module
	def Clean(self):
		for file in self.src:
			debug.info(" " + self.name + " <- (X) " + file);
	
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
	buildList.AddModule(newModule.name)

"""
	
"""
def Dump():
	print 'Dump all module properties'
	if 'moduleList' in globals():
		for mod in moduleList:
			mod.Display()
	else:
		print ' ==> no module added ...'



def Build(name):
	for module in moduleList:
		if module.name == name:
			module.Build()
			return
	debug.error("request to build un-existant module name : '" + name + "'")


def Clean(name):
	for module in moduleList:
		if module.name == name:
			module.Clean()
			return
	debug.error("request to build un-existant module name : '" + name + "'")





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





