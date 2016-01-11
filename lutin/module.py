#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import sys
import os
import inspect
import fnmatch
# Local import
from . import host
from . import tools
from . import debug
from . import heritage
from . import builder
from . import multiprocess
from . import image
from . import license

class Module:
	
	##
	## @brief Module class represent all system needed for a specific
	## 	module like 
	## 		- type (bin/lib ...)
	## 		- dependency
	## 		- flags
	## 		- files
	## 		- ...
	##
	def __init__(self, file, module_name, moduleType):
		## Remove all variable to prevent error of multiple deffinition of the module ...
		debug.verbose("Create a new module : '" + module_name + "' TYPE=" + moduleType)
		self.origin_file=''
		self.origin_path=''
		# type of the module:
		self.type='LIBRARY'
		# Name of the module
		self.name=module_name
		# Dependency list:
		self.depends = []
		# Dependency list (optionnal module):
		self.depends_optionnal = []
		self.depends_find = []
		# Documentation list:
		self.documentation = None
		# export PATH
		self.path = {"export":{},
		             "local":{}
		            }
		self.flags = {"export":{},
		              "local":{}
		             }
		self.extention_order_build = ["java", "javah"] # all is not set here is done in the provided order ...
		# sources list:
		self.src = []
		self.header = []
		# copy files and paths:
		self.image_to_copy = []
		self.files = []
		self.paths = []
		# The module has been already build ...
		self.isbuild = False
		## end of basic INIT ...
		if    moduleType == 'BINARY' \
		   or moduleType == 'BINARY_SHARED' \
		   or moduleType == 'BINARY_STAND_ALONE' \
		   or moduleType == 'LIBRARY' \
		   or moduleType == 'LIBRARY_DYNAMIC' \
		   or moduleType == 'LIBRARY_STATIC' \
		   or moduleType == 'PACKAGE' \
		   or moduleType == 'PREBUILD':
			self.type=moduleType
		else :
			debug.error('for module "%s"' %module_name)
			debug.error('    ==> error : "%s" ' %moduleType)
			raise 'Input value error'
		self.origin_file = file;
		self.origin_path = tools.get_current_path(self.origin_file)
		self.local_heritage = heritage.heritage(self, None)
		# TODO : Do a better dynamic property system => not really versatil
		self.package_prop = { "COMPAGNY_TYPE" : "",
		                      "COMPAGNY_NAME" : "",
		                      "COMPAGNY_NAME2" : "",
		                      "MAINTAINER" : [],
		                      #"ICON" : set(""),
		                      "SECTION" : [],
		                      "PRIORITY" : "",
		                      "DESCRIPTION" : "",
		                      "VERSION" : [0,0,0],
		                      "VERSION_CODE" : "",
		                      "NAME" : "no-name", # name of the application
		                      "ANDROID_MANIFEST" : "", # By default generate the manifest
		                      "ANDROID_RESOURCES" : [],
		                      "ANDROID_APPL_TYPE" : "APPL", # the other mode is "WALLPAPER" ... and later "WIDGET"
		                      "ANDROID_WALLPAPER_PROPERTIES" : [], # To create properties of the wallpaper (no use of EWOL display)
		                      "RIGHT" : [],
		                      "LICENSE" : "", # by default: no license
		                      "ADMOD_POSITION" : "top"
		                     }
		self.package_prop_default = { "COMPAGNY_TYPE" : True,
		                              "COMPAGNY_NAME" : True,
		                              "COMPAGNY_NAME2" : True,
		                              "MAINTAINER" : True,
		                              #"ICON" : True,
		                              "SECTION" : True,
		                              "PRIORITY" : True,
		                              "DESCRIPTION" : True,
		                              "VERSION" : True,
		                              "VERSION_CODE" : True,
		                              "NAME" : True,
		                              "ANDROID_MANIFEST" : True,
		                              "ANDROID_RESOURCES" : True,
		                              "ANDROID_APPL_TYPE" : True,
		                              "ANDROID_WALLPAPER_PROPERTIES" : True,
		                              "RIGHT" : True,
		                              "LICENSE" : True,
		                              "ADMOD_POSITION" : True
		                            }
		self.sub_heritage_list = None
	
	def get_type(self):
		return self.type
	##
	## @brief add Some copilation flags for this module (and only this one)
	##
	def add_extra_compile_flags(self):
		self.compile_flags('c', [
			"-Wall",
			"-Wsign-compare",
			"-Wreturn-type",
			#"-Wint-to-pointer-cast",
			"-Wno-write-strings",
			"-Wno-unused-variable"]);
		self.compile_flags('c++', [
			"-Woverloaded-virtual",
			"-Wnon-virtual-dtor"]);
		#only for gcc : "-Wunused-variable", "-Wunused-but-set-variable",
	
	##
	## @brief remove all unneeded warning on compilation ==> for extern libs ...
	##
	def remove_compile_warning(self):
		self.compile_flags('c', [
			"-Wno-int-to-pointer-cast"
			]);
		self.compile_flags('c++', [
			"-Wno-c++11-narrowing"
			])
		# only for gcc :"-Wno-unused-but-set-variable"
	
	##
	## @brief Send image in the build data directory
	## @param[in] target Target object
	##
	def image_to_build(self, target):
		for source, destination, sizeX, sizeY in self.image_to_copy:
			extension = source[source.rfind('.'):]
			if     extension != ".png" \
			   and extension != ".jpg" \
			   and sizeX > 0:
				debug.error("Can not manage image other than .png and jpg to resize : " + source);
			display_source = source
			source = self.origin_path + "/" + source
			if destination == "":
				destination = source[source.rfind('/')+1:]
				debug.verbose("Regenerate Destination : '" + destination + "'")
			# TODO : set it back : file_cmd = target.get_build_path_data(self.name)
			file_cmd = ""
			if sizeX > 0:
				debug.verbose("Image file : " + display_source + " ==> " + destination + " resize=(" + str(sizeX) + "," + str(sizeY) + ")")
				fileName, fileExtension = os.path.splitext(os.path.join(self.origin_path,source))
				image.resize(source, os.path.join(target.get_build_path_data(self.name), destination), sizeX, sizeY, file_cmd)
			else:
				debug.verbose("Might copy file : " + display_source + " ==> " + destination)
				tools.copy_file(source, os.path.join(target.get_build_path_data(self.name), destination), file_cmd)
	
	##
	## @brief Send files in the build data directory
	## @param[in] target Target object
	##
	def files_to_build(self, target):
		for source, destination in self.files:
			display_source = source
			source = os.path.join(self.origin_path, source)
			if destination == "":
				destination = source[source.rfind('/')+1:]
				debug.verbose("Regenerate Destination : '" + destination + "'")
			# TODO : set it back : file_cmd = target.get_build_path_data(self.name)
			file_cmd = ""
			debug.verbose("Might copy file : " + display_source + " ==> " + destination)
			tools.copy_file(source, os.path.join(target.get_build_path_data(self.name), destination), file_cmd)
	
	##
	## @brief Send compleate folder in the build data directory
	## @param[in] target Target object
	##
	def paths_to_build(self, target):
		for source, destination in self.paths:
			debug.debug("Might copy path : " + source + "==>" + destination)
			tmp_path = os.path.dirname(os.path.realpath(os.path.join(self.origin_path, source)))
			tmp_rule = os.path.basename(source)
			for root, dirnames, filenames in os.walk(tmp_path):
				debug.extreme_verbose(" root='" + str(root) + "' tmp_path='" + str(tmp_path))
				if root != tmp_path:
					break
				debug.verbose(" root='" + str(root) + "' dir='" + str(dirnames) + "' filenames=" + str(filenames))
				list_files = filenames
				if len(tmp_rule)>0:
					list_files = fnmatch.filter(filenames, tmp_rule)
				debug.verbose("       filenames=" + str(filenames))
				# Import the module :
				for cycle_file in list_files:
					#for cycle_file in filenames:
					new_destination = destination
					# TODO : maybe an error when changing subdirectory ...
					#if root[len(source)-1:] != "":
					#	new_destination = os.path.join(new_destination, root[len(source)-1:])
					debug.verbose("Might copy : '" + os.path.join(root, cycle_file) + "' ==> '" + os.path.join(target.get_build_path_data(self.name), new_destination, cycle_file) + "'" )
					file_cmd = "" # TODO : ...
					tools.copy_file(os.path.join(root, cycle_file), os.path.join(target.get_build_path_data(self.name), new_destination, cycle_file), file_cmd)
	
	
	
	def gcov(self, target, generate_output=False):
		if self.type == 'PREBUILD':
			debug.error("Can not generate gcov on prebuid system ... : '" + self.name + "'");
			return
		# remove uncompilable elements:
		list_file = tools.filter_extention(self.src, self.extention_order_build, True)
		global_list_file = ""
		for file in list_file:
			debug.verbose(" gcov : " + self.name + " <== " + file);
			file_dst = target.get_full_name_destination(self.name, self.origin_path, file, "o")
			global_list_file += file_dst + " "
		cmd = "gcov"
		# specify the version of gcov we need to use
		if target.config["compilator-version"] != "":
			cmd += "-" + target.config["compilator-version"] + " "
		cmd += " --branch-counts --preserve-paths "
		if generate_output == False:
			cmd += "--no-output "
		cmd += global_list_file
		debug.extreme_verbose("      " + cmd);
		ret = multiprocess.run_command_direct(cmd)
		# parsing ret :
		debug.extreme_verbose("result: " + str(ret));
		ret = ret.split('\n');
		debug.verbose("*** Gcov result parsing ...");
		useful_list = []
		remove_next = False
		last_file = ""
		executed_lines = 0
		executable_lines = 0
		for elem in ret:
			if remove_next == True:
				remove_next = False
				continue;
			if    elem[:10] == "Creating '" \
			   or elem[:10] == "Removing '":
				remove_next = True
				continue
			if     elem[:6] == "File '" \
			   and self.origin_path != elem[6:len(self.origin_path)+6]:
				remove_next = True
				continue
			if elem[:6] == "File '":
				last_file = elem[6+len(self.origin_path)+1:-1]
				continue
			start_with = "Lines executed:"
			if elem[:len(start_with)] != start_with:
				debug.warning("    gcov ret : " + str(elem));
				debug.warning("         ==> does not start with : " + start_with);
				debug.warning("         Parsing error");
				continue
			out = elem[len(start_with):].split("% of ")
			if len(out) != 2:
				debug.warning("    gcov ret : " + str(elem));
				debug.warning("         Parsing error of '% of '");
				continue
			pourcent = float(out[0])
			total_line_count = int(out[1])
			total_executed_line = int(float(total_line_count)*pourcent/100.0)
			useful_list.append([last_file, pourcent, total_executed_line, total_line_count])
			executed_lines += total_executed_line
			executable_lines += total_line_count
			last_file = ""
		ret = useful_list[:-1]
		#for elem in ret:
		#	debug.info("    " + str(elem));
		for elem in ret:
			if elem[1]<10.0:
				debug.info("   %   " + str(elem[1]) + "\r\t\t" + str(elem[0]));
			elif elem[1]<100.0:
				debug.info("   %  " + str(elem[1]) + "\r\t\t" + str(elem[0]));
			else:
				debug.info("   % " + str(elem[1]) + "\r\t\t" + str(elem[0]));
		pourcent = 100.0*float(executed_lines)/float(executable_lines)
		# generate json file:
		json_file_name = target.get_build_path(self.name) + "/" + self.name + "_coverage.json"
		debug.debug("generate json file : " + json_file_name)
		tmp_file = open(json_file_name, 'w')
		tmp_file.write('{\n')
		tmp_file.write('	"lib-name":"' + self.name + '",\n')
		#tmp_file.write('	"coverage":"' + str(pourcent) + '",\n')
		tmp_file.write('	"executed":"' + str(executed_lines) + '",\n')
		tmp_file.write('	"executable":"' + str(executable_lines) + '",\n')
		tmp_file.write('	"list":[\n')
		val = 0
		for elem in ret:
			if val == 0 :
				tmp_file.write('		{\n')
			else:
				tmp_file.write('		}, {\n')
			val += 1
			tmp_file.write('			"file":"' + elem[0] + '",\n')
			tmp_file.write('			"executed":' + str(elem[2]) + ',\n')
			tmp_file.write('			"executable":' + str(elem[3]) + '\n')
		tmp_file.write('		}\n')
		tmp_file.write('	]\n')
		tmp_file.write('}\n')
		tmp_file.flush()
		tmp_file.close()
		# print debug:
		debug.print_element("coverage", self.name, ":", str(pourcent) + "%  " + str(executed_lines) + "/" + str(executable_lines))
	
	# call here to build the module
	def build(self, target, package_name):
		# ckeck if not previously build
		if target.is_module_build(self.name)==True:
			if self.sub_heritage_list == None:
				self.local_heritage = heritage.heritage(self, target)
			return self.sub_heritage_list
		# create the package heritage
		self.local_heritage = heritage.heritage(self, target)
		
		if     package_name==None \
		   and (    self.type == 'BINARY'
		         or self.type == 'BINARY_SHARED' \
		         or self.type == 'BINARY_STAND_ALONE' \
		         or self.type == 'PACKAGE' ) :
			# this is the endpoint binary ...
			package_name = self.name
		else:
			pass
		# build dependency before
		list_sub_file_needed_to_build = []
		self.sub_heritage_list = heritage.HeritageList()
		# optionnal dependency :
		for dep, option, export in self.depends_optionnal:
			inherit_list, isBuilt = target.build(dep, package_name, True)
			if isBuilt == True:
				self.local_heritage.add_depends(dep);
				# TODO : Add optionnal Flags ...
				#     ==> do it really better ...
				if export == False:
					self.compile_flags(option[0], option[1]);
				else:
					self.add_export_flag(option[0], option[1]);
			# add at the heritage list :
			self.sub_heritage_list.add_heritage_list(inherit_list)
		for dep in self.depends:
			debug.debug("module: '" + str(self.name) + "'   request: '" + dep + "'")
			inherit_list = target.build(dep, package_name, False)
			# add at the heritage list :
			self.sub_heritage_list.add_heritage_list(inherit_list)
		# do sub library action for automatic generating ...
		local_type = self.type
		if self.type == 'LIBRARY_DYNAMIC':
			local_type = 'LIBRARY'
		if self.type == 'LIBRARY_STATIC':
			local_type = 'LIBRARY'
		if self.type == 'BINARY_SHARED':
			local_type = 'BINARY'
		if self.type == 'BINARY_STAND_ALONE':
			local_type = 'BINARY'
		if local_type in target.action_on_state:
			for lvl in range(0,100):
				for level, action_name, action in target.action_on_state[local_type]:
					if level == lvl:
						debug.debug("level=" + str(level) + " Do Action : " + action_name)
						elem = action(target, self, package_name);
		# ----------------------------------------------------
		# -- Generic library help                           --
		# ----------------------------------------------------
		package_version_string = tools.version_to_string(self.package_prop["VERSION"]);
		if self.type == 'PREBUILD':
			debug.print_element("Prebuild", self.name, "-", package_version_string)
		elif self.type == 'LIBRARY':
			debug.print_element("Library", self.name, "-", package_version_string)
		elif self.type == 'LIBRARY_DYNAMIC':
			debug.print_element("Library(dynamic)", self.name, "-", package_version_string)
		elif self.type == 'LIBRARY_STATIC':
			debug.print_element("Library(static)", self.name, "-", package_version_string)
		elif self.type == 'BINARY':
			debug.print_element("Binary(auto)", self.name, "-", package_version_string)
		elif self.type == 'BINARY_SHARED':
			debug.print_element("Binary (shared)", self.name, "-", package_version_string)
		elif self.type == 'BINARY_STAND_ALONE':
			debug.print_element("Binary (stand alone)", self.name, "-", package_version_string)
		elif self.type == 'PACKAGE':
			debug.print_element("Package", self.name, "-", package_version_string)
		# ----------------------------------------------------
		# -- Sources compilation                            --
		# ----------------------------------------------------
		if self.type != 'PREBUILD':
			# build local sources in a specific order:
			for extention_local in self.extention_order_build:
				list_file = tools.filter_extention(self.src, [extention_local])
				for file in list_file:
					#debug.info(" " + self.name + " <== " + file);
					fileExt = file.split(".")[-1]
					try:
						tmp_builder = builder.get_builder(fileExt);
						res_file = tmp_builder.compile(file,
						                               package_name,
						                               target,
						                               self.sub_heritage_list,
						                               flags = self.flags,
						                               path = self.path,
						                               name = self.name,
						                               basic_path = self.origin_path,
						                               module_src = self.src)
						if res_file["action"] == "add":
							list_sub_file_needed_to_build.append(res_file["file"])
						elif res_file["action"] == "path":
							self.add_path(res_file["path"], type='c')
						else:
							debug.error("an not do action for : " + str(res_file))
					except ValueError:
						debug.warning(" UN-SUPPORTED file format:  '" + self.origin_path + "/" + file + "'")
			# now build the other :
			list_file = tools.filter_extention(self.src, self.extention_order_build, invert=True)
			for file in list_file:
				#debug.info(" " + self.name + " <== " + file);
				fileExt = file.split(".")[-1]
				try:
					tmp_builder = builder.get_builder(fileExt);
					res_file = tmp_builder.compile(file,
					                               package_name,
					                               target,
					                               self.sub_heritage_list,
					                               flags = self.flags,
					                               path = self.path,
					                               name = self.name,
					                               basic_path = self.origin_path,
					                               module_src = self.src)
					if res_file["action"] == "add":
						list_sub_file_needed_to_build.append(res_file["file"])
					elif res_file["action"] == "path":
						self.add_path(res_file["path"], type='c')
					else:
						debug.error("an not do action for : " + str(res_file))
				except ValueError:
					debug.warning(" UN-SUPPORTED file format:  '" + self.origin_path + "/" + file + "'")
			# when multiprocess availlable, we need to synchronize here ...
			multiprocess.pool_synchrosize()
		# ----------------------------------------------------
		# -- Generation point                               --
		# ----------------------------------------------------
		if self.type=='PREBUILD':
			self.local_heritage.add_sources(self.src)
		elif    self.type == 'LIBRARY' \
		     or self.type == 'LIBRARY_DYNAMIC' \
		     or self.type == 'LIBRARY_STATIC':
			res_file_out = []
			if    self.type == 'LIBRARY' \
			   or self.type == 'LIBRARY_STATIC':
				try:
					tmp_builder = builder.get_builder_with_output("a");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					if len(list_file) > 0:
						res_file = tmp_builder.link(list_file,
						                            package_name,
						                            target,
						                            self.sub_heritage_list,
						                            flags = self.flags,
						                            name = self.name,
						                            basic_path = self.origin_path)
						self.local_heritage.add_lib_static(res_file)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.a'")
			if target.support_dynamic_link == True:
				if    self.type == 'LIBRARY' \
				   or self.type == 'LIBRARY_DYNAMIC':
					try:
						tmp_builder = builder.get_builder_with_output("so");
						list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
						if len(list_file) > 0:
							res_file = tmp_builder.link(list_file,
							                            package_name,
							                            target,
							                            self.sub_heritage_list,
							                            flags = self.flags,
							                            name = self.name,
							                            basic_path = self.origin_path)
							self.local_heritage.add_lib_dynamic(res_file)
					except ValueError:
						debug.error(" UN-SUPPORTED link format:  '.so'/'.dynlib'/'.dll'")
			try:
				tmp_builder = builder.get_builder_with_output("jar");
				list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
				if len(list_file) > 0:
					res_file = tmp_builder.link(list_file,
					                            package_name,
					                            target,
					                            self.sub_heritage_list,
					                            flags = self.flags,
					                            name = self.name,
					                            basic_path = self.origin_path)
					self.local_heritage.add_lib_interpreted('java', res_file)
			except ValueError:
				debug.error(" UN-SUPPORTED link format:  '.jar'")
		elif    self.type == 'BINARY' \
		     or self.type == 'BINARY_SHARED' \
		     or self.type == 'BINARY_STAND_ALONE':
			shared_mode = False
			if target.name == "Android":
				debug.warning("Android mode ...")
				# special case for android ...
				for elem in self.sub_heritage_list.src['src']:
					debug.warning("    " + elem[-4:])
					if elem[-4:] == '.jar':
						# abstract GUI interface ...
						shared_mode = True
						break;
			static_mode = True
			if target.support_dynamic_link == True:
				if self.type == 'BINARY_SHARED':
					static_mode = False
			if shared_mode == True:
				try:
					tmp_builder = builder.get_builder_with_output("so");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					res_file = tmp_builder.link(list_file,
					                            package_name,
					                            target,
					                            self.sub_heritage_list,
					                            flags = self.flags,
					                            name = self.name,
					                            basic_path = self.origin_path,
					                            static = static_mode)
					self.local_heritage.add_sources(res_file)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.so'")
				try:
					tmp_builder = builder.get_builder_with_output("jar");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					if len(list_file) > 0:
						res_file = tmp_builder.link(list_file,
						                            package_name,
						                            target,
						                            self.sub_heritage_list,
						                            flags = self.flags,
						                            name = self.name,
						                            basic_path = self.origin_path)
						self.local_heritage.add_sources(res_file)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.jar'")
			else:
				try:
					tmp_builder = builder.get_builder_with_output("bin");
					res_file = tmp_builder.link(list_sub_file_needed_to_build,
					                            package_name,
					                            target,
					                            self.sub_heritage_list,
					                            flags = self.flags,
					                            name = self.name,
					                            basic_path = self.origin_path,
					                            static = static_mode)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.bin'")
		elif self.type == "PACKAGE":
			if target.name == "Android":
				# special case for android wrapper:
				try:
					tmp_builder = builder.get_builder_with_output("so");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					res_file = tmp_builder.link(list_file,
					                            package_name,
					                            target,
					                            self.sub_heritage_list,
					                            flags = self.flags,
					                            name = "lib" + self.name,
					                            basic_path = self.origin_path)
					self.local_heritage.add_sources(res_file)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.so'")
				try:
					tmp_builder = builder.get_builder_with_output("jar");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					if len(list_file) > 0:
						res_file = tmp_builder.link(list_file,
						                            package_name,
						                            target,
						                            self.sub_heritage_list,
						                            flags = self.flags,
						                            name = self.name,
						                            basic_path = self.origin_path)
						self.local_heritage.add_sources(res_file)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.jar'")
			else:
				try:
					tmp_builder = builder.get_builder_with_output("bin");
					res_file = tmp_builder.link(list_sub_file_needed_to_build,
					                            package_name,
					                            target,
					                            self.sub_heritage_list,
					                            flags = self.flags,
					                            name = self.name,
					                            basic_path = self.origin_path)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  'binary'")
		else:
			debug.error("Did not known the element type ... (impossible case) type=" + self.type)
		
		# ----------------------------------------------------
		# -- install header                                 --
		# ----------------------------------------------------
		debug.debug("install headers ...")
		copy_list={}
		include_path = target.get_build_path_include(self.name)
		for file in self.header:
			src_path = os.path.join(self.origin_path, file["src"])
			if "multi-dst" in file:
				dst_path = os.path.join(include_path, file["multi-dst"])
				tools.copy_anything(src_path,
				                    dst_path,
				                    recursive=False,
				                    force_identical=True,
				                    in_list=copy_list)
			else:
				dst_path = os.path.join(include_path, file["dst"])
				tools.copy_file(src_path,
				                dst_path,
				                force_identical=True,
				                in_list=copy_list)
		#real copy files
		tools.copy_list(copy_list)
		# remove unneded files (NOT folder ...)
		tools.clean_directory(include_path, copy_list)
		
		# ----------------------------------------------------
		# -- install data                                   --
		# ----------------------------------------------------
		debug.debug("install datas")
		self.image_to_build(target)
		self.files_to_build(target)
		self.paths_to_build(target)
		# TODO : do sothing that create a list of file set in this directory and remove it if necessary ... ==> if not needed anymore ...
		
		# create local heritage specification
		self.local_heritage.auto_add_build_header()
		self.sub_heritage_list.add_heritage(self.local_heritage)
		
		# ----------------------------------------------------
		# -- create package                                 --
		# ----------------------------------------------------
		if    self.type[:6] == 'BINARY' \
		   or self.type == 'PACKAGE':
			if target.end_generate_package == True:
				# generate the package with his properties ...
				if target.name=="Android":
					self.sub_heritage_list.add_heritage(self.local_heritage)
					target.make_package(self.name, self.package_prop, os.path.join(self.origin_path, ".."), self.sub_heritage_list)
				else:
					target.make_package(self.name, self.package_prop, os.path.join(self.origin_path, ".."), self.sub_heritage_list)
		
		# return local dependency ...
		return self.sub_heritage_list
	
	# call here to clean the module
	def clean(self, target):
		if self.type=='PREBUILD':
			# nothing to add ==> just dependence
			None
		elif    self.type=='LIBRARY' \
		     or self.type=='LIBRARY_DYNAMIC' \
		     or self.type=='LIBRARY_STATIC':
			# remove path of the lib ... for this targer
			pathbuild = target.get_build_path(self.name)
			debug.info("remove path : '" + pathbuild + "'")
			tools.remove_path_and_sub_path(pathbuild)
		elif    self.type=='BINARY' \
		     or self.type=='PACKAGE':
			# remove path of the lib ... for this targer
			pathbuild = target.get_build_path(self.name)
			debug.info("remove path : '" + pathbuild + "'")
			tools.remove_path_and_sub_path(pathbuild)
			pathStaging = target.get_staging_path(self.name)
			debug.info("remove path : '" + pathStaging + "'")
			tools.remove_path_and_sub_path(pathStaging)
		else:
			debug.error("Dit not know the element type ... (impossible case) type=" + self.type)
	
	def add_module_depend(self, list):
		tools.list_append_to(self.depends, list, True)
	
	def add_optionnal_module_depend(self, module_name, compilation_flags=["", ""], export=False):
		tools.list_append_and_check(self.depends_optionnal, [module_name, compilation_flags, export], True)
	
	def add_path(self, list, type='c'):
		tools.list_append_to_2(self.path["local"], type, list)
	
	def add_export_flag(self, type, list):
		tools.list_append_to_2(self.flags["export"], type, list)
	
	# add the link flag at the module
	# TODO : Rename this in add_flag
	def compile_flags(self, type, list):
		tools.list_append_to_2(self.flags["local"], type, list)
	
	def compile_version(self, compilator_type, version, same_as_api=True, gnu=False):
		if    compilator_type == "c++" \
		   or compilator_type == "C++":
			cpp_version_list = [1999, 2003, 2011, 2014, 2017]
			if version not in cpp_version_list:
				debug.error("can not select CPP version : " + str(version) + " not in " + str(cpp_version_list))
			# select API version:
			api_version = 1999
			if same_as_api == True:
				api_version = version
			self.flags["local"]["c++-version"] = { "version":version,
			                                       "gnu":gnu
			                                     }
			self.flags["export"]["c++-version"] = api_version
			if gnu == True and same_as_api == True:
				debug.warning("Can not propagate the gnu extention of the CPP vesion for API");
		elif    compilator_type == "c" \
		     or compilator_type == "C":
			c_version_list = [1989, 1990, 1999, 2011]
			if version not in c_version_list:
				debug.error("can not select C version : " + str(version) + " not in " + str(c_version_list))
			# select API version:
			api_version = 1999
			if same_as_api == True:
				api_version = version
			self.flags["local"]["c-version"] = { "version":version,
			                                     "gnu":gnu
			                                   }
			self.flags["export"]["c-version"] = api_version
			if gnu == True and same_as_api == True:
				debug.warning("Can not propagate the gnu extention of the C vesion for API");
		else:
			debug.warning("Can not set version of compilator:" + str(compilator_type));
	
	def add_src_file(self, list):
		tools.list_append_to(self.src, list, True)
	
	def add_header_file(self, list, destination_path=None):
		if destination_path != None:
			debug.verbose("Change destination PATH: '" + str(destination_path) + "'")
		new_list = []
		for elem in list:
			if destination_path != None:
				base = os.path.basename(elem)
				if '*' in base or '[' in base or '(' in base:
					new_list.append({"src":elem,
					                 "multi-dst":destination_path})
				else:
					new_list.append({"src":elem,
					                 "dst":os.path.join(destination_path, base)})
			else:
				new_list.append({"src":elem,
				                 "dst":elem})
		tools.list_append_to(self.header, new_list, True)
	
	def add_export_path(self, list, type='c'):
		tools.list_append_to_2(self.path["export"], type, list)
	
	def copy_image(self, source, destination='', sizeX=-1, sizeY=-1):
		self.image_to_copy.append([source, destination, sizeX, sizeY])
	
	def copy_file(self, source, destination=''):
		self.files.append([source, destination])
	
	def copy_path(self, source, destination=''):
		self.paths.append([source, destination])
	
	def print_list(self, description, input_list):
		if type(input_list) == list:
			if len(input_list) > 0:
				print('        ' + str(description))
				for elem in input_list:
					print('            ' + str(elem))
		else:
			print('        ' + str(description))
			print('            ' + str(input_list))
	
	def display(self, target):
		print('-----------------------------------------------')
		print(' package : "' + self.name + "'")
		print('-----------------------------------------------')
		print('    type:"' + str(self.type) + "'")
		print('    file:"' + str(self.origin_file) + "'")
		print('    path:"' + str(self.origin_path) + "'")
		
		self.print_list('depends',self.depends)
		self.print_list('depends_optionnal', self.depends_optionnal)
		
		for element in self.flags["local"]:
			value = self.flags["local"][element]
			self.print_list('flags "' + str(element) + '"', value)
		
		for element in self.flags["export"]:
			value = self.flags["export"][element]
			self.print_list('flags export "' + str(element) + '"', value)
		
		self.print_list('src',self.src)
		self.print_list('files',self.files)
		self.print_list('paths',self.paths)
		for element in self.path["local"]:
			value = self.path["local"][element]
			self.print_list('local path ' + str(element), value)
		
		for element in self.path["export"]:
			value = self.path["export"][element]
			self.print_list('export path ' + str(element), value)
		
	
	def pkg_set(self, variable, value):
		if "COMPAGNY_TYPE" == variable:
			#	com : Commercial
			#	net : Network??
			#	org : Organisation
			#	gov : Governement
			#	mil : Military
			#	edu : Education
			#	pri : Private
			#	museum : ...
			if value not in ["", "com", "net", "org", "gov", "mil", "edu", "pri", "museum"]:
				debug.error("can not set the value for this Input : '" + variable + "' : '" + value + "'")
			else:
				self.package_prop[variable] = value
				self.package_prop_default[variable] = False
		elif "COMPAGNY_NAME" == variable:
			self.package_prop[variable] = value
			self.package_prop_default[variable] = False
			val2 = value.lower()
			val2 = val2.replace(' ', '')
			val2 = val2.replace('-', '')
			val2 = val2.replace('_', '')
			self.package_prop["COMPAGNY_NAME2"] = val2
			self.package_prop_default["COMPAGNY_NAME2"] = False
		elif "ICON" == variable:
			self.package_prop[variable] = value
			self.package_prop_default[variable] = False
		elif "MAINTAINER" == variable:
			self.package_prop[variable] = value
			self.package_prop_default[variable] = False
		elif "SECTION" == variable:
			# project section : (must be separate by coma
			#    refer to : http://packages.debian.org/sid/
			#        admin cli-mono comm database debian-installer
			#        debug doc editors electronics devel embedded
			#        fonts games gnome gnu-r gnustep graphics
			#        hamradio haskell httpd interpreters java
			#        kde kernel libdevel libs lisp localization
			#        mail math misc net news ocaml oldlibs otherosfs
			#        perl php python ruby science shells sound tex
			#        text utils vcs video virtual web x11 xfce zope ...
			self.package_prop[variable] = value
			self.package_prop_default[variable] = False
		elif "PRIORITY" == variable:
			#list = ["required","important","standard","optional","extra"]
			#if isinstance(value, list):
			if value not in ["required", "important", "standard", "optional", "extra"]:
				debug.error("can not set the value for this Input : '" + variable + "' : '" + value + "'")
			else:
				self.package_prop[variable] = value
				self.package_prop_default[variable] = False
		elif variable in ["DESCRIPTION",
		                  "VERSION",
		                  "VERSION_CODE",
		                  "NAME",
		                  "ANDROID_MANIFEST",
		                  "ANDROID_JAVA_FILES",
		                  "RIGHT",
		                  "ANDROID_RESOURCES",
		                  "ANDROID_APPL_TYPE",
		                  "ADMOD_ID",
		                  "APPLE_APPLICATION_IOS_ID",
		                  "LICENSE"]:
			self.package_prop[variable] = value
			self.package_prop_default[variable] = False
		elif "ADMOD_POSITION" == variable:
			if value in ["top", "bottom"]:
				self.package_prop[variable] = value
				self.package_prop_default[variable] = False
			else:
				debug.error("not know pkg element : '" + variable + "' with value : '" + value + "' must be [top|bottom]")
		else:
			debug.error("not know pkg element : '" + variable + "'")
	
	def pkg_set_if_default(self, variable, value):
		if self.package_prop_default[variable] == True:
			self.pkg_set(variable, value)
	
	def pkg_add(self, variable, value):
		if variable in self.package_prop:
			self.package_prop[variable].append(value)
		else:
			self.package_prop[variable] = [value]
	
	def ext_project_add_module(self, target, projectMng, added_module = []):
		if self.name in added_module:
			return
		added_module.append(self.name)
		debug.verbose("add a module to the project generator :" + self.name)
		debug.verbose("local path :" + self.origin_path)
		projectMng.add_files(self.name, self.origin_path, self.src)
		#projectMng.add_data_file(self.origin_path, self.files)
		#projectMng.add_data_path(self.origin_path, self.paths)
		"""
		for depend in self.depends:
			target.project_add_module(depend, projectMng, added_module)
		"""
	
	def create_project(self, target, projectMng):
		projectMng.set_project_name(self.name)
		self.ext_project_add_module(target, projectMng)
		projectMng.generate_project_file()



module_list=[]
__start_module_name="lutin_"

def import_path(path):
	global module_list
	matches = []
	debug.debug('MODULE: Start find sub File : "%s"' %path)
	for root, dirnames, filenames in os.walk(path):
		tmpList = fnmatch.filter(filenames, __start_module_name + "*.py")
		# Import the module :
		for filename in tmpList:
			debug.debug('Module:     Find a file : "%s"' %os.path.join(root, filename))
			#matches.append(os.path.join(root, filename))
			sys.path.append(os.path.dirname(os.path.join(root, filename)) )
			module_name = filename.replace('.py', '')
			module_name = module_name.replace(__start_module_name, '')
			debug.debug("MODULE:     Integrate module: '" + module_name + "' from '" + os.path.join(root, filename) + "'")
			module_list.append([module_name, os.path.join(root, filename)])
	debug.verbose("New list module: ")
	for mod in module_list:
		debug.verbose("    " + str(mod[0]))

def exist(target, name):
	global module_list
	for mod in module_list:
		if mod[0] == name:
			return True
	return False

def load_module(target, name):
	global module_list
	for mod in module_list:
		if mod[0] == name:
			sys.path.append(os.path.dirname(mod[1]))
			debug.verbose("import module : '" + __start_module_name + name + "'")
			the_module_file = mod[1]
			the_module = __import__(__start_module_name + name)
			# get basic module properties:
			property = get_module_option(the_module, name)
			# configure the module:
			if "create" in dir(the_module):
				tmp_element = the_module.create(target, name)
				if tmp_element != None:
					# overwrite some package default property (if not set by user)
					if property["compagny-type"] != None:
						tmp_element.pkg_set_if_default("COMPAGNY_TYPE", property["compagny-type"])
					if property["compagny-name"] != None:
						tmp_element.pkg_set_if_default("COMPAGNY_NAME", property["compagny-name"])
					if property["maintainer"] != None:
						tmp_element.pkg_set_if_default("MAINTAINER", property["maintainer"])
					if property["name"] != None:
						tmp_element.pkg_set_if_default("NAME", property["name"])
					if property["description"] != None:
						tmp_element.pkg_set_if_default("DESCRIPTION", property["description"])
					if property["license"] != None:
						tmp_element.pkg_set_if_default("LICENSE", property["license"])
					if property["version"] != None:
						tmp_element.pkg_set_if_default("VERSION", property["version"])
			else:
				debug.warning(" no function 'create' in the module : " + mod[0] + " from:'" + mod[1] + "'")
				continue
			"""
			if property["type"] == "":
				continue
			# configure the module:
			if "configure" in dir(the_module):
				tmp_element = module.Module(the_module_file, name, property["type"], property)
				ret = the_module.configure(target, tmp_element)
				if ret == True:
					debug.warning("configure done corectly : " + mod[0] + " from:'" + mod[1] + "'")
				else:
					debug.warning("configure NOT done corectly : " + mod[0] + " from:'" + mod[1] + "'")
			else:
				debug.warning(" no function 'configure' in the module : " + mod[0] + " from:'" + mod[1] + "'")
				continue
			"""
			# check if create has been done corectly
			if tmp_element == None:
				debug.debug("Request load module '" + name + "' not define for this platform")
			else:
				target.add_module(tmp_element)

def list_all_module():
	global module_list
	tmpListName = []
	for mod in module_list:
		tmpListName.append(mod[0])
	return tmpListName

def list_all_module_with_desc():
	global module_list
	tmpList = []
	for mod in module_list:
		sys.path.append(os.path.dirname(mod[1]))
		the_module = __import__("lutin_" + mod[0])
		tmpList.append(get_module_option(the_module, mod[0]))
	return tmpList


def get_module_option(the_module, name):
	type = None
	sub_type = None
	description = None
	license = None
	compagny_type = None
	compagny_name = None
	maintainer = None
	version = None
	
	if "get_type" in dir(the_module):
		type = the_module.get_type()
	else:
		debug.debug(" function get_type() must be provided in the module: " + name)
	
	if "get_sub_type" in dir(the_module):
		sub_type = the_module.get_sub_type()
	
	if "get_desc" in dir(the_module):
		description = the_module.get_desc()
	
	if "get_licence" in dir(the_module):
		license = the_module.get_licence()
	
	if "get_compagny_type" in dir(the_module):
		compagny_type = the_module.get_compagny_type()
		#	com : Commercial
		#	net : Network??
		#	org : Organisation
		#	gov : Governement
		#	mil : Military
		#	edu : Education
		#	pri : Private
		#	museum : ...
		compagny_type_list = ["", "com", "net", "org", "gov", "mil", "edu", "pri", "museum"]
		if compagny_type not in compagny_type_list:
			debug.warning("[" + name + "] type of the company not normal: " + compagny_type + " not in " + str(compagny_type_list))
	
	if "get_compagny_name" in dir(the_module):
		compagny_name = the_module.get_compagny_name()
	
	if "get_maintainer" in dir(the_module):
		maintainer = the_module.get_maintainer()
	
	if "get_version" in dir(the_module):
		version = the_module.get_version()
	
	return {
	       "name":name,
	       "description":description,
	       "type":type,
	       "sub-type":sub_type,
	       "license":license,
	       "compagny-type":compagny_type,
	       "compagny-name":compagny_name,
	       "maintainer":maintainer,
	       "version":version
	       }


