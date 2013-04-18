#!/usr/bin/python
import debug
import datetime
import buildTools
import environement

class Target:
	def __init__(self):
		self.name='Linux'
		debug.info("create board target : "+self.name);
		if 1==environement.GetClangMode():
			self.cc='clang'
			self.xx='clang++'
		else:
			self.cc='gcc'
			self.xx='g++'
		self.ar='ar'
		self.ld='ld'
		self.nm='nm'
		self.strip='strip'
		self.ranlib='ranlib'
		self.dlltool='dlltool'
		###############################################################################
		# Target global variables.
		###############################################################################
		self.global_include_cc=''
		self.global_flags_cc=['-D__TARGET_OS__Linux', "-DBUILD_TIME=\"\\\""+str(datetime.datetime.now())+"\\\"\""]
		self.global_flags_xx=''
		self.global_flags_mm=''
		self.global_flags_m=''
		self.global_flags_ar='rcs'
		self.global_flags_ld=''
		self.global_flags_ld_shared=''
		self.global_libs_ld=''
		self.global_libs_ld_shared=''
		
		self.suffix_dependence='.o'
		self.suffix_obj='.o'
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.so'
		self.suffix_binary=''
		self.suffix_package='.deb'
		
		self.folder_arch="/" + self.name
		
		if 1==environement.GetDebugMode():
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
	
	"""
		return a list of 3 elements :
			0 : sources files (can be a list)
			1 : destination file
			2 : dependence files module (*.d)
	"""
	def GenerateFile(self,moduleName,basePath,file,type):
		list=[]
		if (type=="bin"):
			list.append(file)
			list.append(buildTools.GetRunFolder() + self.folder_out + self.folder_staging + self.folder_bin + "/" + moduleName + self.suffix_binary)
			list.append(buildTools.GetRunFolder() + self.folder_out + self.folder_build + "/" + moduleName + "/" + moduleName + self.suffix_dependence)
		elif (type=="obj"):
			list.append(basePath + "/" + file)
			list.append(buildTools.GetRunFolder() + self.folder_out + self.folder_build + "/" + moduleName + "/" + file + self.suffix_obj)
			list.append(buildTools.GetRunFolder() + self.folder_out + self.folder_build + "/" + moduleName + "/" + file + self.suffix_dependence)
		elif (type=="lib-shared"):
			list.append(file)
			list.append(buildTools.GetRunFolder() + self.folder_out + self.folder_staging + self.folder_lib + "/" + moduleName + self.suffix_lib_dynamic)
			list.append(buildTools.GetRunFolder() + self.folder_out + self.folder_build + "/" + moduleName + "/" + moduleName + self.suffix_dependence)
		elif (type=="lib-static"):
			list.append(file)
			list.append(buildTools.GetRunFolder() + self.folder_out + self.folder_build + "/" + moduleName + "/" + moduleName + self.suffix_lib_static)
			list.append(buildTools.GetRunFolder() + self.folder_out + self.folder_build + "/" + moduleName + "/" + moduleName + self.suffix_dependence)
		else:
			debug.error("unknow type : " + type)
		return list
	
	def GetStagingFolder(self, moduleName):
		return buildTools.GetRunFolder() + self.folder_out + self.folder_staging + self.folder_data + "/" + moduleName
	
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
	
	

"""
TARGET_GLOBAL_LDFLAGS = "-L$(TARGET_OUT_STAGING)/lib
TARGET_GLOBAL_LDFLAGS += -L$(TARGET_OUT_STAGING)/usr/lib
TARGET_GLOBAL_LDFLAGS_SHARED += -L$(TARGET_OUT_STAGING)/lib
TARGET_GLOBAL_LDFLAGS_SHARED += -L$(TARGET_OUT_STAGING)/usr/lib
"""